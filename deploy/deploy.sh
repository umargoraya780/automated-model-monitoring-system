#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# These variables will be passed as arguments (or via GitHub Actions later)
DOCKER_USERNAME=$1
EC2_HOST=$2
EC2_USER=${3:-ubuntu} # Default to ubuntu if not provided

IMAGE_NAME="mlops-inference-api"
TAG="latest"
FULL_IMAGE_PATH="$DOCKER_USERNAME/$IMAGE_NAME:$TAG"

echo "=== Building Docker image ==="
docker build -t $FULL_IMAGE_PATH .

echo "=== Pushing to Docker Hub ==="
docker push $FULL_IMAGE_PATH

echo "=== Deploying to EC2 ==="
# We use SSH to run commands directly on your AWS instance
# FIX: Added '-i mlops-key.pem' so AWS accepts the connection
ssh -i mlops-key.pem -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << EOF
    echo "Pulling latest image..."
    docker pull $FULL_IMAGE_PATH
    
    echo "Stopping existing container (if running)..."
    docker stop mlops-api || true
    docker rm mlops-api || true
    
    echo "Starting new container..."
    # Map container port 8000 to host port 8000
    docker run -d --name mlops-api -p 8000:8000 $FULL_IMAGE_PATH
    
    echo "Deployment successful!"
EOF