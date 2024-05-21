#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
poetry install --with c,production

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# create superuser
if [[ -z "${DJANGO_CREATE_SUPERUSER}" ]]; then
  echo "No superuser created"
else
  python manage.py createsuperuser --noinput
  export DJANGO_SUPERUSER_PASSWORD="invalid"
  export DJANGO_CREATE_SUPERUSER="false"
fi