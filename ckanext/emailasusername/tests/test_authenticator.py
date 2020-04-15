"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
from ckan.tests import helpers
import ckanext.emailasusername.authenticator as authenticator
import logging
import unittest
import mock

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ModuleTests(unittest.TestCase):

    @classmethod
    def setup_class(self):
        log.warning("Setting up class")
        ckan.plugins.load('emailasusername')

    @classmethod
    def teardown_class(self):
        log.warning("Tearing down class")
        ckan.plugins.unload('emailasusername')
        helpers.reset_db()

    def teardown(self):
        log.warning("Tearing down function")
        helpers.reset_db()

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
        self.assertEquals(response, 'tester')

        # Test that a correct email based login returns the username
        identity['login'] = 'test@ckan.org'
        response = auth.authenticate({}, identity)
        self.assertEquals(response, 'tester')

        # Test that an incorrect email based login fails login
        identity['login'] = 'test@ckan-wrong.org'
        response = auth.authenticate({}, identity)
        self.assertEquals(response, None)
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
        self.assertEquals(response, None)
        flash_mock.assert_not_called()

        # Test that an incorrect password fails login
        identity['password'] += '!'
        response = auth.authenticate({}, identity)
        self.assertEquals(response, None)
        flash_mock.assert_not_called()
