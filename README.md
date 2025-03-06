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

## Project Automation with Makefile

This project uses a Makefile to standardize workflows and automate common tasks:

- **Environment Management**: Setup development environment with proper dependencies
- **Application Lifecycle**: Start, stop, and monitor services in different environments
- **Testing & Quality**: Run tests, linting, and code quality checks
- **Dependency Management**: Add and manage Python dependencies with UV
- **Deployment**: Automate deployment to production environments

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
│   ├── .dir_structure_cache.json     # Cache file for directory structure
│   ├── deploy_to_ec2.sh              # Script for deploying to EC2
│   ├── directory_printer.py          # Script for printing directory structure
│   ├── ec2_security_setup.sh         # Script for setting up EC2 security
│   ├── schedule_job.py               # Script for scheduling jobs
│   ├── update_readme_structure.py    # Script for updating README structure
├── config/
│   ├── config.py                     # Configuration file
│   ├── credentials/
│   │   ├── .gitkeep                  # Placeholder file for git
│   │   ├── README.md                 # Credentials directory documentation
│   │   ├── google_credentials.json    # Google API credentials
├── src/
│   ├── main.py                       # Main script
│   ├── automation/
│   │   ├── puppeteer_scripts/
│   │   │   ├── handshake.js          # Puppeteer script for handshake
│   │   │   ├── index.ts              # Puppeteer script index
│   │   │   ├── utils.js              # Puppeteer utility functions
│   │   ├── selenium_scripts/
│   │   │   ├── utils.py              # Selenium utility functions
│   ├── config/
│   │   ├── environment.py            # Environment configuration
│   ├── connectors/
│   │   ├── discord_connector.py      # Discord API connector
│   │   ├── email_connector.py        # Email API connector
│   │   ├── handshake_connector.py    # Handshake API connector
│   │   ├── linkedin_connector.py     # LinkedIn API connector
│   │   ├── slack_connector.py        # Slack API connector
│   ├── processing/
│   │   ├── message_classifier.py     # Message classifier
│   │   ├── nlp_processor.py          # NLP processor
│   ├── scheduling/
│   │   ├── calendly.py               # Calendly scheduling integration
│   │   ├── google_calendar.py        # Google Calendar scheduling integration
│   ├── storage/
│   │   ├── google_sheets.py          # Google Sheets storage integration
├── tests/
│   ├── run_all_tests.py              # Script to run all tests
│   ├── run_component_tests.py        # Script to run component tests
│   ├── run_credential_tests.py       # Script to run credential tests
│   ├── component/
│   │   ├── test_automation.py        # Automation component tests
│   │   ├── test_connectors.py        # Connectors component tests
│   │   ├── test_processing.py        # Processing component tests
│   │   ├── test_scheduling.py        # Scheduling component tests
│   │   ├── test_storage.py           # Storage component tests
│   ├── credentials/
│   │   ├── README.md                 # Credentials tests documentation
│   │   ├── test_calendly_credentials.py   # Calendly credentials test
│   │   ├── test_discord_credentials.py    # Discord credentials test
│   │   ├── test_email_credentials.py      # Email credentials test
│   │   ├── test_openai_credentials.py     # OpenAI credentials test
│   │   ├── test_phantombuster_credentials.py   # Phantombuster credentials test
│   │   ├── test_sheets_credentials.py    # Google Sheets credentials test
│   │   ├── test_slack_credentials.py     # Slack credentials test
├── .dockerignore                     # Docker ignore file
├── .eslintrc.js                      # ESLint configuration
├── .pre-commit-config.yaml           # Pre-commit configuration
├── Dockerfile                        # Dockerfile for containerization
├── Makefile                          # Makefile for project tasks
├── README.md                         # Project documentation
├── TODOPROMPTS.txt                   # TODO prompts file
├── comm_centralizer.log              # Project log file
├── docker-compose.dev.yml            # Docker compose file for development
├── docker-compose.prod.yml           # Docker compose file for production
├── docker-compose.yml                # Docker compose file
├── package.json                      # Node.js package configuration
├── pyproject.toml                    # Python project configuration
├── requirements.txt                  # Python requirements file
├── setup.sh                          # Setup script
└── tsconfig.json                     # TypeScript configuration
```
