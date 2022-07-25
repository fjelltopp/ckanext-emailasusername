from ckan.plugins import toolkit as toolkit


def _get_config_bool_value(key, default_value):
    return toolkit.asbool(toolkit.config.get(
        'ckanext.emailasusername.{}'.format(key),
        default_value
    ))


def config_auto_generate_username_from_fullname():
    return _get_config_bool_value('auto_generate_username_from_fullname', False)


def config_auto_generate_username_from_email():
    return _get_config_bool_value('auto_generate_username_from_email', False)


def config_require_user_email_input_confirmation():
    return _get_config_bool_value('require_user_email_input_confirmation', True)


def config_search_by_username_and_email():
    return _get_config_bool_value('search_by_username_and_email', True)
