"""Tests for logic.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
import ckan.tests.helpers
import pytest


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


@pytest.mark.usefixtures(u'clean_db')
@pytest.mark.ckan_config(u'ckan.plugins', u'emailasusername')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
class TestSearchUsersByEmail(object):

    @pytest.mark.ckan_config(u'emailasusername.search_by_username_and_email', u'')
    def test_search_by_email_without_config(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'])
        assert not response

    @pytest.mark.ckan_config(u'emailasusername.search_by_username_and_email', u'True')
    def test_search_by_full_email(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'])
        assert len(response) == 1

    @pytest.mark.ckan_config(u'emailasusername.search_by_username_and_email', u'True')
    def test_search_by_partial_email_sysadmin(self, sysadmin_context, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', sysadmin_context, q='test@ckan')
        assert len(response) == 1

    @pytest.mark.ckan_config(u'emailasusername.search_by_username_and_email', u'True')
    def test_search_by_nonexisting_email_sysadmin(self, sysadmin_context, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', sysadmin_context, q='tast@ckan.org')
        assert not response

    @pytest.mark.ckan_config(u'emailasusername.search_by_username_and_email', u'True')
    def test_search_by_partial_email(self, identity):
        ckan.tests.factories.User(**identity)
        response = ckan.tests.helpers.call_action('user_autocomplete', {}, q=identity['email'][:-1])
        assert not response
