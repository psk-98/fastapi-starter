#!/bin/sh

set -x

echo "installing deps ..."
uv sync

echo "installing email deps ..."
bun install

echo "exporting email templates ..."
bun run email:export

echo "copying .env ..."
cp example.dev.env .env


echo "copying docker compose ..."
cp .docker/docker-compose.dev.yml docker-compose.yml

echo "building docker container ..."
docker compose up -d --build

echo "running migrate script ..."
chmod +x ./scripts/migrate.sh
./scripts/migrate.sh
