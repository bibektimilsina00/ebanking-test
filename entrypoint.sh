#!/bin/bash
# entrypoint.sh

# Function to wait for MySQL to be ready
wait_for_db() {
    echo "Waiting for MySQL..."
    # Loop until 'mysqladmin ping' gets a response
    while ! mysqladmin ping -h"$MYSQL_HOST" --silent; do
        sleep 1
    done
}

# Wait for the database to become available
wait_for_db

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting server..."
gunicorn ebanking.wsgi:application --bind 0.0.0.0:8000
