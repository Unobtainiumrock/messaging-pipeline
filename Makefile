.PHONY: setup test lint update-readme clean docker-build docker-run docker-test docker-shell docker-run-dev docker-run-prod docker-build-dev docker-build-prod docker-logs docker-stop ec2-deploy

# Setup development environment
setup:
	pip install -r requirements.txt
	pre-commit install

# Run tests
test:
	pytest

# Lint code
lint:
	flake8 .
	black --check .

# Update README structure
update-readme:
	python scripts/update_readme_structure.py

# Clean temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".hypothesis" -exec rm -rf {} +

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-test:
	docker-compose run --rm app pytest

docker-shell:
	docker-compose run --rm app /bin/bash

docker-run-dev:
	docker-compose -f docker-compose.dev.yml up

docker-run-prod:
	docker-compose -f docker-compose.prod.yml up -d

docker-build-dev:
	docker-compose -f docker-compose.dev.yml build

docker-build-prod:
	docker-compose -f docker-compose.prod.yml build

docker-logs:
	docker-compose -f docker-compose.prod.yml logs -f

docker-stop:
	docker-compose -f docker-compose.prod.yml down

ec2-deploy:
	@echo "Deploying to EC2..."
	scp -i $(EC2_KEY) -r ./* ec2-user@$(EC2_IP):/home/ec2-user/comm-centralizer/
	ssh -i $(EC2_KEY) ec2-user@$(EC2_IP) "cd /home/ec2-user/comm-centralizer && ./setup.sh && make docker-run-prod"

help:
	@echo "Available commands:"
	@echo "  setup          - Set up development environment"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting tools"
	@echo "  update-readme  - Update README with project structure"
	@echo "  clean          - Clean temporary files"
	@echo "  docker-build   - Build Docker container"
	@echo "  docker-run     - Run application in Docker"
	@echo "  docker-test    - Run tests in Docker"
	@echo "  docker-shell   - Open a shell in the Docker container"
	@echo "  docker-run-dev - Run development environment in Docker"
	@echo "  docker-run-prod - Run production environment in Docker"
	@echo "  docker-build-dev - Build development environment Docker container"
	@echo "  docker-build-prod - Build production environment Docker container"
	@echo "  docker-logs - View Docker container logs"
	@echo "  docker-stop - Stop Docker container"
	@echo "  ec2-deploy - Deploy to EC2" 