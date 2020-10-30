"""Tests for plugin.py."""
import ckan.plugins
import ckan.model as model
import ckan.logic.schema
import ckan.tests.factories
from ckan.tests import helpers
import ckanext.emailasusername.authenticator as authenticator
import logging
import pytest
import mock

@pytest.fixture
def initdb():
    model.Session.remove()
    model.Session.configure(bind=model.meta.engine)
    model.init_tables()

@pytest.mark.usefixtures(u'initdb')
@pytest.mark.usefixtures(u'clean_db')
@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
@pytest.mark.usefixtures(u'mail_server')
class TestAuthenticator(object):

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_authenticate(self, flash_mock):
        auth = authenticator.EmailAsUsernameAuthenticator()
        response = auth.authenticate({}, {})
        self.assertEquals(response, None)
        identity = {'login': 'tester', 'password': 'RandomPassword123'}
        ckan.tests.factories.User(
            name=identity['login'],
            email='test@ckan.org',
            password=identity['password']
        )

        # Test that a correct login returns the username
        response = auth.authenticate({}, identity)
        assert response == 'tester'
        #self.assertEquals(response, 'tester')

        # Test that a correct email based login returns the username
        identity['login'] = 'test@ckan.org'
        response = auth.authenticate({}, identity)
        assert response == 'tester'
        #self.assertEquals(response, 'tester')

        # Test that an incorrect email based login fails login
        identity['login'] = 'test@ckan-wrong.org'
        response = auth.authenticate({}, identity)
        assert response is None
        #self.assertEquals(response, None)
        flash_mock.assert_not_called()

        # Test that login fails when two accounts registered with email exists
        identity = {'login': 'tester2', 'password': 'RandomPassword123'}
        ckan.tests.factories.User(
            name=identity['login'],
            email='test@ckan.org',
            password=identity['password']
        )
        identity['login'] = 'test@ckan.org'
        response = auth.authenticate({}, identity)
        assert response is None
        #self.assertEquals(response, None)
        flash_mock.assert_not_called()

        # Test that an incorrect password fails login
        identity['password'] += '!'
        response = auth.authenticate({}, identity)
        assert response is None
        #self.assertEquals(response, None)
        flash_mock.assert_not_called()
