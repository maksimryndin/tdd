from fabric.contrib.files import append, exists
from fabric.api import env, local
import random
import string


REPO_URL = 'https://github.com/maksimryndin/tdd.git'


def deploy():
    site_folder = '/home/{}/superlists-staging'.format(env.user)
    source_folder = site_folder + '/source'
    _get_latest_source(source_folder)
    _update_settings(source_folder)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_db(source_folder)
    _update_wsgi()
    _test_deployment(source_folder)


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        local('cd {} && git pull'.format(source_folder))
    else:
        local('git clone {} {}'.format(REPO_URL, source_folder))


def _update_settings(source_folder):
    settings_path = source_folder + '/superlists/settings/prod.py'
    secret_key_file = source_folder + '/superlists/settings/secret_key.py'
    if not exists(secret_key_file):
        chars = string.ascii_lowercase + string.digits + '@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '{}'".format(key))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        local('virtualenv --python=python3 {}'.format(virtualenv_folder))
    local('{}/bin/pip install -r {}/requirements.txt'.format(virtualenv_folder, source_folder))


def _update_static_files(source_folder):
    local('''cd {} && ../virtualenv/bin/python3 manage.py
          collectstatic --noinput'''.format(source_folder))


def _update_db(source_folder):
    local('''cd {} && ../virtualenv/bin/python3 manage.py
          migrate --noinput'''.format(source_folder))


def _update_wsgi():
    local('touch /var/www/maksimryndin_pythonanywhere_com_wsgi.py')


def _test_deployment(source_folder):
    local('cd {} && python manage.py test'.format(source_folder))
