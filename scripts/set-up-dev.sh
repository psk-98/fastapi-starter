#!/bin/sh

set -x

echo "installing deps ..."
uv sync

echo "copying .env ..."
cp example.dev.env .env


echo "copying docker compose ..."
cp .docker/docker-compose.dev.yml docker-compose.yml

echo "building docker container ..."
docker compose up -d --build

echo "running migrate script ..."
chmod +x ./scripts/migrate.sh
./scripts/migrate.sh
