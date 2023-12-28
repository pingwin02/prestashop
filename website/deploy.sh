#!/bin/bash

IMAGE_NAME="pingwin02/prestashop:latest"
COMPOSE_URL="https://raw.githubusercontent.com/pingwin02/prestashop/main/website/docker-compose-prod.yml"
STACK_NAME="BE_186044"

echo "Pulling docker image..."
docker pull $IMAGE_NAME

echo "Downloading docker-compose.yml..."
wget $COMPOSE_URL -O docker-compose.yml

echo "Deploying the app..."
docker stack deploy -c docker-compose.yml $STACK_NAME --with-registry-auth