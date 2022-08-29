# encoding: utf-8
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic.schema as schema
from ckan.lib.plugins import DefaultTranslation
import ckan.model as model
from ckan.common import _
from ckanext.emailasusername.blueprint import emailasusername
from ckanext.emailasusername.logic import (
    user_autocomplete,
    user_create
)
import ckanext.emailasusername.helpers as helpers

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
        schema.user_new_form_schema = emailasusername_user_new_form_schema

    def get_validators(self):
        return {
            'email_is_unique': email_is_unique,
            'user_both_emails_entered': user_both_emails_entered,
            'user_emails_match': user_emails_match
        }

    def get_actions(self):
        actions = {}
        if helpers.config_search_by_username_and_email():
            actions['user_autocomplete'] = user_autocomplete
        if helpers.config_auto_generate_username_from_email():
            actions['user_create'] = user_create
        return actions

    def get_blueprint(self):
        return emailasusername

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'config_auto_generate_username_from_fullname':
                helpers.config_auto_generate_username_from_fullname,
            'config_require_user_email_input_confirmation':
                helpers.config_require_user_email_input_confirmation
        }


@schema.validator_args
def emailasusername_user_new_form_schema(
        unicode_safe, unicode_only, user_both_passwords_entered,
        user_password_validator, user_passwords_match, email_is_unique,
        not_empty, email_validator):
    emailasusername_schema = schema.default_user_schema()
    emailasusername_schema['fullname'] = [
        not_empty, unicode_safe
    ]
    emailasusername_schema['password1'] = [
        unicode_only, user_both_passwords_entered,
        user_password_validator, user_passwords_match
    ]
    emailasusername_schema['password2'] = [
        unicode_only
    ]
    emailasusername_schema['email'] = [unicode_safe, email_validator]
    emailasusername_schema['email1'] = [
        not_empty, unicode_safe, email_validator, email_is_unique
    ]
    if helpers.config_require_user_email_input_confirmation():
        emailasusername_schema['email1'] += [
            user_emails_match, user_both_emails_entered
        ]
        emailasusername_schema['email2'] = [not_empty]
    return emailasusername_schema


def email_is_unique(key, data, errors, context):
    if data.get(('state',)) != model.State.DELETED:

        def is_me(user):
            # Core logic taken from ckan.logic.validators.email_is_unique
            return (user.name in (data.get(("name",)), data.get(("id",)))
                    or user.id == data.get(("id",)))

        users_matching_email = model.User.by_email(data[key])
        undeleted_users_matching_email = [
            a for a in users_matching_email if a.state != model.State.DELETED
        ]
        undeleted_users_matching_email_not_including_me = [
            a for a in undeleted_users_matching_email if not is_me(a)
        ]
        if undeleted_users_matching_email_not_including_me:
            raise toolkit.Invalid(
                _('An account is already registered to that email.')
            )


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
