## -*- mode: python -*-
"""
Starter fabfile for deploying a Django-powered web application.

All the settings marked with ``CHANGEME`` MUST be changed to reflect
project-specific setup.  Other settings MAY be changed, but their values should be
generic enough to provide for sensible defaults.
"""
from fabric import utils
from fabric.api import *
from fabric.context_managers import cd, lcd, settings

import code, database as db, venv, static, webserver, solr, tasks

import os

# Python interpreter executable to use on virtualenv creation
PYTHON_BIN = 'python' #pyhton 2.7
PYTHON_PREFIX = '' # e.g. ``/usr``, ``/usr/local``; leave empty for default.
PYTHON_FULL_PATH = "%s/bin/%s" % (PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX else PYTHON_BIN

# exclude patterns for ``rsync`` invocations
RSYNC_EXCLUDE = ( 
    ##CHANGEME!
    '*~',
    '.git',
    '.gitignore',
    '.idea',
    '.DS_Store',
    '*.pyc',
    '*.sample',
    '*.eml',
    'docs/',
    '*.markdown',
    '*.gz',
    'fabfile',
    'project_site',
    'apache/*',
    'import_tmp/*',
    'solr',
    'log',
    'solr.example',
    'open_coesione/settings_*.py',
    'open_coesione/urls_*.py',
    'sitestatic',
    'media',
    '*.sqlite',
    '*.db',
    '*.db.old',
    'manage.py',
    'fixtures/*',
    'GIS/tiles/*',
    'dati/*',
    'splitcsv2.py',
    'smtp_sink_server.py',
)

## TODO: these constants should be read from an external configuration file
# the name of the project managed by this fabfile
PROJECT_NAME = 'open_coesione'
# a unique identifier for this web application instance
# usually is set to the primary domain from which the web application is accessed
APP_DOMAIN = 'stagingcoesione.deppsviluppo.org'
# filesystem location of project's files on the local machine
LOCAL_PROJECT_ROOT = '/Users/guglielmo/Workspace/open_coesione'

env.project = PROJECT_NAME
env.app_domain = APP_DOMAIN
env.local_project_root = LOCAL_PROJECT_ROOT
env.rsync_exclude = RSYNC_EXCLUDE
env.python = PYTHON_FULL_PATH
## Environment-specific setup

@task
def staging():
    """ Use staging environment on remote host"""
    env.environment = 'staging'
    ## TODO: these constants should be read from an external configuration file
    # the system user (on the server machine) used for managing websites
    WEB_USER = 'webmaster'
    # the parent directory of domain-specific directories (on the server machine)
    WEB_ROOT = '/home/' #I keep it simple, here
    # the root directory for domain-specific files (on the server machine)
    DOMAIN_ROOT = os.path.join(WEB_ROOT, env.app_domain)
    # the root directory of application-specific Python virtual environment (on the server machine)
    VIRTUALENV_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'venv')
    # the root directory for project-specific files (on the server machine)
    PROJECT_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'python')
    # the root directory for application-specific Python code (on the server machine)
    CODE_ROOT = os.path.join(PROJECT_ROOT, env.project) ##CHANGEME!
    # import path of Django settings file for the staging environment
    DJANGO_SETTINGS_MODULE = '%(project)s.settings_staging' % env
    # Directory where static files should be collected.  This MUST equal the value
    # of ``STATIC_ROOT`` attribute of the Django settings module used on the server.
    STATIC_ROOT =  os.path.join(DOMAIN_ROOT, 'public', 'static') ## CHANGEME!

    ## set up Fabric global environment dictionary
    env.web_user = WEB_USER
    env.web_root = WEB_ROOT
    env.domain_root = DOMAIN_ROOT
    env.virtualenv_root = VIRTUALENV_ROOT
    env.project_root = PROJECT_ROOT
    env.code_root = CODE_ROOT
    env.settings = DJANGO_SETTINGS_MODULE
    env.static_root = STATIC_ROOT

    env.roledefs = {
        'web': ['%(web_user)s@ovhb2' % env],
        'db': ['dba@ovhb2'],
        }


@task
def production():
    """ Use staging environment on remote host"""
    env.environment = 'production'
    ## TODO: these constants should be read from an external configuration file
    # the system user (on the server machine) used for managing websites
    WEB_USER = 'webmaster'
    # the parent directory of domain-specific directories (on the server machine)
    WEB_ROOT = '/home/' #I keep it simple, here
    # the root directory for domain-specific files (on the server machine)
    DOMAIN_ROOT = os.path.join(WEB_ROOT, env.app_domain)
    # the root directory of application-specific Python virtual environment (on the server machine)
    VIRTUALENV_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'venv')
    # the root directory for project-specific files (on the server machine)
    PROJECT_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'python')
    # the root directory for application-specific Python code (on the server machine)
    CODE_ROOT = os.path.join(PROJECT_ROOT, env.project) ##CHANGEME!
    # import path of Django settings file for the staging environment
    DJANGO_SETTINGS_MODULE = '%(project)s.settings_production' % env
    # Directory where static files should be collected.  This MUST equal the value
    # of ``STATIC_ROOT`` attribute of the Django settings module used on the server.
    STATIC_ROOT =  os.path.join(DOMAIN_ROOT, 'public', 'static') ## CHANGEME!

    ## set up Fabric global environment dictionary
    env.web_user = WEB_USER
    env.web_root = WEB_ROOT
    env.domain_root = DOMAIN_ROOT
    env.virtualenv_root = VIRTUALENV_ROOT
    env.project_root = PROJECT_ROOT
    env.code_root = CODE_ROOT
    env.settings = DJANGO_SETTINGS_MODULE
    env.static_root = STATIC_ROOT

    env.roledefs = {
    'web': ['%(web_user)s@XXX' % env],
    'db': ['dba@XXX'],
    }
 
## Macro-tasks
@task
@roles('web')
def initial_deploy():
    """
    Deploy the web application to remote server(s) **for the first time**

    The first deployment procedure may differ from subsequent ones,
    since some initialization tasks have to be performed only once.

    Some examples:
    * fake South migrations
    * ..
    """
    require('environment', provided_by=('production', 'staging'))
    env.initial_deploy = True
    deploy()        

@task
@roles('web')
def deploy():
    """
    Deploy the web application to remote server(s)
    """
    require('environment', provided_by=('production', 'staging'))
    ## TODO: early initialization steps go here  
    if env.get('initial_deploy'):
        code.copy_website_skeleton()

    code.update()
    venv.update_requirements()
    db.update()
    webserver.clear_logs()

    webserver.restart()


def adjust_permissions():
    """
    Adjust filesystem permissions after completing the deployment process.
    """
    require('web_user', 'domain_root', provided_by=('production', 'staging'))
    sudo('chown -R www-data:sudo %(domain_root)s' % env)


