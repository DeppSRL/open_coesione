## -*- mode: python -*-
"""
Fabric script (a.k.a. "fabfile.deprecated") to automate the deployment process
of an instance of the Open Coesione web application.

Deployment on both staging & production machine(s) is supported:

* To deploy on the staging server(s), run the shell command ``fab staging deploy``
* To deploy on the production server(s), run the shell command ``fab production deploy``

The first time you perform a deploy on a given machine (or set of machines), you MUST
use the command  `fab (staging|production) initial_deploy`` instead, which takes care
of performing one-time initialization tasks.

In order to customize the deployment procedure to suit your specific needs,
you can control the behaviour of this script by setting up the provided configuration files
(``conf_staging.py`` and ``conf_production.py`` for staging and production deployment,
respectively).
"""
from fabric.utils import abort
from fabric.api import env, execute, hide, require, roles, run, settings, sudo, task

import code, database as db, venv, static, webserver, solr, provision

import os


## Environment-specific setup
@task
def staging():
    """
    Deploys OpenMunicipio to the staging server.
    """
    # import staging's conf module
    import conf_staging as conf
    ## set up Fabric global environment dictionary
    env.environment = 'staging'
    env.server = conf.SERVER_MACHINE
    env.project = conf.PROJECT_NAME
    env.app_domain = conf.APP_DOMAIN
    env.local_repo_root = conf.LOCAL_REPO_ROOT
    env.local_project_root = conf.LOCAL_PROJECT_ROOT
    env.rsync_exclude = conf.RSYNC_EXCLUDE
    env.python = conf.PYTHON_FULL_PATH
    env.web_user = conf.WEB_USER
    env.web_root = conf.WEB_ROOT
    env.domain_root = conf.DOMAIN_ROOT
    env.virtualenv_root = conf.VIRTUALENV_ROOT
    env.project_root = conf.PROJECT_ROOT
    env.settings = conf.DJANGO_SETTINGS_MODULE
    env.static_root = conf.STATIC_ROOT
    # Tomcat
    env.tomcat_user = conf.TOMCAT_USER
    env.tomcat_controller = conf.TOMCAT_CONTROLLER
    env.catalina_home = conf.CATALINA_HOME
    # Solr
    env.solr_download_link = conf.SOLR_DOWNLOAD_LINK
    env.solr_install_dir = conf.SOLR_INSTALL_DIR
    env.solr_home = conf.SOLR_HOME
    # role definitions
    env.roledefs = {
        'admin': ['root@%(server)s' % env],
        'web': ['%(web_user)s@%(server)s' % env],
        'db': ['dba@%(server)s' % env],
        'solr': ['solr@%(server)s' % env],
        }

@task
def production():
    """
    Deploys OpenMunicipio to the production server.
    """
    env.environment = 'production'
    abort('Production deployment not yet implemented.')


## Macro-tasks

@task
def setup_platform():
    """
    Takes care of all preliminay tasks needed to setup the OS of the
    target machine(s) in order for the deploy of an OpenMunicipio instance
    to be possible.
    """
    require('environment', provided_by=('staging', 'production'))
    # setup Solr (include Tomcat's setup)
    execute(provision.setup_solr)
    # execute(provision.setup_postgres)

@task
def initial_deploy():
    """
    Deploy the web application to remote server(s) **for the first time**.

    The first deployment procedure may differ from subsequent ones,
    since some initialization tasks have to be performed only once.

    Some examples:
    * fake South migrations
    * ..
    """
    require('environment', provided_by=('staging', 'production'))
    env.initial_deploy = True
    execute(deploy)


@task
@roles('web')
def deploy():
    """
    Deploy the web application to remote server(s)
    """
    require('environment', provided_by=('staging', 'production'))
    with hide('commands'):
    ## one-time initialization steps go here
        if env.get('initial_deploy'):
            # create the initial filesystem layout
            execute(code.make_website_skeleton)
            # add a new core for this OpenMunicipio instance
            execute(solr.add_new_core)
            ## tasks to be performed each time the application is deployed on the server
            # sanity check
        with hide('everything'):
            if run('test -d %(domain_root)s' % env).failed:
                abort("It seems that the root dir for this OpenMunicipio instance has not been created, yet.")
        with settings(warn_only=True):
            execute(webserver.stop)
            # update Django project's files
        execute(code.update_project)
        # update external dependencies
        execute(venv.update_requirements)
        # update DB
        execute(db.update)
        # update Solr conf
        execute(solr.update_core_conf)
        # update Solr index
        execute(solr.update_index)
        # collect static files
        execute(static.collect_files)
        # clear webserver's log when deploying to the staging server
        if env.environment == 'staging': execute(webserver.clear_logs)
        # update webserver configuration
        execute(webserver.update_conf)
        execute(webserver.start)
        # adjust filesystem permissions
        execute(adjust_permissions)


@roles('admin')
def adjust_permissions():
    """
    Adjust filesystem permissions after completing the deployment process.
    """
    require('web_user', 'domain_root', provided_by=('staging', 'production'))
    sudo('chown -R %(web_user)s:www-data %(domain_root)s' % env)
    ## Only needed for SQLite DBs
    # SQLite needs write access to the folder containing the DB file
    sudo('chmod g+w %(domain_root)s/private' % env)
    # SQLite need write access to the DB file itself
    db_file = os.path.join(env.domain_root, 'private', 'db.sqlite')
    sudo('chmod g+w %s' % db_file)
