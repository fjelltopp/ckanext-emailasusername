"""Tests for plugin.py."""
from ckan.plugins import toolkit
import ckan.model
import ckan.logic.schema
from ckan.tests.factories import User
import ckan.tests.helpers
from ckan.lib.helpers import url_for
import ckanext.emailasusername.plugin as plugin
from ckanext.emailasusername.helpers import (
    config_require_user_email_input_confirmation
)
from contextlib import nullcontext as does_not_raise
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

    @pytest.mark.parametrize("existing_user, data, result", [
        (
            None,
            {('email',): 'test@ckan.org'},
            does_not_raise()
        ), (
            {'email': 'test@ckan.org'},
            {('email',): 'test@ckan.org'},
            pytest.raises(toolkit.Invalid)
        ), (
            {'email': 'test@ckan.org', 'state': 'deleted'},
            {('email',): 'test@ckan.org'},
            does_not_raise()
        ), (
            {'email': 'test@ckan.org', 'state': 'deleted', 'name': 'tester1'},
            {('email',): 'test@ckan.org', 'state': 'active', ('name',): 'tester1'},
            does_not_raise()
        ), (
            {'email': 'test@ckan.org', 'name': 'tester1'},
            {('email',): 'test@ckan.org', ('name',): 'tester1'},
            does_not_raise()
        ), (
            {'email': 'test@ckan.org', 'name': 'tester1'},
            {('email',): 'test@ckan.org', ('name',): 'tester2'},
            pytest.raises(toolkit.Invalid)
        )
    ], ids=[
        "creating user with a unique email address",
        "creating user with an existing email address",
        "creating user with an email address used by deleted user",
        "updating user state to active",
        "updating user without changing the email address",
        "updating user with an existing email address"
    ])
    def test_email_is_unique(self, existing_user, data, result):

        if existing_user:
            User(**existing_user)

        with result:
            plugin.email_is_unique(('email',), data, {('email',): []}, {})

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
