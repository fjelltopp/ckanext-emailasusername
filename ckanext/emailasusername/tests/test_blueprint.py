"""Tests for plugin.py."""
import ckan.plugins
import ckan.model
import ckan.logic.schema
import ckan.tests.factories
import six
from ckan.lib.helpers import url_for
from ckan.tests import helpers
import ckanext.emailasusername.blueprint as blueprint
import logging
import unittest
import mock
from ckan.tests.helpers import submit_and_follow
import ckan.plugins as plugins

log = logging.getLogger(__name__)


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
        ckan.tests.factories.User(name=username, email=email)

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


def _assert_in_body(string, response):
    if six.PY2:
        assert string in response.body.decode('utf8')
    else:
        assert string in response.body


def _assert_login_page_displayed(response):
    login_form = response.forms[1]
    for input in ['login', 'password', 'remember']:
        assert input in login_form.fields


def _assert_request_reset_page_displayed(response):
    reset_form = response.forms[1]
    assert reset_form.action == url_for('emailasusername.request_reset')


class TestRequestResetFunctional(helpers.FunctionalTestBase):
    def setup(self):
        helpers.reset_db()
        self.app = helpers._get_test_app()
        if not plugins.plugin_loaded(u'emailasusername'):
            plugins.load(u'emailasusername')
            plugin = plugins.get_plugin(u'emailasusername')
            self.app.flask_app.register_extension_blueprint(plugin.get_blueprint())

    def teardown(self):
        ckan.plugins.unload('emailasusername')

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_sends_reset_link_for_correct_username(self, mailer_mock):
        # given:
        user = ckan.tests.factories.User()
        # when:
        password_reset_form = self.app.get(url_for('user.request_reset')).forms[1]
        password_reset_form['user'] = user['name']
        test_response = submit_and_follow(self.app, password_reset_form, name='reset')

        # then:
        assert mailer_mock.called
        called_user = mailer_mock.call_args[0][0]
        assert called_user.id == user['id']
        _assert_in_body("Please check your inbox for a reset code.", test_response)
        _assert_login_page_displayed(test_response)

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_sends_reset_link_for_correct_email(self, mailer_mock):
        # given:
        user = ckan.tests.factories.User()
        # when:
        password_reset_form = self.app.get(url_for('user.request_reset')).forms[1]
        password_reset_form['user'] = user['email']
        test_response = submit_and_follow(self.app, password_reset_form, name='reset')

        # then:
        assert mailer_mock.called
        called_user = mailer_mock.call_args[0][0]
        assert called_user.id == user['id']
        _assert_in_body("Please check your inbox for a reset code.", test_response)
        _assert_login_page_displayed(test_response)

    @mock.patch('ckanext.emailasusername.blueprint.mailer.send_reset_link')
    def test_request_reset_display_error_for_incorrect_email(self, mailer_mock):
        # given:
        fake_email = 'fake@mail.com'
        # when:
        password_reset_form = self.app.get(url_for('user.request_reset')).forms[1]
        password_reset_form['user'] = fake_email
        test_response = submit_and_follow(self.app, password_reset_form, name='reset')

        # then:
        assert not mailer_mock.called
        _assert_in_body("No such user: {}".format(fake_email), test_response)
        _assert_request_reset_page_displayed(test_response)

    def test_request_reset_display_error_on_smtp_problem(self):
        # given:
        user = ckan.tests.factories.User()
        # when:
        r = self.app.get(url_for('user.request_reset'))
        password_reset_form = r.forms[1]
        password_reset_form['user'] = user['name']
        test_response = submit_and_follow(self.app, password_reset_form, name='reset')
        # then:
        _assert_in_body("Could not send reset link:", test_response)
        _assert_request_reset_page_displayed(test_response)
