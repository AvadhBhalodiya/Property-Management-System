#!/bin/sh
set -e

echo "waiting for postgres on $DB_HOST:$DB_PORT"
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "postgres is up"

exec "$@"
