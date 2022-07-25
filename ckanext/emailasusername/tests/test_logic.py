"""Tests for logic.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
import ckan.tests.helpers
import pytest
import mock
import ckan.plugins.toolkit as toolkit
from ckan.tests.helpers import call_action
import ckanext.emailasusername.logic as logic


@pytest.fixture
def sysadmin_context():
    sysadmin = ckan.tests.factories.Sysadmin()
    # helpers.call_action sets 'ignore_auth' to True by default
    context = {'user': sysadmin['name'], 'ignore_auth': False}
    return context


@pytest.fixture
def identity():
    identity = {'name': 'login', 'email': 'test@ckan.org', 'password': 'password'}
    return identity


@pytest.mark.usefixtures('clean_db', 'with_plugins')
class TestSearchUsersByEmail(object):

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'false')
    def test_search_by_email_without_config(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'])
        assert not response

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_full_email(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'])
        assert len(response) == 1

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_full_email_case_insensitive(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'].upper())
        assert len(response) == 1

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_partial_email_sysadmin(self, sysadmin_context, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', sysadmin_context, q='test@ckan')
        assert len(response) == 1

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_partial_email_sysadmin_case_insensitive(self, sysadmin_context, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', sysadmin_context, q='test@ckan'.upper())
        assert len(response) == 1

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_nonexisting_email_sysadmin(self, sysadmin_context, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', sysadmin_context, q='tast@ckan.org')
        assert not response

    @pytest.mark.ckan_config('ckanext.emailasusername.search_by_username_and_email', 'True')
    def test_search_by_partial_email(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'][:-1])
        assert not response


@pytest.mark.usefixtures('clean_db', 'with_plugins')
@pytest.mark.ckan_config(
    'ckanext.emailasusername.auto_generate_username_from_email',
    'true'
)
class TestUsernameCreate():

    def test_without_name_or_email(self):
        expected_error_message = "Must specify either a name or an email"
        with pytest.raises(toolkit.ValidationError, match=expected_error_message):
            call_action(
                'user_create',
                {},
                id='test-id',
                password='test-password'
            )

    @pytest.mark.parametrize('email, expected_username', [
        ('test.user@unaids.org', 'test-user-2222'),
        ('test123@who.int', 'test123-2222'),
        ('faulty_email_address', 'faulty_email_address-2222'),
        ('faulty-address@fault@address.org', 'faulty-address-2222')
    ])
    @mock.patch(
        'ckanext.emailasusername.logic.random.SystemRandom.random',
        return_value=0.2222
    )
    def test_username_generation(self, random_patch, email, expected_username):
        result = logic._get_random_username_from_email(email, ckan.model)
        assert result == expected_username

    @mock.patch(
        'ckanext.emailasusername.logic.random.SystemRandom.random',
        return_value=0.2222
    )
    def test_simple_email(self, random_patch):
        result = call_action(
            'user_create',
            {},
            id='test-id',
            email='testuser@avenirhealth.com',
            password='test-password'
        )
        assert result['name'] == 'testuser-2222'

    def test_invalid_email(self):
        with pytest.raises(toolkit.ValidationError) as error_raised:
            call_action(
                'user_create',
                {},
                id='test-id',
                email='testuser.org',
                password='test-password'
            )
        # Check that a name error hasn't also been thrown for an email error
        assert 'name' not in error_raised.value.error_dict.keys()
