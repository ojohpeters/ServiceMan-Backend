#!/usr/bin/env bash
# Render start command

echo "🚀 Starting application..."
echo "📍 Port: $PORT"
echo "🌐 Host: 0.0.0.0"

# Start Gunicorn with optimal settings for Render
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

