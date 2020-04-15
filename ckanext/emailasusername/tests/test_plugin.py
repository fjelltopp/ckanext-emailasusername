"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
from ckan.tests import helpers
import ckanext.emailasusername.plugin as plugin
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
        assert False

    def test_user_emails_match(self):
        key = ('email',)
        data = {
            ('email1',): 'test@test.com',
            ('email2',): 'test@test.com',
            ('email',): ''
        }
        errors = {('email',): []}
        context = {}

        # Test that function works for matching emails
        plugin.user_emails_match(key, data, errors, context)
        self.assertEquals(errors, {('email',): []})
        self.assertEquals(data[('email', )], data[('email1',)])

        # Test that the function works for non-matching emails
        data[('email2',)] = 'tes@test.com'
        errors = {('email',): []}
        plugin.user_emails_match(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) > 0)

    def test_user_both_emails_entered(self):
        key = ('email',)
        data = {
            ('email1',): 'test@test.com',
            ('email2',): 'test@test.com',
            ('email',): ''
        }
        errors = {('email',): []}
        context = {}

        # Test that the function works for correct input
        plugin.user_both_emails_entered(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) == 0)

        # Test that the function works for missing input
        data[('email1',)] = ''
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) == 1)

        data[('email1',)] = None
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        log.warning(errors)
        self.assertTrue(len(errors[('email',)]) == 1)

        data[('email2',)] = 'test@test.com'
        data[('email2',)] = ''
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) == 1)

        data[('email2',)] = None
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) == 1)

    def test_email_exists(self):
        # Test email exists validator for valid data
        key = ('email',)
        data = {('email',): 'test@ckan.org'}
        errors = {('email',): []}
        context = {}
        plugin.email_exists(key, data, errors, context)
        self.assertEquals(errors, {('email',): []})

        # Test email exists validator for invalid data
        # i.e. a pre-existing account already exists with the given email
        test_user_dict = ckan.tests.factories.User(
            name='tester1',
            email='test@ckan.org'
        )
        data = {('email',): test_user_dict['email']}
        plugin.email_exists(key, data, errors, context)
        self.assertTrue(len(errors[('email',)]) == 1)

    def test_emailasusername_new_user_schema(self):

        schema = ckan.logic.schema.user_new_form_schema()
        self.assertIn('email', schema)
        self.assertIn('email1', schema)
        self.assertIn('email2', schema)
        self.assertIn('password1', schema)
        self.assertIn('password2', schema)

        def get_validator_names(validator_list):
            return list(map(lambda f: f.__name__, validator_list))

        email1_validators = get_validator_names(schema['email1'])
        self.assertIn('user_emails_match', email1_validators)
        self.assertIn('user_both_emails_entered', email1_validators)

        email_validators = get_validator_names(schema['email'])
        self.assertNotIn('not_empty', email_validators)

        default_schema = ckan.logic.schema.default_user_schema()
        del default_schema['email']

        # Check that all the other default schema fields remain untouched
        for key, value in default_schema.items():
            self.assertIn(
                key, schema,
                "Key from default user schema not found: {}".format(key)
            )
            self.assertEquals(
                value, schema[key],
                "Value from default user schema changed: {} | {} | {}".format(
                    key, value, schema[key]
                )
            )
