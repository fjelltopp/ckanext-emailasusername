# encoding: utf-8
import logging
from zope.interface import implements
from repoze.who.interfaces import IAuthenticator
from ckan.model import User

log = logging.getLogger(__name__)


class EmailAsUsernameAuthenticator(object):

    implements(IAuthenticator)

    def authenticate(self, environ, identity):
        log.debug("Authenticate Called")
        if not ('login' in identity and 'password' in identity):
            return None

        login = identity['login']
        log.debug('Login: {}'.format(login))
        user = user_by_username_or_email(login)
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


def user_by_username_or_email(login):
    user = User.by_name(login)
    log.debug("User: {} ".format(user))
    if user:
        return user
    else:
        def not_deleted(user):
            return getattr(user, 'state') != 'deleted'
        user_list = User.by_email(login)
        user_list = filter(not_deleted, user_list)

        if len(user_list) == 1:
            return user_list[0]
        elif len(user_list) > 1:
            log.debug("Multiple users with email address: {}".format(login))
            return None
        else:
            return None
