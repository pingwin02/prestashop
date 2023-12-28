#!/bin/bash

IMAGE_NAME="ryslek/be_186044_prestashop:1.0"
COMPOSE_URL="https://github.com/pingwin02/prestashop/blob/Add-production-config/website/prod/docker-compose.yml"
STACK_NAME="BE_186044"

echo "Pulling docker image..."
docker pull $IMAGE_NAME

echo "Downloading docker-compose.yml..."
wget $COMPOSE_URL

echo "Deploying the app..."
docker stack deploy -c docker-compose.yml $STACK_NAME --with-registry-auth