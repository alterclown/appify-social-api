#!/bin/sh

# Parse connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -e 's/.*@//' -e 's/:.*/ /' | awk '{print $1}')
DB_PORT=$(echo $DATABASE_URL | sed -e 's/.*://' -e 's/\/.*//')
DB_USER=$(echo $DATABASE_URL | sed -e 's/.*:\/\///' -e 's/:.*//')
DB_NAME=$(echo $DATABASE_URL | sed -e 's/.*\///')

echo "Checking if PostgreSQL is available at $DB_HOST:$DB_PORT..."

if ! nc -z $DB_HOST $DB_PORT; then
  echo "--------------------------------------------------------"
  echo "ERROR: PostgreSQL is NOT running on $DB_HOST:$DB_PORT!"
  echo "Please start your local PostgreSQL instance first."
  echo "--------------------------------------------------------"
  exit 1
fi

echo "PostgreSQL detected!"
export PGPASSWORD="password"

# 1. Check if the specific database exists, and create it if it doesn't
DB_EXISTS=$(psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
  echo "Database '$DB_NAME' does not exist. Creating it now..."
  psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "CREATE DATABASE \"$DB_NAME\";"
else
  echo "Database '$DB_NAME' already exists."
fi

# 2. Run your schema file against the target database
echo "Running schema file: social_feed.sql..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f /app/social_feed.sql

echo "Database initialized successfully. Launching API..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000