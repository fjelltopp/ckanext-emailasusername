# encoding: utf-8
import ckan.lib.helpers as h
import ckan.lib.mailer as mailer
from ckan.model.user import User
from ckan.common import _
from flask import Blueprint, request
import logging

log = logging.getLogger(__name__)

emailasusername = Blueprint(
    u'emailasusername',
    __name__,
    url_prefix='/emailasusername'
)


def user_by_username_or_email(login):
    user = User.by_name(login)
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
            h.flash_error(_(u'Multiple users with email: {}').format(login))
            return None
        else:
            h.flash_error(_(u'No such user: {}').format(login))
            return None


def request_reset():
    id = request.form.get(u'user')
    user_obj = user_by_username_or_email(id)
    if user_obj:
        try:
            mailer.send_reset_link(user_obj)
            h.flash_success(_(u'Please check your inbox for a reset code.'))
            return h.redirect_to(h.url_for('user.login'))
        except mailer.MailerException as e:
            h.flash_error(_(u'Could not send reset link: {}').format(e))
    return h.redirect_to(h.url_for('user.reset'))


emailasusername.add_url_rule(
    u'/reset',
    view_func=request_reset,
    methods=['POST']
)
