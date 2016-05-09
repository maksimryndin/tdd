import random
import string
from os import path, makedirs, environ

from fabric.api import env, local


REPO_URL = "https://github.com/maksimryndin/tdd.git"


def deploy():
    site_folder = '/home/{}/superlists-staging'.format(env.user)
    source_folder = site_folder + '/source'
    _get_latest_source(source_folder)
    _update_settings(source_folder)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_db(source_folder)
    _update_wsgi()


def _get_latest_source(source_folder):
    if path.exists(source_folder + '/.git'):
        local('cd {} && git pull'.format(source_folder))
    else:
        makedirs(source_folder)
        local('cd {0} && git clone {1} {0}'.format(source_folder, REPO_URL))


def _update_settings(source_folder):
    environ["DJANGO_SETTINGS_MODULE"] = "superlists.settings.prod"
    settings_path = source_folder + '/superlists/settings/prod.py'
    secret_key_file = source_folder + '/superlists/settings/secret_key.py'
    if not path.exists(secret_key_file):
        chars = string.ascii_lowercase + string.digits + '@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        with open(secret_key_file, 'w') as f:
            f.write("SECRET_KEY = '{}'".format(key))
    with open(settings_path, 'a') as set_file:
        set_file.write('\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not path.exists(virtualenv_folder + '/bin/pip'):
        local('virtualenv --python=python3 {}'.format(virtualenv_folder))
    local('{}/bin/pip install -r {}/requirements.txt'.format(virtualenv_folder, source_folder))


def _update_static_files(source_folder):
    static_folder = source_folder + '/../static'
    if not path.exists(static_folder):
        makedirs(static_folder)
    local('cd {} && ../virtualenv/bin/python3 manage.py collectstatic --noinput'.format(source_folder))


def _update_db(source_folder):
    db_folder = source_folder + '/../database'
    if not path.exists(db_folder):
        makedirs(db_folder)
    local('cd {} && ../virtualenv/bin/python3 manage.py migrate --noinput'.format(source_folder))


def _update_wsgi():
    local('touch /var/www/maksimryndin_pythonanywhere_com_wsgi.py')
