#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if EC2 instance IP is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: EC2 instance IP address is required.${NC}"
    echo -e "Usage: $0 <ec2-ip-address> <path-to-ssh-key>"
    exit 1
fi

# Check if SSH key is provided
if [ -z "$2" ]; then
    echo -e "${RED}Error: Path to SSH key is required.${NC}"
    echo -e "Usage: $0 <ec2-ip-address> <path-to-ssh-key>"
    exit 1
fi

EC2_IP=$1
SSH_KEY=$2
ENVIRONMENT=${3:-"production"}  # Default to production if not specified
DOCKER_TAG=${4:-"latest"}       # Default to latest if not specified

echo -e "${YELLOW}Deploying to $ENVIRONMENT environment at $EC2_IP...${NC}"

# Create a production-ready .env file
echo -e "${YELLOW}Creating $ENVIRONMENT .env file...${NC}"
cp .env.example .env.$ENVIRONMENT

# Sync project files to EC2
echo -e "${YELLOW}Copying project files to EC2...${NC}"
rsync -avz --exclude '.git' --exclude 'venv' --exclude 'node_modules' \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    ./ ec2-user@$EC2_IP:/home/ec2-user/comm-centralizer/

# SSH into EC2 and set up the project
echo -e "${YELLOW}Setting up project on EC2...${NC}"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ec2-user@$EC2_IP "cd /home/ec2-user/comm-centralizer && \
    mv .env.$ENVIRONMENT .env && \
    chmod +x setup.sh && ./setup.sh && \
    # Pull the specific Docker image if specified
    [ "$DOCKER_TAG" != "latest" ] && docker pull ghcr.io/your-username/comm-centralizer:$DOCKER_TAG || true && \
    make docker-build-prod && \
    make docker-run-prod"

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "Your application is now running at: http://$EC2_IP:8000"
echo -e "To view logs: ssh -i $SSH_KEY ec2-user@$EC2_IP 'cd /home/ec2-user/comm-centralizer && make docker-logs'"
echo -e "To stop the application: ssh -i $SSH_KEY ec2-user@$EC2_IP 'cd /home/ec2-user/comm-centralizer && make docker-stop'"
