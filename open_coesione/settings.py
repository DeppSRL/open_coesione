# -*- coding: utf-8 -*-
# Django settings for open_coesione project.
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.dirname(PROJECT_ROOT))
API_URL = None

# Haystack talks with solr
HAYSTACK_SITECONF = 'open_coesione.search_sites'
HAYSTACK_SEARCH_ENGINE = ''
HAYSTACK_SOLR_URL = ''

# GeoDjango needs GDAL
GDAL_LIBRARY_PATH = ''

DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_LESS=False


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Much easier than using floatformat:0 in templates
USE_THOUSAND_SEPARATOR = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(REPO_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(REPO_ROOT, 'sitestatic')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(DPS_ISTAT_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# This is your public and private API keys as provided by reCAPTCHA
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
#RECAPTCHA_USE_SSL = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'open_coesione.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'open_coesione.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_extensions',
    'django.contrib.gis',
    'django.contrib.humanize',
    'open_coesione',
    'sekizai',
    'bootstrapform',
    'south',
    'haystack',
    'oc_search',
    'tinymce',
    'captcha',
    'cache_panel',
    'disqus',
    'open_coesione',
    'progetti',
    'soggetti',
    'territori',
    'blog',
    'idioticon',
    'tagging',
    'urlshortener',
    'open_coesione.charts',
    'rest_framework',
    'api',
    'widgets',
    'solo',
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'cache_panel.panel.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

# context processors and templates directory
from django.conf.global_settings import TEMPLATE_DIRS, TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_DIRS += (os.path.join(REPO_ROOT, 'templates'),)
TEMPLATE_CONTEXT_PROCESSORS += (
    'open_coesione.context_processor.main_settings',
    'django.core.context_processors.request',
    'sekizai.context_processors.sekizai',
)

TEMATIZZAZIONI = ('totale_costi', 'totale_pagamenti', 'totale_progetti')
MAP_TEMATIZZAZIONI = TEMATIZZAZIONI + ('totale_costi_procapite',)

CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",  # db 1
        "TIMEOUT": 0,
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

CACHE_PAGE_DURATION_SECS = 86400 * 360

MAPNIK_HOST = False
TILESTACHE_CACHE_PATH = ''
TILESTACHE_URL = ''

GRAY_MAP_COLORS = {
    'c0': '#eae7df',
    'c1': '#c9c7c3',
    'c2': '#969491',
    'c3': '#676462',
    'c4': '#2d2b2a',
}

# http://colorbrewer2.org/ color map
# "#F7FCFD", "#E5F5F9", "#CCECE6", "#99D8C9", "#66C2A4", "#41AE76", "#238B45", "#005824"

MAP_COLORS = {
    'c0': '#eae7df',
    'c1': '#d1e2d6',
    'c2': '#b6d9c4',
    'c3': '#97bba6',
    'c4': '#54816a',
    'c5': '#0f5433',
}

N_MAX_DOWNLOADABLE_RESULTS = 1000

# used in middleware for site-wide caching
# CACHE_MIDDLEWARE_SECONDS = 86400
# CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s.%(msecs).03d] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': REPO_ROOT + "/log/logfile",
            'maxBytes': 10000000,
            'backupCount': 10,
            'formatter': 'standard',
        },
        'import_logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': REPO_ROOT + "/log/import_logfile",
            'mode': 'w',
            'formatter': 'standard',
        },
        'cg_logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': REPO_ROOT + "/log/cg_logfile",
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'oc': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'csvimport': {
            'handlers': ['console', 'import_logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'cachegenerator': {
            'handlers': ['cg_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', ],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

# recipients for contacts
CONTACTS_EMAIL = tuple()

# tinymce admin support
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'tiny_mce')
TINYMCE_JS_URL = os.path.join(STATIC_URL, "tiny_mce/tiny_mce_src.js")
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'theme_advanced_toolbar_location': "top"
}
TINYMCE_SPELLCHECKER = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '12/minute',  # 1 req every 5 seconds
        'user': '2/second',  # un-throttled  (default: '1/second')
    },
    'PAGINATE_BY': 25,
    'MAX_PAGE_BY': 500,
    'PAGINATE_BY_PARAM': 'page_size',
}

SOUTH_TESTS_MIGRATE = False

TEST_RUNNER = 'open_coesione.testing.DatabaselessTestRunner'

WIDGETS = [
    'territori.widgets.TerritorioWidget',
    'progetti.widgets.TemaWidget',
    'progetti.widgets.NaturaWidget',
    'progetti.widgets.ProgettoWidget',
    'progetti.widgets.ProgettiWidget',
    'soggetti.widgets.SoggettoWidget',
]

BIG_SOGGETTI_THRESHOLD = 2000
BIG_PROGRAMMI_THRESHOLD = 500

GRAPPELLI_ADMIN_TITLE = "Amministrazione di OpenCoesione"
GRAPPELLI_INDEX_DASHBOARD = 'open_coesione.dashboard.CustomIndexDashboard'
FILEBROWSER_STRICT_PIL = True
FILEBROWSER_NORMALIZE_FILENAME = True
FILEBROWSER_VERSIONS_BASEDIR = '_versions'
FILEBROWSER_SEARCH_TRAVERSE = True
FILEBROWSER_MAX_UPLOAD_SIZE = 104857600
FILEBROWSER_EXTENSIONS = {
    'Folder': [''],
    'Image': ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff'],
    'Document': ['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv', '.zip'],
    'Video': ['.mov', '.wmv', '.mpeg', '.mpg', '.avi', '.rm'],
    'Audio': ['.mp3', '.mp4', '.wav', '.aiff', '.midi', '.m4p']
}
FILEBROWSER_SELECT_FORMATS = {
    'file': ['Folder', 'Image', 'Document', 'Video', 'Audio'],
    'image': ['Image'],
    'document': ['Document'],
    'media': ['Video', 'Audio'],
}

URLSHORTENER_DOMAIN = 'opencoesione.gov.it'

SECTION1420_PAGES = (
    {
        'name': 'OpenCoesione nella programmazione 2014-2020',
        'url': '/programmazione_2014_2020/',
    },
    {
        'name': 'Risorse',
        'url': '/risorse_2014_2020/',
    },
    {
        'name': 'Programmi',
        'url': '/programmi_2014_2020/',
    },
    {
        'name': 'Opportunità',
        'url': '/opportunita_2014_2020/',
    },
    {
        'name': 'Bandi',
        'url': '/bandi_2014_2020/',
    },
    {
        'name': 'Progetti',
        'url': '/progetti_2014_2020/',
    },
    {
        'name': 'Aiuti',
        'url': '/aiuti_2014_2020/',
    },
)
