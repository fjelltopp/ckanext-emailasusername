from ckan.model import User
import ckan.logic as logic
from ckan.model import meta
from sqlalchemy.sql.expression import or_
from sqlalchemy import func
import ckan.plugins.toolkit as toolkit
import ckan.plugins as p
from ckanext.emailasusername.interfaces import IEmailAsUsername
import re
import random

_check_access = logic.check_access


def search_by_username_and_email(querystr, sqlalchemy_query=None, user_name=None):
    '''Search name, fullname, email. '''
    if sqlalchemy_query is None:
        query = meta.Session.query(User)
    else:
        query = sqlalchemy_query
    qstr = '%' + querystr + '%'
    filters = [
        User.name.ilike(qstr),
        User.fullname.ilike(qstr),
    ]
    # sysadmins can search on user emails, everyone else has to know the exact email
    import ckan.authz as authz
    if user_name and authz.is_sysadmin(user_name):
        filters.append(User.email.ilike(qstr))
    else:
        filters.append(func.lower(User.email) == func.lower(querystr))
    query = query.filter(or_(*filters))
    return query


@logic.validate(logic.schema.default_autocomplete_schema)
def user_autocomplete(context, data_dict):
    '''Return a list of users with names that contain a string or emails
    that match a string.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of user names to return (optional,
        default: ``20``)
    :type limit: int

    :rtype: a list of user dictionaries each with keys ``'name'``,
        ``'fullname'``, and ``'id'``

    '''
    model = context['model']
    user = context['user']

    _check_access('user_autocomplete', context, data_dict)

    q = data_dict['q']
    limit = data_dict.get('limit', 20)
    ignore_self = data_dict.get('ignore_self', False)
    query = search_by_username_and_email(q, user_name=user)
    query = query.filter(model.User.state != model.State.DELETED)

    if ignore_self:
        query = query.filter(model.User.name != user)

    query = query.limit(limit)

    user_list = []
    for user in query.all():
        result_dict = {}
        for k in ['id', 'name', 'fullname']:
            result_dict[k] = getattr(user, k)

        user_list.append(result_dict)

    return user_list


@toolkit.chained_action
def user_create(next_action, context, data_dict):
    """
    Autogenerates a username using the email field (if username is not provided).
    """

    if data_dict.get('name'):
        return next_action(context, data_dict)

    if not data_dict.get('email'):
        raise toolkit.ValidationError(toolkit._("Must specify either a name or an email"))

    email = data_dict['email']
    username = _get_random_username_from_email(email, context['model'])

    for plugin in p.PluginImplementations(IEmailAsUsername):
        username = plugin.generate_username(email, username)

    data_dict['name'] = username

    return next_action(context, data_dict)


def _get_random_username_from_email(email, model):
    """
    This function is copied from a CKAN core private function:
        ckan.logic.action.create._get_random_username_from_email
    Github permalink:
        https://github.com/ckan/ckan/blob/0a596b8394dbf9582902853ad91450d2c0d7959b/ckan/logic/action/create.py#L1102-L1116

    The function has been deployed and used across a plethora of CKAN
    instances, which is why we are adopting it here.

    WARNING: This logic reveals part of the user's email address
    as their username.  Fjelltopp recommends overriding this logic
    for public CKAN instances. Use the IEmailAsUsername plugin
    interface to do this.
    """

    localpart = email.split('@')[0]
    cleaned_localpart = re.sub(r'[^\w]', '-', localpart).lower()

    # if we can't create a unique user name within this many attempts
    # then something else is probably wrong and we should give up
    max_name_creation_attempts = 100

    for i in range(max_name_creation_attempts):
        random_number = random.SystemRandom().random() * 10000
        name = '%s-%d' % (cleaned_localpart, random_number)
        if not model.User.get(name):
            return name

    return cleaned_localpart
