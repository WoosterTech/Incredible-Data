#!/usr/bin/env bash
# Exit on error
set -o errexit

# Convert static asset files
python manage.py collectstatic --no-input

python manage.py compress

gunicorn config.wsgi --bind 0.0.0.0:8000
