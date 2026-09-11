#!/usr/bin/env bash
set -e

if [ ! -f .env ]; then
    cp .env.example .env
    echo "created .env from .env.example"
fi

docker compose up --build -d

echo ""
echo "api is running on http://localhost:8000"
echo "demo staff login: staff@example.com / Staff@123"
echo "logs: docker compose logs -f web"
