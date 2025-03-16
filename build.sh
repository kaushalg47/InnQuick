#!/usr/bin/env bash
# exit on error
set -0 errexit
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email
