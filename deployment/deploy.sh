#!/bin/bash

###############################################################################
# Deployment script for AWS EC2 Production Server
# This script pulls the latest Docker image and restarts the application
###############################################################################

set -e  # Exit on error

# Configuration
DOCKER_IMAGE=${1:-taskapp:latest}
APP_NAME="taskapp"
CONTAINER_NAME="taskapp_production"
ENV_FILE="/opt/taskapp/.env"
NETWORK_NAME="taskapp_network"

echo "========================================="
echo "Starting deployment of ${DOCKER_IMAGE}"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Pull the latest image
echo "Pulling Docker image: ${DOCKER_IMAGE}"
docker pull ${DOCKER_IMAGE}

# Stop and remove existing container
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping existing container..."
    docker stop ${CONTAINER_NAME} || true
    docker rm ${CONTAINER_NAME} || true
fi

# Create network if it doesn't exist
if [ ! "$(docker network ls -q -f name=${NETWORK_NAME})" ]; then
    echo "Creating Docker network: ${NETWORK_NAME}"
    docker network create ${NETWORK_NAME}
fi

# Run the new container
echo "Starting new container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --network ${NETWORK_NAME} \
    --restart unless-stopped \
    -p 5000:5000 \
    --env-file ${ENV_FILE} \
    --health-cmd='python -c "import urllib.request; urllib.request.urlopen(\"http://localhost:5000\")"' \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    ${DOCKER_IMAGE}

# Wait for container to be healthy
echo "Waiting for application to be healthy..."
for i in {1..30}; do
    if [ "$(docker inspect --format='{{.State.Health.Status}}' ${CONTAINER_NAME})" == "healthy" ]; then
        echo "Application is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Warning: Health check timeout"
        docker logs ${CONTAINER_NAME}
    fi
    sleep 2
done

# Clean up old images
echo "Cleaning up old Docker images..."
docker image prune -f

echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo "Container: ${CONTAINER_NAME}"
echo "Image: ${DOCKER_IMAGE}"
echo "Status: $(docker ps -f name=${CONTAINER_NAME} --format '{{.Status}}')"
echo "========================================="

# Show container logs
echo "Recent logs:"
docker logs --tail 20 ${CONTAINER_NAME}
