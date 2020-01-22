"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
from ckan.tests import helpers
import ckanext.emailasusername.blueprint as blueprint
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
    def test_user_by_username_or_email(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        log.warning(ckan.tests.factories.User(name=username, email=email))

        # Test getting user by username
        user_obj = blueprint.user_by_username_or_email(username)
        self.assertEquals(getattr(user_obj, 'name'), username)
        self.assertEquals(getattr(user_obj, 'email'), email)

        # Test getting user by email
        user_obj = blueprint.user_by_username_or_email(email)
        self.assertEquals(getattr(user_obj, 'name'), username)
        self.assertEquals(getattr(user_obj, 'email'), email)

        # Test trying to get a nonexistant user
        user_obj = blueprint.user_by_username_or_email('wrongname')
        flash_mock.assert_called()
        self.assertEquals(user_obj, None)

        # Test trying to get by email when multiple accounts have same email
        ckan.tests.factories.User(name='tester2', email=email)
        user_obj = blueprint.user_by_username_or_email(email)
        flash_mock.assert_called()
        self.assertEquals(user_obj, None)

    def test_request_reset(self):
        # Todo: Test request_reset
        assert True
