#!/bin/sh
set -e

echo "waiting for postgres on $DB_HOST:$DB_PORT"
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "postgres is up"

if [ "$RUN_MIGRATIONS" = "true" ]; then
    python manage.py migrate --noinput

    if [ "$SEED_DEMO_DATA" = "true" ]; then
        python manage.py seed_demo_data
    fi
fi

exec "$@"
