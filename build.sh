#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🗂️  Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️  Running database migrations..."
python manage.py migrate

echo "✅ Build completed successfully!"

