"""Tests for plugin.py."""
import ckan.plugins
import ckan.logic.schema
import ckan.tests.factories
import ckanext.emailasusername.authenticator as authenticator
import pytest
from ckan.logic import ValidationError


@pytest.mark.usefixtures('clean_db', 'with_plugins')
@pytest.mark.usefixtures('mail_server')
class TestAuthenticator(object):

    @pytest.mark.parametrize("identity, existing_user, result", [
        ({}, False, None),
        ({'login': 'tester', 'password': 'RandomPassword123'}, True, 'tester'),
        ({'login': 'test@ckan.org', 'password': 'RandomPassword123'}, True, 'tester'),
        ({'login': 'test@ckan-wrong.org', 'password': 'RandomPassword123'}, True, None),
        ({'login': 'testerwrong', 'password': 'RandomPassword123'}, True, None),
        ({'login': 'test@ckan.org', 'password': 'wrongpassword'}, True, None)
    ], ids=[
        "Empty credentials",
        "Correct credentials with username",
        "Correct credentials with email",
        "Incorrect email",
        "Incorrect username",
        "Incorrect password"
    ])
    def test_authenticate(self, existing_user, identity, result):
        auth = authenticator.EmailAsUsernameAuthenticator()
        if existing_user:
            ckan.tests.factories.User(
                name='tester',
                email='test@ckan.org',
                password='RandomPassword123'
            )
        assert auth.authenticate({}, identity) == result

    def test_email_authentication_fails_if_multiple_accounts_share_email(self):
        auth = authenticator.EmailAsUsernameAuthenticator()
        ckan.tests.factories.User(
            name='tester1',
            email='test@ckan.org',
            password='RandomPassword123'
        )
        try:
            ckan.tests.factories.User(
                name="tester2",
                email="test@ckan.org",
                password="RandomPassword123"
            )
            identity = {'login': 'test@ckan.org', 'password': 'RandomPassword123'}
            response = auth.authenticate({}, identity)
            assert response is None
        except ValidationError as e:
            # CKAN 2.9 does not allow users to have identical emails
            assert "Email" in e.error_summary
