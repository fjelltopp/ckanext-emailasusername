"""Tests for plugin.py."""
import ckan.plugins
import ckan.logic.schema
import ckan.tests.factories
import ckanext.emailasusername.authenticator as authenticator
import pytest
import mock
from ckan.logic import ValidationError


@pytest.mark.usefixtures('clean_db', 'with_plugins')
@pytest.mark.usefixtures('mail_server')
class TestAuthenticator(object):

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_authenticate(self, flash_mock):
        auth = authenticator.EmailAsUsernameAuthenticator()
        response = auth.authenticate({}, {})
        assert response is None
        identity = {'login': 'tester', 'password': 'RandomPassword123'}
        ckan.tests.factories.User(
            name=identity['login'],
            email='test@ckan.org',
            password=identity['password']
        )

        # Test that a correct login returns the username
        response = auth.authenticate({}, identity)
        assert response == 'tester'

        # Test that a correct email based login returns the username
        identity['login'] = 'test@ckan.org'
        response = auth.authenticate({}, identity)
        assert response == 'tester'

        # Test that an incorrect email based login fails login
        identity['login'] = 'test@ckan-wrong.org'
        response = auth.authenticate({}, identity)
        assert response is None
        flash_mock.assert_not_called()

        # Test that login fails when two accounts registered with email exists
        identity = {'login': 'tester2', 'password': 'RandomPassword123'}
        email = 'test@ckan.org'
        try:
            ckan.tests.factories.User(
                name=identity['login'],
                email=email,
                password=identity['password']
            )
            identity['login'] = email
            response = auth.authenticate({}, identity)
            assert response is None
            flash_mock.assert_not_called()
        except ValidationError as e:
            # CKAN 2.9 does not allow users to have identical emails
            assert e.error_summary['Email'] == 'The email address \'{}\' belongs to a registered user.'.format(email)

        # Test that an incorrect password fails login
        identity['password'] += '!'
        response = auth.authenticate({}, identity)
        assert response is None
        flash_mock.assert_not_called()
