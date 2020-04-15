.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/fjelltopp/ckanext-emailasusername.svg?branch=master
    :target: https://travis-ci.org/fjelltopp/ckanext-emailasusername

.. image:: https://coveralls.io/repos/fjelltopp/ckanext-emailasusername/badge.svg
  :target: https://coveralls.io/r/fjelltopp/ckanext-emailasusername

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

=======================
ckanext-emailasusername
=======================

We have have found that many of our users quickly forget their CKAN username.
We have also observed several users assume they should use their email to
login.  This fails with a bad login error message, which causes some confusion.

This CKAN extension allows users to login or reset their password with either
their email address or their username. It doesn't do away with the username
but just offers the option to use email instead.

Out of the box, CKAN allows multiple accounts to be registered with the same
email address.  This causes a problem for using email to identify the user.
This extension therefore adds a validator to the registration form to stop
new accounts being created if there already exists an account with the same
email.

If multiple accounts are registered to your email, then identifying the user
by email fails - you must use your username to login/reset your password
instead. It's recommended, if feasible, to work with your userbase to phase
out multiple accounts with the same email.

**Important**  Installing this extension requires editing CKAN's who.ini file to point to the new authenticator.py file provided by this module.  Make sure you complete complete step 4 in the installation instructions below.

------------
Requirements
------------

This extension has been built and tested with CKAN 2.8.2. 

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


--------------------------------------------------
Releasing a New Version of ckanext-emailasusername
--------------------------------------------------

ckanext-emailasusername is availabe on PyPI as https://pypi.python.org/pypi/ckanext-emailasusername.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist bdist_wheel

3. Upload the source distribution to PyPI::

     python -m twine upload dist/*

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags


--------------
With thanks...
--------------

This extension has been built by Fjelltopp with funding from UNAIDS as part of
the AIDS Data Repository project: `https://adr.unaids.org <https://adr.unaids.org>`_

.. image:: https://hivtools.unaids.org/images/unaids.png
  :width: 400
  :alt: UNAIDS

.. image:: https://hivtools.unaids.org/images/FjelltoppColourBlue.png
  :width: 400
  :alt: Fjelltopp
