#!/bin/sh

set -e # exit if errors happen anywhere
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :8000 --master --enable-threads --module todo_django_app_name_here.wsgi
