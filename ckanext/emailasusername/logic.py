from ckan.model import User
import ckan.logic as logic
from ckan.model import meta
from sqlalchemy.sql.expression import or_
from sqlalchemy import func
import ckan.plugins.toolkit as toolkit
import ckan.plugins as p
from ckanext.emailasusername.interfaces import IEmailAsUsername
from ckan.logic.action.create import _get_random_username_from_email

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

    data_dict['name'] = _generate_username(data_dict['email'])

    return next_action(context, data_dict)


def _generate_username(email):
    username = _get_random_username_from_email(email)
    for plugin in p.PluginImplementations(IEmailAsUsername):
        username = plugin.generate_username(email, username)
    return username
