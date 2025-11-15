#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Start gunicorn
gunicorn mobile_inventory.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
