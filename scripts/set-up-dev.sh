#!/bin/sh

set -x

echo "copying .env ..."
cp example.dev.env .env


echo "copying docker compose ..."
cp .docker/docker-compose.dev.yml docker-compose.yml

docker compose up -d --build
