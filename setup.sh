#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up the Comm Centralizer project...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo -e "${RED}Docker is not installed. Installing Docker...${NC}"
    # Install Docker using convenience script
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed successfully.${NC}"
    echo -e "${YELLOW}IMPORTANT: You need to log out and log back in for Docker group changes to take effect.${NC}"
    DOCKER_INSTALLED=true
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo -e "${YELLOW}Docker Compose is not installed. Installing Docker Compose...${NC}"
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully.${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p screenshots
mkdir -p logs
mkdir -p config/credentials
echo -e "${GREEN}Created directories for screenshots, logs, and credentials.${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your credentials.${NC}"
fi

# Create empty .gitkeep in credentials directory
touch config/credentials/.gitkeep
echo -e "${GREEN}Created .gitkeep file in credentials directory.${NC}"

# Check if user can access Docker
if ! docker info &> /dev/null; then
    echo -e "${RED}Cannot connect to the Docker daemon.${NC}"

    # Check if Docker service exists
    if systemctl list-unit-files | grep -q docker.service; then
        echo -e "${YELLOW}Docker service exists but may not be running. Attempting to start...${NC}"

        # Try to start the Docker service and capture the result
        if sudo systemctl start docker; then
            echo -e "${YELLOW}Waiting for Docker service to initialize...${NC}"
            # Give Docker more time to fully initialize
            sleep 5

            if docker info &> /dev/null; then
                echo -e "${GREEN}Successfully started Docker service.${NC}"
            else
                echo -e "${RED}Docker service started but daemon is not responding.${NC}"
                echo -e "${YELLOW}This might be a permissions issue.${NC}"

                # Check if the current user is in the docker group
                if groups | grep -q docker; then
                    echo -e "${YELLOW}Your user is in the docker group, but you may need to log out and log back in.${NC}"
                    echo -e "${YELLOW}After logging back in, run this setup script again.${NC}"
                else
                    echo -e "${YELLOW}Your user is not in the docker group. Adding you to the group...${NC}"
                    sudo usermod -aG docker $USER
                    echo -e "${GREEN}User added to docker group.${NC}"
                    echo -e "${YELLOW}You need to log out and log back in for this change to take effect.${NC}"
                    echo -e "${YELLOW}After logging back in, run this setup script again.${NC}"
                fi

                echo -e "${YELLOW}Setup partially complete. Docker container was not built.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}Failed to start Docker service.${NC}"
            echo -e "${YELLOW}Try running manually: ${GREEN}sudo systemctl start docker${NC}"
            echo -e "${YELLOW}You might also check the Docker service status: ${GREEN}sudo systemctl status docker${NC}"
            echo -e "${YELLOW}Setup partially complete. Docker container was not built.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Docker service not found or not properly installed.${NC}"
        echo -e "${YELLOW}You might need to reinstall Docker or check your installation.${NC}"

        if [ "${DOCKER_INSTALLED}" = true ]; then
            echo -e "${YELLOW}You need to log out and log back in for Docker group changes to take effect.${NC}"
            echo -e "${YELLOW}After logging back in, run this setup script again to complete the installation.${NC}"
        fi

        echo -e "${YELLOW}Setup partially complete. Docker container was not built.${NC}"
        exit 1
    fi
fi

# Build the Docker container
echo -e "${YELLOW}Building Docker container...${NC}"
docker-compose -f docker-compose.yml build

# Install Python dependencies using UV for local development
echo -e "${YELLOW}Setting up local Python environment with UV...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    pip install uv
fi
echo -e "${GREEN}Creating virtual environment with UV...${NC}"
uv venv
echo -e "${GREEN}Installing dependencies...${NC}"
source .venv/bin/activate || source .venv/Scripts/activate
uv pip install --editable ".[dev]"

# Install pre-commit hooks locally if pre-commit is available
echo -e "${YELLOW}Checking for pre-commit...${NC}"
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}Installing pre-commit hooks...${NC}"
    pre-commit install
else
    echo -e "${YELLOW}Pre-commit not found. Installing...${NC}"
    pip install pre-commit
    echo -e "${GREEN}Installing pre-commit hooks...${NC}"
    pre-commit install
fi

# Install Pytype only (removing MonkeyType)
echo -e "${YELLOW}Installing Pytype...${NC}"
uv pip install pytype==2023.10.17
echo -e "${GREEN}Pytype installed successfully.${NC}"

echo -e "${GREEN}Setup complete!${NC}"
echo -e "--------------------------------------------------"
echo -e "Next steps:"
echo -e "1. Edit .env file with your credentials if you haven't already"
echo -e "2. For advanced configurations, add API credentials to config/credentials/ directory"
echo -e "--------------------------------------------------"
echo -e "To start the development environment, run: ${YELLOW}make docker-run-dev${NC}"
echo -e "To start the production environment, run: ${YELLOW}make docker-run-prod${NC}"
echo -e "For more commands, run: ${YELLOW}make help${NC}"

# Make the script executable
chmod +x setup.sh
