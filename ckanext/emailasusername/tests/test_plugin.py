"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
import ckan.tests.helpers
from ckan.lib.helpers import url_for
import ckanext.emailasusername.plugin as plugin
from ckanext.emailasusername.helpers import (
    config_require_user_email_input_confirmation
)
import logging
import pytest

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_validator_names(validator_list):
    return list(map(lambda f: f.__name__, validator_list))


@pytest.mark.usefixtures('clean_db', 'with_plugins')
class TestEmails(object):

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
        assert errors == {('email',): []}
        assert data[('email', )] == data[('email1',)]

        # Test that the function works for non-matching emails
        data[('email2',)] = 'tes@test.com'
        errors = {('email',): []}
        plugin.user_emails_match(key, data, errors, context)
        assert len(errors[('email',)]) > 0

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
        assert len(errors[('email',)]) == 0

        # Test that the function works for missing input
        data[('email1',)] = ''
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        assert len(errors[('email',)]) == 1

        data[('email1',)] = None
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        log.warning(errors)
        assert len(errors[('email',)]) == 1

        data[('email2',)] = 'test@test.com'
        data[('email2',)] = ''
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        assert len(errors[('email',)]) == 1

        data[('email2',)] = None
        errors = {('email',): []}
        plugin.user_both_emails_entered(key, data, errors, context)
        assert len(errors[('email',)]) == 1

    def test_email_exists(self):
        # Test email exists validator for valid data
        key = ('email',)
        data = {('email',): 'test@ckan.org'}
        errors = {('email',): []}
        context = {}
        plugin.email_exists(key, data, errors, context)
        assert errors, {('email',): []}

        # Test email exists validator for invalid data
        # i.e. a pre-existing account already exists with the given email
        test_user_dict = ckan.tests.factories.User(
            name='tester1',
            email='test@ckan.org'
        )
        data = {('email',): test_user_dict['email']}
        plugin.email_exists(key, data, errors, context)
        assert len(errors[('email',)]) == 1

    def test_emailasusername_new_user_schema(self):
        schema = ckan.logic.schema.user_new_form_schema()
        assert 'fullname' in schema
        assert 'email' in schema
        assert 'email1' in schema
        assert 'email2' in schema
        assert 'password1' in schema
        assert 'password2' in schema

        email1_validators = get_validator_names(schema['email1'])
        assert 'user_emails_match' in email1_validators
        assert 'user_both_emails_entered' in email1_validators

        email_validators = get_validator_names(schema['email'])
        assert 'not_empty' not in email_validators

        default_schema = ckan.logic.schema.default_user_schema()
        del default_schema['fullname']
        del default_schema['email']

        # Check that all the other default schema fields remain untouched
        for key, value in default_schema.items():
            assert key in schema
            assert (value in schema[key] or value == schema[key])

    def test_default_config_email_input_confirmation_value(self):
        assert config_require_user_email_input_confirmation()

    @pytest.mark.ckan_config('ckanext.emailasusername.require_user_email_input_confirmation', False)
    def test_config_email_input_confirmation_value_when_false(self):
        assert not config_require_user_email_input_confirmation()

    def test_user_registration_form_defaults_to_requiring_email_confirmation(self, app):
        response = app.get(url_for('user.register'))
        assert 'email2' in response.body

    @pytest.mark.ckan_config('ckanext.emailasusername.require_user_email_input_confirmation', False)
    def test_user_registration_form_not_requiring_email_confirmation(self, app):
        response = app.get(url_for('user.register'))
        assert 'email2' not in response.body

    @pytest.mark.ckan_config('ckanext.emailasusername.require_user_email_input_confirmation', False)
    def test_emailasusername_new_user_schema_when_email_confirmation_is_not_required(self):
        schema = ckan.logic.schema.user_new_form_schema()
        assert 'email2' not in schema
        email_validators = get_validator_names(schema['email1'])
        assert 'user_emails_match' not in email_validators
        assert 'user_both_emails_entered' not in email_validators
