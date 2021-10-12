from ckan.plugins import toolkit as toolkit


def _get_config_value(key, default_value):
    return toolkit.config.get(
        'ckanext.emailasusername.{}'.format(key),
        default_value
    )


def config_auto_generate_username_from_fullname():
    return _get_config_value('auto_generate_username_from_fullname', False)


def config_require_user_email_input_confirmation():
    return _get_config_value('require_user_email_input_confirmation', True)
