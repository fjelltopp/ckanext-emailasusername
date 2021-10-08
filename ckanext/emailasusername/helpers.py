from ckan.plugins import toolkit as toolkit


def get_auto_generate_username_from_fullname():
    return toolkit.config.get(
        'ckanext.emailasusername.auto_generate_username_from_fullname',
        False
    )
