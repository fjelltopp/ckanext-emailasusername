"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
from ckan.tests import helpers
import ckanext.emailasusername.authenticator as authenticator
import logging
import unittest

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

    def test_user_by_username_or_email(self):
        username = 'tester1'
        email = 'test1@ckan.org'
        log.warning(ckan.tests.factories.User(name=username, email=email))

        # Test getting user by username
        user_obj = authenticator.user_by_username_or_email(username)
        self.assertEquals(getattr(user_obj, 'name'), username)
        self.assertEquals(getattr(user_obj, 'email'), email)

        # Test getting user by email
        user_obj = authenticator.user_by_username_or_email(email)
        self.assertEquals(getattr(user_obj, 'name'), username)
        self.assertEquals(getattr(user_obj, 'email'), email)

        # Test trying to get a nonexistant user
        user_obj = authenticator.user_by_username_or_email('wrongname')
        self.assertEquals(user_obj, None)

        # Test trying to get by email when multiple accounts have same email
        ckan.tests.factories.User(name='tester2', email=email)
        user_obj = authenticator.user_by_username_or_email(email)
        self.assertEquals(user_obj, None)

    def test_authenticate(self):
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

        # Test that an incorrect password fails login
        identity['password'] += '!'
        response = auth.authenticate({}, identity)
        self.assertEquals(response, None)
