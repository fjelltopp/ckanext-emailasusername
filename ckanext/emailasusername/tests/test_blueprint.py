"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
from ckan.logic import ValidationError
import ckan.tests.factories
from ckan.lib.helpers import url_for
import ckanext.emailasusername.blueprint as blueprint
from ckan.lib.mailer import MailerException
import logging
import pytest
import mock

log = logging.getLogger(__name__)


@pytest.mark.usefixtures('clean_db', 'with_plugins')
@pytest.mark.usefixtures('mail_server')
class TestGetUser(object):

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_user_by_username_or_email_create_user(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        ckan.tests.factories.User(name=username, email=email)

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_user_by_username(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        ckan.tests.factories.User(name=username, email=email)
        # Test getting user by username
        user_obj = blueprint.user_by_username_or_email(username)
        assert getattr(user_obj, 'name') == username
        assert getattr(user_obj, 'email') == email

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_user_by_email(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        ckan.tests.factories.User(name=username, email=email)
        # Test getting user by email
        user_obj = blueprint.user_by_username_or_email(email)
        assert getattr(user_obj, 'name') == username
        assert getattr(user_obj, 'email') == email

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_user_by_wrong_username(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        ckan.tests.factories.User(name=username, email=email)
        # Test trying to get a nonexistant user
        user_obj = blueprint.user_by_username_or_email('wrongname')
        flash_mock.assert_called()
        assert user_obj is None

    @mock.patch('ckanext.emailasusername.blueprint.h.flash_error')
    def test_user_by_username_or_email_duplicate_email(self, flash_mock):
        username = 'tester1'
        email = 'test1@ckan.org'
        ckan.tests.factories.User(name=username, email=email)
        # Test trying to get by email when multiple accounts have same email
        with pytest.raises(ValidationError):
            ckan.tests.factories.User(name='tester2', email=email)


def _assert_in_body(string, response):
    assert string in response.body


def _assert_login_page_displayed(response):
    login_form = response.forms[1]
    for input in ['login', 'password', 'remember']:
        assert input in login_form.fields


# def _assert_request_reset_page_displayed(response):
#     reset_form = response.forms[1]
#     assert reset_form.action == url_for('emailasusername.request_reset')

@pytest.mark.usefixtures('clean_db', 'with_plugins')
@pytest.mark.usefixtures('mail_server')
class TestRequestResetFunctional(object):

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_sends_reset_link_for_correct_username(self, mailer_mock, app):
        # given:
        user = ckan.tests.factories.User()

        # when:
        offset = url_for("user.request_reset")
        test_response = app.post(
            offset, data=dict(user=user["name"])
        )

        # then:
        assert mailer_mock.called
        called_user = mailer_mock.call_args[0][0]
        assert called_user.id == user['id']
        _assert_in_body("A reset link has been emailed to you", test_response)

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_sends_reset_link_for_correct_email(self, mailer_mock, app):
        # given:
        user = ckan.tests.factories.User()

        # when:
        offset = url_for("user.request_reset")
        test_response = app.post(
            offset, data=dict(user=user["email"])
        )

        # then:
        assert mailer_mock.called
        called_user = mailer_mock.call_args[0][0]
        assert called_user.id == user['id']
        _assert_in_body("A reset link has been emailed to you", test_response)

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_display_error_for_incorrect_email(self, mailer_mock, app):
        # given:
        fake_email = 'fake@mail.com'

        # when:
        offset = url_for("user.request_reset")
        test_response = app.post(
            offset, data=dict(user=fake_email)
        )

        # then:
        assert not mailer_mock.called
        _assert_in_body("A reset link has been emailed to you", test_response)

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_display_error_on_smtp_problem(self, send_reset_link, app):
        # given:
        user = ckan.tests.factories.User()

        # when:
        offset = url_for("user.request_reset")
        # This is the exception when the mailer is not configured:
        send_reset_link.side_effect = MailerException(
            'SMTP server could not be connected to: "localhost" '
            "[Errno 111] Connection refused"
        )
        test_response = app.post(
            offset, data=dict(user=user["name"])
        )

        # then:
        _assert_in_body("Error sending the email. Try again later or contact an administrator for help", test_response)
