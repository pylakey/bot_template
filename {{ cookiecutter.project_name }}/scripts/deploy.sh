#!/usr/bin/env sh
set -e
docker compose up -d --build --remove-orphans "$@"