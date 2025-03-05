#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up EC2 security...${NC}"

# Ensure Docker socket permissions are correct
sudo usermod -aG docker ec2-user

# Set appropriate permissions for credential files
sudo chmod 600 /home/ec2-user/comm-centralizer/config/credentials/*
sudo chown ec2-user:ec2-user /home/ec2-user/comm-centralizer/config/credentials/*

# Set appropriate permissions for .env file
sudo chmod 600 /home/ec2-user/comm-centralizer/.env
sudo chown ec2-user:ec2-user /home/ec2-user/comm-centralizer/.env

# Set up automatic updates for security patches
sudo yum update -y
sudo yum install -y yum-cron
sudo sed -i 's/apply_updates = no/apply_updates = yes/' /etc/yum/yum-cron.conf
sudo systemctl enable yum-cron
sudo systemctl start yum-cron

echo -e "${GREEN}EC2 security setup complete!${NC}" 