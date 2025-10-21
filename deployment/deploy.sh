#!/bin/bash
set -e

APP_NAME="taskapp"
APP_DIR="/opt/taskapp"
CONTAINER_NAME="${APP_NAME}_production"
IMAGE_TAG="${1:-latest}"
APP_PORT="8000"

echo "=========================================="
echo "Deploying Task Management Application"
echo "=========================================="

if [ -z "$1" ]; then
    echo "No image tag specified, using 'latest'"
    IMAGE_TAG="latest"
fi

echo "Image: ${IMAGE_TAG}"
echo "Container: ${CONTAINER_NAME}"
echo ""

cd $APP_DIR

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found in $APP_DIR"
    echo "Please create .env file with required configuration"
    exit 1
fi

echo "Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $APP_PORT:8000 \
    --env-file $APP_DIR/.env \
    $IMAGE_TAG

sleep 5

echo "Checking container status..."
if docker ps | grep -q $CONTAINER_NAME; then
    echo "Container is running!"

    echo ""
    echo "Running health check..."
    if curl -f http://localhost:$APP_PORT/ >/dev/null 2>&1; then
        echo "Health check passed!"
    else
        echo "WARNING: Health check failed, but container is running"
        echo "Check logs with: docker logs $CONTAINER_NAME"
    fi

    echo ""
    echo "=========================================="
    echo "Deployment successful!"
    echo "=========================================="
    echo "Container: $CONTAINER_NAME"
    echo "Port: $APP_PORT"
    echo ""
    echo "View logs: docker logs -f $CONTAINER_NAME"
    echo "Stop app: docker stop $CONTAINER_NAME"
    echo "Restart app: docker restart $CONTAINER_NAME"
else
    echo "ERROR: Container failed to start"
    echo "Check logs with: docker logs $CONTAINER_NAME"
    exit 1
fi
