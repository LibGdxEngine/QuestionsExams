#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements/production.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Restart Gunicorn
sudo systemctl restart gunicorn