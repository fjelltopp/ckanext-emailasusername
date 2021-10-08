from ckan.plugins import toolkit as toolkit


def _get_extension_env(env_variable, default_value):
    return toolkit.config.get(
        'ckanext.emailasusername.{}'.format(env_variable),
        default_value
    )


def get_auto_generate_username_from_fullname():
    return _get_extension_env('auto_generate_username_from_fullname', False)


def get_skip_user_email_input_confirmation():
    return _get_extension_env('skip_user_email_input_confirmation', False)
