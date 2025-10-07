#!/bin/bash
# Railway deployment script
# This script handles the deployment process

echo "🚀 Starting Railway deployment..."

# Set default environment variables if not set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"config.settings.production"}
export DEBUG=${DEBUG:-"False"}
export PORT=${PORT:-"8000"}

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔧 Starting Gunicorn server..."
gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --worker-class gevent \
    --timeout 120 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile -
