#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
poetry install --with c,production

# Convert static asset files
python manage.py collectstatic --no-input

python manage.py compress

# Apply any outstanding database migrations
python manage.py migrate

# create superuser
if [[ -z "${DJANGO_CREATE_SUPERUSER}" ]]; then
  echo "No superuser created"
else
  python manage.py createsuperuser --noinput
  echo "Remove DJANGO_CREATE_SUPERUSER env var"
fi
