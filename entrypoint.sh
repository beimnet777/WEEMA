#!/bin/bash
# entrypoint.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check PostgreSQL readiness using Python
function postgres_ready(){
python << END
import sys
import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        connect_timeout=1
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until postgres_ready; do
  sleep 1
done
python manage.py makemigrations --noinput

echo "Database migrations applied."
python manage.py collectstatic --noinput

# Start the Django server
exec "$@"
