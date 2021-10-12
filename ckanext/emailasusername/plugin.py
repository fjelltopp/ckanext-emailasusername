# encoding: utf-8
import logging
from six import text_type
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic.schema as schema
from ckan.lib.plugins import DefaultTranslation
from ckan.model import User
from ckan.common import _
from ckanext.emailasusername.blueprint import emailasusername
from ckanext.emailasusername.logic import user_autocomplete
from ckanext.emailasusername.helpers import (
    config_auto_generate_username_from_fullname,
    config_require_user_email_input_confirmation
)

log = logging.getLogger(__name__)


class EmailasusernamePlugin(plugins.SingletonPlugin, DefaultTranslation):

    plugins.implements(plugins.interfaces.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.interfaces.IValidators)
    plugins.implements(plugins.interfaces.IBlueprint)
    plugins.implements(plugins.interfaces.ITranslation)
    plugins.implements(plugins.interfaces.IActions)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'emailasusername')
        schema.user_new_form_schema = emailasusername_new_user_schema

    def get_validators(self):
        return {
            'email_exists': email_exists,
            'user_both_emails_entered': user_both_emails_entered,
            'user_emails_match': user_emails_match
        }

    def get_actions(self):
        actions = {}
        if toolkit.config.get("emailasusername.search_by_username_and_email"):
            actions['user_autocomplete'] = user_autocomplete
        return actions

    def get_blueprint(self):
        return emailasusername

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'config_auto_generate_username_from_fullname': config_auto_generate_username_from_fullname,
            'config_require_user_email_input_confirmation': config_require_user_email_input_confirmation
        }


@schema.validator_args
def emailasusername_new_user_schema(
        unicode_safe, user_both_passwords_entered,
        user_password_validator, user_passwords_match, email_exists,
        not_empty, email_validator):
    emailasusername_schema = schema.default_user_schema()
    emailasusername_schema['fullname'] = [
        not_empty, unicode_safe
    ]
    emailasusername_schema['password1'] = [
        text_type, user_both_passwords_entered,
        user_password_validator, user_passwords_match
    ]
    emailasusername_schema['password2'] = [
        text_type
    ]
    emailasusername_schema['email'] = [unicode_safe, email_validator]
    emailasusername_schema['email1'] = [
        not_empty, unicode_safe, email_validator, email_exists
    ]
    if config_require_user_email_input_confirmation():
        emailasusername_schema['email1'] += [
            user_emails_match, user_both_emails_entered
        ]
        emailasusername_schema['email2'] = [not_empty]
    return emailasusername_schema


def email_exists(key, data, errors, context):
    result = User.by_email(data[key])
    if result:
        errors[('email',)] = errors.get(key, [])
        errors[('email',)] = [
            _('An account is already registered to that email.')
        ]


def user_both_emails_entered(key, data, errors, context):
    email1 = data.get(('email1',), None)
    email2 = data.get(('email2',), None)
    if email1 is None or email1 == '' or \
       email2 is None or email2 == '':
        errors[('email',)].append(
            _('Please enter your email in both email fields')
        )


def user_emails_match(key, data, errors, context):
    email1 = data.get(('email1',), None)
    email2 = data.get(('email2',), None)
    if not email1 == email2:
        errors[('email',)].append(
            _('You did not retype your email correctly')
        )
    else:
        data[('email',)] = email1
