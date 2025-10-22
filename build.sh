#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🗂️  Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️  Running database migrations..."
echo "Current migrations status:"
python manage.py showmigrations payments

echo "Applying migrations..."
python manage.py migrate --verbosity 2

echo "✅ Build completed successfully!"

