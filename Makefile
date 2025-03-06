.PHONY: setup test lint update-readme clean docker-build docker-run docker-test docker-shell docker-run-dev docker-run-prod docker-build-dev docker-build-prod docker-logs docker-stop ec2-deploy uv-add uv-add-dev ci-test ci-build ci-deploy-staging ci-deploy-production

# Setup development environment
setup:
	./setup.sh

# Setup Python environment only (without Docker)
setup-python:
	uv venv
	source .venv/bin/activate && uv pip install --editable ".[dev]"
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
	rm -rf .venv .uv

# UV dependency management
uv-add:
	source .venv/bin/activate && uv pip add $(package) -e "."

uv-add-dev:
	source .venv/bin/activate && uv pip add $(package) -e ".[dev]"

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

# CI/CD commands
ci-test:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check .
	pytest tests/component
	npm run tsc
	npm run lint

ci-build:
	docker build -t ghcr.io/$(shell git config --get remote.origin.url | cut -d: -f2 | sed 's/\.git//'):$(shell git rev-parse --short HEAD) .

ci-deploy-staging:
	./scripts/deploy_to_ec2.sh $(STAGING_EC2_IP) $(SSH_KEY_PATH) staging $(shell git rev-parse --short HEAD)

ci-deploy-production:
	./scripts/deploy_to_ec2.sh $(PRODUCTION_EC2_IP) $(SSH_KEY_PATH) production $(shell git rev-parse --short HEAD)

help:
	@echo "Available commands:"
	@echo "  setup          - Set up complete development environment (Docker + Python)"
	@echo "  setup-python   - Set up Python environment only with UV"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting tools"
	@echo "  update-readme  - Update README with project structure"
	@echo "  clean          - Clean temporary files"
	@echo "  uv-add         - Add a package with UV (usage: make uv-add package=packagename)"
	@echo "  uv-add-dev     - Add a dev package with UV (usage: make uv-add-dev package=packagename)"
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
	@echo "  ci-test      - Run CI/CD tests"
	@echo "  ci-build     - Build Docker image for CI/CD"
	@echo "  ci-deploy-staging - Deploy to staging environment"
	@echo "  ci-deploy-production - Deploy to production environment"
