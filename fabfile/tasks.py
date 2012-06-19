from fabric.api import *
from venv import run_venv

@roles('web')
@task
def upgrademoney():
    require('settings', 'virtualenv_root', provided_by=('production'))
    run_venv('django-admin.py upgrademoney --settings=%s' % (env.settings,))

@roles('web')
@task
def countsimilarity(app):
    require('settings', 'virtualenv_root', provided_by=('production'))
    run_venv('django-admin.py countsimilarity %s --settings=%s --list' % (app, env.settings))


@roles('web')
@task
def migrations_list(app):
    require('settings', 'virtualenv_root', provided_by=('production'))
    run_venv('django-admin.py migrate %s --settings=%s --list' % (app, env.settings))

@roles('web')
@task
def migrate(app, migration_number=None, fake='False', dryrun='True'):
    require('settings', 'virtualenv_root', provided_by=('production'))

    migration_number_option = ''
    fake_option = ''
    dryrun_option = ''

    if migration_number is not None:
        migration_number_option = migration_number

    if fake == 'True':
        fake_option = '--fake'

    if dryrun == 'True':
        dryrun_option = '--db-dry-run'

    run_venv('django-admin.py migrate %s %s %s %s --no-initial-data --settings=%s ' %
             (app, migration_number_option, fake_option, dryrun_option, env.settings))





