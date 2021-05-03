#!/bin/sh

set -e # exit if errors happen anywhere
python manage.py collectstatic --noinput
python manage.py migrate

celery -A iidb worker -l info --detach
uwsgi --socket :8000 --master --enable-threads --module iidb.wsgi

