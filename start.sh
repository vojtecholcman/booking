#!/bin/bash
set -e

PROJ="/home/vojta/projects/booking"
cd "$PROJ"

source venv/bin/activate

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn korova_chata.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
