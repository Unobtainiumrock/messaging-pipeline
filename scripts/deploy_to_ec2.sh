#!/bin/bash
# Enhanced deployment script with versioning and rollback support

set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if EC2 instance IP is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: EC2 instance IP address is required.${NC}"
    echo -e "Usage: $0 <ec2-ip-address> <environment> <version> [action]"
    exit 1
fi

# Check if environment is provided
if [ -z "$2" ]; then
    echo -e "${RED}Error: Environment is required.${NC}"
    echo -e "Usage: $0 <ec2-ip-address> <environment> <version> [action]"
    exit 1
fi

# Check if version is provided
if [ -z "$3" ]; then
    echo -e "${RED}Error: Version is required.${NC}"
    echo -e "Usage: $0 <ec2-ip-address> <environment> <version> [action]"
    exit 1
fi

EC2_IP=$1
ENVIRONMENT=$2
VERSION=$3
ACTION=${4:-deploy}  # default action is deploy, can be "rollback"

SSH_OPTIONS="-o StrictHostKeyChecking=no"

echo "=== Deployment to $ENVIRONMENT ==="
echo "Target: $EC2_IP"
echo "Version: $VERSION"
echo "Action: $ACTION"

if [ "$ACTION" == "rollback" ]; then
  echo "Performing rollback to previous version..."

  # SSH into the server and perform rollback
  ssh $SSH_OPTIONS ec2-user@$EC2_IP << EOF
    cd /app
    echo "Stopping current deployment..."
    docker-compose down

    echo "Checking for previous version..."
    if [ -f "docker-compose.previous.yml" ]; then
      echo "Rolling back to previous deployment..."
      mv docker-compose.previous.yml docker-compose.yml
      docker-compose up -d
      echo "Rollback complete!"
    else
      echo "No previous version found, cannot rollback!"
      exit 1
    fi
EOF

  exit $?
fi

# Regular deployment
echo "Performing deployment of version $VERSION..."

# If deploying a new version, first load the Docker image
docker load < image.tar

# SSH into the server and deploy
ssh $SSH_OPTIONS ec2-user@$EC2_IP << EOF
  # Create app directory if it doesn't exist
  mkdir -p /app
  cd /app

  # Save current deployment for rollback if it exists
  if [ -f "docker-compose.yml" ]; then
    echo "Backing up current deployment for potential rollback..."
    cp docker-compose.yml docker-compose.previous.yml
  fi

  # Create deployment tracking file
  echo "$VERSION deployed at $(date)" >> deployment_history.log

  # Stop current containers
  docker-compose down || true

  # Set up new deployment
  cat > docker-compose.yml << 'EOFINNER'
version: '3.8'

services:
  app:
    image: ghcr.io/${GITHUB_REPOSITORY}:${VERSION}
    restart: always
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
    volumes:
      - ./config:/app/config
    ports:
      - "8000:8000"
EOFINNER

  # Pull the new image and start containers
  docker-compose pull
  docker-compose up -d

  # Verify deployment
  echo "Deployment completed, verifying..."
  sleep 10
  if docker-compose ps | grep -q "Up"; then
    echo "Deployment verification: SUCCESS"
  else
    echo "Deployment verification: FAILED"
    echo "Attempting automatic rollback..."
    if [ -f "docker-compose.previous.yml" ]; then
      mv docker-compose.previous.yml docker-compose.yml
      docker-compose up -d
      echo "Rolled back to previous version"
      exit 1
    fi
  fi
EOF

# Set up monitoring
./scripts/setup_monitoring.sh $ENVIRONMENT $VERSION

echo "=== Deployment completed successfully ==="
