# Communication Centralizer

An automated system to centralize communications from multiple platforms (Email, LinkedIn, Handshake, etc.) into a single Google Sheet and automate scheduling using NLP.

## Features

- Captures messages from multiple platforms:
  - Emails (Gmail/Outlook)
  - LinkedIn DMs (via PhantomBuster)
  - Handshake Messages (via web automation)
  - Slack, Discord, and other platforms
- Centralizes all data in Google Sheets
- Uses spaCy with LLM integration to identify interview requests
- Automatically schedules interviews via Calendly and Google Calendar

## Requirements

- Docker and Docker Compose (installed automatically by `setup.sh`)
- Google Cloud Platform account for API access
- PhantomBuster account for LinkedIn automation
- Calendly account
- AWS account (for CI/CD deployment)

## Setup

1. **Clone this repository**
2. **Run the setup script: `./setup.sh`**
   - Installs Docker and Docker Compose if needed
   - Sets up necessary directories and configuration files
   - Builds the Docker images
   - Creates a Python virtual environment with UV
3. **Configure credentials** in `config/credentials/` following the README there
4. **Set environment variables** in `.env` (copy from `.env.example`)
5. **Log out and log back in** if prompted (required for Docker permissions)
6. **Start the application in development mode**:

   ```bash
   make docker-run-dev
   ```

## Credentials Setup

The application requires various API credentials:

1. **Google Sheets**: Create a service account and place JSON credentials in `config/credentials/google_credentials.json`
2. **Gmail/Email**: Create an App Password if using 2FA (see [Gmail documentation](https://support.google.com/accounts/answer/185833))
3. **Slack/Discord**: Create bot tokens with appropriate permissions
4. **Calendly/PhantomBuster**: Generate API keys from respective platforms

Run credential tests after setup to verify your configuration.

## CI/CD Pipeline

This project includes a complete CI/CD pipeline using GitHub Actions for automated testing, building, and deployment:

### GitHub Actions Workflow

The pipeline includes the following stages:

- **Test**: Runs linting, type checking, and unit tests for both Python and JavaScript/TypeScript
- **Build**: Builds and pushes Docker images to GitHub Container Registry
- **Deploy-Staging**: Automatically deploys to the staging environment when code is pushed to the `develop` branch
- **Deploy-Production**: Automatically deploys to production when code is pushed to the `main` branch or manually triggered

### Required Secrets

To use the CI/CD pipeline, set up these secrets in your GitHub repository:

1. `AWS_ACCESS_KEY_ID`: AWS access key with EC2 permissions
2. `AWS_SECRET_ACCESS_KEY`: AWS secret key
3. `AWS_REGION`: AWS region (e.g., us-east-1)
4. `STAGING_EC2_IP`: IP address of your staging EC2 instance
5. `PRODUCTION_EC2_IP`: IP address of your production EC2 instance
6. `EC2_SSH_PRIVATE_KEY`: SSH private key for EC2 access

### Environment Configuration

The project uses environment-specific configuration files:

- `.env.staging`: Configuration for the staging environment
- `.env.production`: Configuration for the production environment

### Manual Deployment

To manually trigger a deployment to production:

1. Go to GitHub Actions
2. Select the "CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Select "true" for the "Deploy to production" option
5. Click "Run workflow"

### Version Tagging

To create a new version tag:

1. Go to GitHub Actions
2. Select the "Tag Version" workflow
3. Click "Run workflow"
4. Enter the version (e.g., "v1.0.0")
5. Click "Run workflow"

## Project Automation with Makefile

This project uses a Makefile to standardize workflows and automate common tasks:

- **Environment Management**: Setup development environment with proper dependencies
- **Application Lifecycle**: Start, stop, and monitor services in different environments
- **Testing & Quality**: Run tests, linting, and code quality checks
- **Dependency Management**: Add and manage Python dependencies with UV
- **CI/CD Operations**: Execute CI/CD tasks for testing, building, and deployment
- **Deployment**: Automate deployment to staging and production environments

Run `make help` to see all available commands with descriptions.

## Docker Operations

```bash
# Start development environment
make docker-run-dev

# Start production environment
make docker-run-prod

# Stop containers
make docker-stop

# View logs
make docker-logs

# Rebuild containers (after changing Dockerfile)
make docker-build
```

## CI/CD Operations

```bash
# Run all CI tests
make ci-test

# Build Docker image for CI
make ci-build

# Deploy to staging
make ci-deploy-staging

# Deploy to production
make ci-deploy-production
```

## Dependency Management

This project uses UV for Python dependency management. Dependencies are defined in `pyproject.toml`.

```bash
# Add a regular dependency
make uv-add package=package-name

# Add a development dependency
make uv-add-dev package=package-name
```

## Testing

The project includes a comprehensive test suite organized into credential verification and component tests.

### Running Tests

```bash
# Run all tests (credentials and components)
make test

# Run tests in Docker environment
make docker-test
```

### Test Organization

- `tests/credentials/` - Tests for API credentials and service connections
- `tests/component/` - Functional tests for code components

### Adding New Tests

**Credential Tests**

1. Create a file in `tests/credentials/` named `test_<service>_credentials.py`
2. Implement a function named `test_<service>_credentials()` that returns `True` or `False`
3. Add the service to the list in `tests/run_credential_tests.py` if needed

**Component Tests**

1. Add test classes or functions to files in `tests/component/`
2. Follow pytest naming conventions for automatic discovery

## VS Code Configuration

If you're using VS Code, set up the correct Python interpreter to avoid import resolution issues:

1. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Type "Python: Select Interpreter"
3. Select the "**Pyenv**" option (e.g., `Python 3.12.3 64-bit ('3.12.3') ~/.pyenv/versions/3.12.3/bin/python`)
4. **Important**: Make sure to select the "Pyenv" option specifically, not the similar "Recommended" or "Workspace" options
5. Restart VS Code or reload the window

This ensures that VS Code correctly resolves all imports, including the `crontab` module used in scheduling scripts.

## Development Commands

The following commands are available to help with development tasks:

### JavaScript/TypeScript Commands

- `npm run format`: Formats all JavaScript, TypeScript, and JSON files using Prettier
- `npm run tsc`: Runs TypeScript compiler to check types without emitting output files
- `npm run lint`: Runs ESLint to find and fix issues in JavaScript/TypeScript files

### Python Commands

- `black .`: Formats all Python files according to Black coding style
- `flake8`: Checks Python files for style issues and potential bugs
- `pre-commit run --all-files`: Runs all pre-commit hooks on all files

### Development Workflow

- `make dev`: Starts the development environment (if Makefile is configured)
- `./setup.sh`: Sets up the project for first-time use
- `git commit`: Automatically runs pre-commit hooks to format and lint code

## Project Structure

```bash
comm-centralizer/
├── scripts/
│   ├── .dir_structure_cache.json   # Cache file storing directory structure
│   ├── deploy_to_ec2.sh            # Script for deploying to EC2 instance
│   ├── directory_printer.py        # Python script for printing directory structure
│   ├── ec2_security_setup.sh       # Script for setting up security on EC2 instance
│   ├── schedule_job.py             # Script for scheduling jobs
│   ├── setup_env_credentials.sh    # Script for setting up environment credentials
│   ├── setup_monitoring.sh         # Script for setting up monitoring
│   └── update_readme_structure.py  # Python script for updating README structure
├── terraform/
│   └── main.tf                     # Terraform main configuration file
├── config/
│   ├── config.py                   # Configuration file
│   └── credentials/
│       ├── .gitkeep                # Git placeholder file
│       ├── README.md               # Credentials README
│       └── google_credentials.json  # Google API credentials
├── src/
│   ├── main.py                     # Main Python script
│   ├── automation/
│   │   └── puppeteer_scripts/
│   │       ├── handshake.js        # Puppeteer script for handshake
│   │       ├── index.ts            # Puppeteer script index
│   │       └── utils.js            # Puppeteer utility functions
│   │   └── selenium_scripts/
│   │       └── utils.py            # Selenium utility functions
│   ├── config/
│   │   └── environment.py          # Environment configuration
│   ├── connectors/
│   │   ├── discord_connector.py    # Discord API connector
│   │   ├── email_connector.py      # Email API connector
│   │   ├── handshake_connector.py  # Handshake API connector
│   │   ├── linkedin_connector.py   # LinkedIn API connector
│   │   └── slack_connector.py      # Slack API connector
│   ├── processing/
│   │   ├── message_classifier.py   # Message classifier
│   │   └── nlp_processor.py        # NLP processor
│   ├── scheduling/
│   │   ├── calendly.py             # Calendly scheduling integration
│   │   └── google_calendar.py      # Google Calendar scheduling integration
│   ├── storage/
│   │   └── google_sheets.py        # Google Sheets storage integration
├── tests/
│   ├── run_all_tests.py            # Script for running all tests
│   ├── run_component_tests.py      # Script for running component tests
│   ├── run_credential_tests.py     # Script for running credential tests
│   ├── component/
│   │   ├── test_automation.py      # Automation component tests
│   │   ├── test_connectors.py      # Connectors component tests
│   │   ├── test_processing.py      # Processing component tests
│   │   ├── test_scheduling.py      # Scheduling component tests
│   │   └── test_storage.py         # Storage component tests
│   └── credentials/
│       ├── README.md               # Credentials README
│       ├── test_calendly_credentials.py  # Calendly credentials test
│       ├── test_discord_credentials.py   # Discord credentials test
│       ├── test_email_credentials.py     # Email credentials test
│       ├── test_openai_credentials.py    # OpenAI credentials test
│       ├── test_phantombuster_credentials.py  # Phantombuster credentials test
│       ├── test_sheets_credentials.py     # Google Sheets credentials test
│       └── test_slack_credentials.py      # Slack credentials test
├── .eslintrc.js                    # ESLint configuration
├── .pre-commit-config.yaml         # Pre-commit configuration
├── Dockerfile                      # Dockerfile for development
├── Dockerfile.prod                 # Dockerfile for production
├── Makefile                        # Makefile for project
├── README.md                       # Project documentation
├── TODOPROMPTS.txt                 # TODO prompts file
├── comm_centralizer.log            # Project log file
├── docker-compose.dev.yml          # Docker Compose file for development
├── docker-compose.prod.yml         # Docker Compose file for production
├── docker-compose.yml              # Docker Compose file
├── package.json                    # Node.js package file
├── pyproject.toml                  # Python project configuration
├── setup.sh                        # Setup script
└── tsconfig.json                   # TypeScript configuration
```

## Validating the CI/CD Pipeline

To ensure your CI/CD pipeline is correctly configured and working properly, follow these validation steps:

### 1. Local Environment Setup

```bash
# Verify your scripts have proper permissions
chmod +x scripts/deploy_to_ec2.sh
chmod +x scripts/setup_env_credentials.sh
chmod +x scripts/setup_monitoring.sh

# Test your CI commands locally
make ci-test
```

### 2. GitHub Repository Configuration

1. **Set Up Required Secrets**:

   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add all required secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `AWS_REGION`
     - `STAGING_EC2_IP`
     - `PRODUCTION_EC2_IP`
     - `EC2_SSH_PRIVATE_KEY`

2. **Configure Branch Protection**:
   - Go to Settings → Branches → Add rule
   - Protect your `main` and `develop` branches
   - Require status checks to pass before merging

### 3. Test the Pipeline

1. Create a test branch:

   ```bash
   git checkout -b test-ci-pipeline
   ```

2. Make a small change (e.g., update a comment)

3. Push the branch and create a PR to `develop`:

   ```bash
   git push origin test-ci-pipeline
   ```

4. Verify each stage in GitHub Actions:
   - **Test**: All tests, linting, and type checks pass
   - **Build**: Docker image builds and pushes to GitHub Container Registry
   - **Deploy-Staging**: (After merging to `develop`) Application deploys to staging
   - **Deploy-Production**: (After merging to `main` or manual trigger) Application deploys to production

### 4. Verify Deployment

```bash
# Check staging deployment
ssh -i your-key.pem ec2-user@your-staging-ip 'cd /home/ec2-user/comm-centralizer && docker ps'

# Check application logs
ssh -i your-key.pem ec2-user@your-staging-ip 'cd /home/ec2-user/comm-centralizer && make docker-logs'

# Verify monitoring setup
ssh -i your-key.pem ec2-user@your-staging-ip 'sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status'
```

### 5. Test Rollback Procedure

If you need to roll back to a previous version:

```bash
# Deploy previous version
make ci-deploy-production DOCKER_TAG=previous-version-tag
```

## Infrastructure as Code with Terraform

This project uses Terraform to manage cloud infrastructure in a consistent, version-controlled way.

### What is Terraform?

Terraform is an Infrastructure as Code (IaC) tool that allows you to define and provision infrastructure using declarative configuration files. Instead of manually creating servers through the AWS console, you define your infrastructure in code.

### Benefits for This Project

- **Consistency**: Identical environments for staging and production
- **Version Control**: Infrastructure changes are tracked in Git
- **Automation**: Reduces human error in infrastructure setup
- **Documentation**: Self-documenting infrastructure
- **Disaster Recovery**: Quickly recreate infrastructure if needed

### Using Terraform

1. **Create variables file** (`terraform/variables.tf`):

```hcl
variable "aws_region" {
  description = "AWS region to deploy to"
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (staging or production)"
  default     = "staging"
}

variable "ami_id" {
  description = "Amazon Machine Image ID"
  default     = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 AMI
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = "Name of the key pair for SSH access"
}
```

2. **Initialize Terraform**:

```bash
cd terraform
terraform init
```

3. **Create infrastructure plan**:

```bash
terraform plan -var="key_pair_name=your-key-pair-name"
```

4. **Apply the infrastructure**:

```bash
terraform apply -var="key_pair_name=your-key-pair-name"
```

5. **Destroy infrastructure when no longer needed**:

```bash
terraform destroy -var="key_pair_name=your-key-pair-name"
```

### Terraform Makefile Commands

```bash
# Initialize Terraform
make terraform-init

# Plan infrastructure changes
make terraform-plan ENVIRONMENT=staging KEY_PAIR_NAME=your-key-pair

# Apply infrastructure changes
make terraform-apply ENVIRONMENT=production KEY_PAIR_NAME=your-key-pair
```

The Terraform configuration in this project creates:

- EC2 instances for application hosting
- Security groups with proper port configurations
- Initial server setup with Docker and other requirements
