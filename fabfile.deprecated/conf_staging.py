import os

# IP/domain name of the staging server
SERVER_MACHINE = 'stagingcoesione.deppsviluppo.org'
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
    'fabfile.deprecated',
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

# the name of the Django project managed by this fabfile.deprecated
PROJECT_NAME = 'open_coesione'
# a unique identifier for this web application instance
# usually it's set to the primary domain from which the web application is accessed
APP_DOMAIN = 'stagingcoesione.deppsviluppo.org'
# filesystem location of project's repository on the local machine
LOCAL_REPO_ROOT =  os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
# filesystem location of Django project's files on the local machine
LOCAL_PROJECT_ROOT = os.path.join(LOCAL_REPO_ROOT, PROJECT_NAME)
# the system user (on the server machine) used for managing this OpenMunicipio's instance
WEB_USER = 'oc'
# the parent directory of domain-specific directories (on the server machine)
WEB_ROOT = '/home/opencoesione'
# the root directory for domain-specific files (on the server machine)
DOMAIN_ROOT = os.path.join(WEB_ROOT, APP_DOMAIN)
# the root directory of application-specific Python virtual environment (on the server machine)
VIRTUALENV_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'venv')
# the root directory for project-specific files (on the server machine)
PROJECT_ROOT = os.path.join(DOMAIN_ROOT, 'private', PROJECT_NAME)
# import path of Django settings module for the staging environment
DJANGO_SETTINGS_MODULE = '%(project)s.settings_staging' % {'project': PROJECT_NAME}
# Directory where static files should be collected.  This MUST equal the value
# of ``STATIC_ROOT`` attribute of the Django settings module used on the server.
STATIC_ROOT =  os.path.join(DOMAIN_ROOT, 'public', 'static')
# system user the Tomcat process run as
TOMCAT_USER = 'tomcat6'
# Tomcat's controller script
TOMCAT_CONTROLLER = '/etc/init.d/tomcat6'
# home dir for Catalina
CATALINA_HOME = '/etc/tomcat6/Catalina'
# URL pointing to the Solr distribution to be installed on the server machine
# Must be a compressed tarball (i.e. a  ``.tgz`` or ``.tar.gz`` file)
SOLR_DOWNLOAD_LINK = 'http://apache.fastbull.org/lucene/solr/3.6.0/apache-solr-3.6.0.tgz'
# where Solr configuration and data reside on the server machine
SOLR_INSTALL_DIR = '/home/apache-solr-3.6.0'
# where configuration/data files for Solr reside on the server machine
SOLR_HOME = '/home/solr'