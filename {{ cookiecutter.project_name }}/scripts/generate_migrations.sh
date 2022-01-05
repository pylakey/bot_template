#!/bin/bash
set -e
. ./.env

DB_URI="postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DATABASE:-postgres}"

pw_migrate create --auto --auto-source="app.database.model" --directory="app/database/migrations" --database="$DB_URI" "$@"
