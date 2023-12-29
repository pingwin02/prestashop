#!/bin/bash

IMAGE_NAME="ryslek/BE_186044_prestashop:1.0"
COMPOSE_URL="https://raw.githubusercontent.com/pingwin02/prestashop/Add-prestashop-caching/website/docker-compose-prod.yml"
INIT_URL="https://raw.githubusercontent.com/pingwin02/prestashop/main/website/init_script.sh"
STACK_NAME="BE_186044"

echo "Pulling docker image..."
docker pull $IMAGE_NAME

echo "Downloading docker-compose.yml..."
wget $COMPOSE_URL -O docker-compose.yml

echo "Downloading init_script.sh..."
wget $INIT_URL

echo "Deploying the app..."
docker stack deploy -c docker-compose.yml $STACK_NAME --with-registry-auth