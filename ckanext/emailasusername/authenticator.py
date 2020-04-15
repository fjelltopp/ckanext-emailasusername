# encoding: utf-8
import logging
from zope.interface import implements
from repoze.who.interfaces import IAuthenticator
from ckanext.emailasusername.blueprint import user_by_username_or_email

log = logging.getLogger(__name__)


class EmailAsUsernameAuthenticator(object):
    """
    CKAN uses WSGI authentication middleware who.repoze to manage its
    authentication.  Here we override the default authentication behaviour
    to check the given credentials against email and username data.

    When installing this extension you must configure CKAN to use this
    authenticator. Check the installation instructions for how to update
    who.ini file to do this.
    """

    implements(IAuthenticator)

    def authenticate(self, environ, identity):
        log.debug("Authenticate Called")
        if not ('login' in identity and 'password' in identity):
            return None

        login = identity['login']
        log.debug('Login: {}'.format(login))
        # No translator available when this function is called...
        # ...so be careful not to flash translated errors here.
        user = user_by_username_or_email(login, flash_errors=False)
        log.debug("User: {}".format(user))

        if user is None:
            log.debug('Login failed - {} not found'.format(login))
        elif not user.is_active():
            log.debug('Login as {} failed - user isn\'t active'.format(login))
        elif not user.validate_password(identity['password']):
            log.debug('Login as {} failed - password not valid'.format(login))
        else:
            return user.name

        return None
