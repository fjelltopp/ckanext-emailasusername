.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/fjelltopp/ckanext-emailasusername.svg?branch=master
    :target: https://travis-ci.org/fjelltopp/ckanext-emailasusername

.. image:: https://coveralls.io/repos/fjelltopp/ckanext-emailasusername/badge.svg
  :target: https://coveralls.io/r/fjelltopp/ckanext-emailasusername

.. image:: https://pypip.in/download/ckanext-emailasusername/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-emailasusername/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-emailasusername/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-emailasusername/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-emailasusername/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-emailasusername/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-emailasusername/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-emailasusername/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-emailasusername/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-emailasusername/
    :alt: License

=============
ckanext-emailasusername
=============

This CKAN extension allows users to login or reset their password with their
email address as well as their username.  If multiple accounts are registered
to your email, you must use your username to login instead. The
extension adds validators to the registration form to ensure that no new
accounts can be created with an email address already attached to another
account.

------------
Requirements
------------

For example, you might want to mention here which versions of CKAN this
extension works with.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-emailasusername:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-emailasusername Python package into your virtual environment::

     pip install ckanext-emailasusername

3. Add ``emailasusername`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Configure CKAN to use the authenticator provided in this plugin. Add
   ``ckanext.emailasusername.authenticator:EmailAsUsernameAuthenticator`` to
   the ``[authenticators] plugins`` configuration in CKAN's who.ini file. In
   ckan core, thise who.ini file is stored in ``ckan/ckan/config`` and linked
   to from ``ckan/``::

       [authenticators]
       plugins =
           auth_tkt
           ckanext.emailasusername.authenticator:EmailAsUsernameAuthenticator


5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.emailasusername --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-emailasusername on PyPI
---------------------------------

ckanext-emailasusername should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-emailasusername. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-emailasusername
----------------------------------------

ckanext-emailasusername is availabe on PyPI as https://pypi.python.org/pypi/ckanext-emailasusername.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags

-----------
With thanks...
-----------

This extension has been built by Fjelltopp with funding from UNAIDS as part of
the AIDS Data Repository project: `https://adr.unaids.org <https://adr.unaids.org>`_

.. image:: https://docs.google.com/a/unaids.org/uc?id=0ByKFPfgVtJ6RMlRjdDNVMFhkb0U&
  :width: 400
  :alt: UNAIDS

.. image:: https://previews.dropbox.com/p/thumb/AAr0hD-MnuJTNfYaOwHz9Pl-TS8UzWYu0_dLpEL_l3XkouqCYQPPe7IdpNfX-c2mJoYGJeYxKOA8GjxpxGYyLaGFNguR9d-_rOuEnHxGAzPdnF-299kvW7nsqYFhRt7YAuFRMWjA7HFyApB9X1ZrRxhpLFoJrrwWmZqPNxwIRPDqru2QJ4YbRhtxahzFvU19t91R1YtY-pwGcQOBmI-udn92EqqtqdO8Zl-K00xxzzr7XQFxOcUvz_wieW4mfFISqWOrTJ4H71cI-_VjLc6PCLSXG8Cdx6SXvbX1WDenE52r4QTgHUGyi5Kc1vkwk-mqZ_6nqeOlkBXufvcYPuOKjnCc/p.png?fv_content=true&size_mode=5
  :width: 400
  :alt: Fjelltopp
