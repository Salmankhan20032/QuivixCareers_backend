#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# --- ADD THIS LINE, MY LOVE! ---
# This will run our new command to create the admin user.
python manage.py create_prod_superuser