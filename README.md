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

## Setup

### Docker-based Setup (Recommended)

1. Clone this repository
2. Run the setup script: `./setup.sh`
   - This will install Docker and Docker Compose if needed
   - Set up necessary directories and configuration files
   - Build the Docker images
3. Configure credentials in `config/credentials/` following the README there
4. Set environment variables in `.env` (copy from `.env.example`)
5. Log out and log back in if prompted (required for Docker permissions)
6. Start the application in development mode: `make docker-run-dev`

### Alternative: Manual Setup

If you prefer not to use Docker:

1. Clone this repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install Node.js dependencies: `npm install`
4. Configure credentials in `config/credentials/`
5. Set environment variables in `.env` (copy from `.env.example`)
6. Run the main application: `python src/main.py`

## Docker Commands

The project includes a Makefile with useful commands for Docker-based development:

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

# Restart containers
make docker-restart

# List all available commands
make help
```

## VS Code Configuration

If you're using VS Code, set up the correct Python interpreter to avoid import resolution issues:

1. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Type "Python: Select Interpreter"
3. Select the "**Pyenv**" option (e.g., `Python 3.12.3 64-bit ('3.12.3') ~/.pyenv/versions/3.12.3/bin/python`)
4. **Important**: Make sure to select the "Pyenv" option specifically, not the similar "Recommended" or "Workspace" options
5. Restart VS Code or reload the window

This ensures that VS Code correctly resolves all imports, including the `crontab` module used in scheduling scripts.

## Requirements

- Docker and Docker Compose (installed automatically by setup.sh)
- OR if not using Docker:
  - Python 3.9+
  - Node.js 14+ (for Puppeteer scripts)
  - Puppeteer 24.3.1+ (earlier versions have security vulnerabilities)
- Google Cloud Platform account for API access
- PhantomBuster account for LinkedIn automation
- Calendly account

## Testing

The project includes a comprehensive test suite organized into credential verification and component tests.

### Running Tests

```bash
# Run all tests (credentials and components)
python tests/run_all_tests.py

# Run only credential verification tests
python tests/run_credential_tests.py

# Run only component tests
python tests/run_component_tests.py

# Run an individual credential test
python tests/credentials/test_sheets_credentials.py

# When using Docker
make docker-test
```

### Test Organization

- `tests/credentials/` - Tests for API credentials and service connections
- `tests/component/` - Functional tests for code components

### Adding New Tests

#### Credential Tests

1. Create a file in `tests/credentials/` named `test_<service>_credentials.py`
2. Implement a function named `test_<service>_credentials()` that returns `True` or `False`
3. Add the service to the list in `tests/run_credential_tests.py` if needed

#### Component Tests

1. Add test classes or functions to files in `tests/component/`
2. Follow pytest naming conventions for automatic discovery

## Credentials Setup

The application requires various API credentials:

1. **Google Sheets**: Create a service account and place JSON credentials in `config/credentials/google_credentials.json`
2. **Gmail/Email**: Create an App Password if using 2FA (see [Gmail documentation](https://support.google.com/accounts/answer/185833))
3. **Slack/Discord**: Create bot tokens with appropriate permissions
4. **Calendly/PhantomBuster**: Generate API keys from respective platforms

Run credential tests after setup to verify your configuration.

## Project Structure

```bash
comm-centralizer/
├── scripts/
│   ├── deploy_to_ec2.sh                # Script to deploy project to EC2 instance
│   ├── directory_printer.py            # Script to print directory structure
│   ├── ec2_security_setup.sh           # Script to set up security on EC2 instance
│   ├── schedule_job.py                 # Script to schedule jobs
│   ├── update_readme_structure.py      # Script to update README structure
├── config/
│   ├── config.py                       # Configuration file for project
│   ├── credentials/
│   │   ├── .gitkeep                    # Placeholder file for credentials directory
│   │   ├── README.md                   # Information about credentials directory
│   │   ├── google_credentials.json      # Google API credentials file
├── src/
│   ├── main.py                         # Main entry point of the project
│   ├── automation/
│   │   ├── selenium_utils.py           # Utility functions for Selenium automation
│   │   ├── puppeteer_scripts/
│   │   │   ├── handshake.js            # Puppeteer script for handshake process
│   │   │   ├── utils.js                # Utility functions for Puppeteer scripts
│   ├── config/
│   │   ├── environment.py              # Environment configuration file
│   ├── connectors/
│   │   ├── discord_connector.py        # Connector for Discord platform
│   │   ├── email_connector.py          # Connector for email platforms
│   │   ├── handshake_connector.py      # Connector for handshake process
│   │   ├── linkedin_connector.py       # Connector for LinkedIn platform
│   │   ├── slack_connector.py          # Connector for Slack platform
│   ├── processing/
│   │   ├── message_classifier.py       # Message classification module
│   │   ├── nlp_processor.py            # Natural Language Processing module
│   ├── scheduling/
│   │   ├── calendly.py                 # Calendly scheduling integration
│   │   ├── google_calendar.py          # Google Calendar scheduling integration
│   ├── storage/
│   │   ├── google_sheets.py            # Google Sheets storage integration
├── tests/
│   ├── run_all_tests.py                # Script to run all tests
│   ├── run_component_tests.py          # Script to run component tests
│   ├── run_credential_tests.py         # Script to run credential tests
│   ├── component/
│   │   ├── test_automation.py          # Automated tests for automation module
│   │   ├── test_connectors.py          # Automated tests for connectors module
│   │   ├── test_processing.py          # Automated tests for processing module
│   │   ├── test_scheduling.py          # Automated tests for scheduling module
│   │   ├── test_storage.py             # Automated tests for storage module
│   ├── credentials/
│   │   ├── README.md                   # Information about credentials tests
│   │   ├── test_calendly_credentials.py # Test script for Calendly credentials
│   │   ├── test_discord_credentials.py  # Test script for Discord credentials
│   │   ├── test_email_credentials.py    # Test script for email credentials
│   │   ├── test_openai_credentials.py   # Test script for OpenAI credentials
│   │   ├── test_phantombuster_credentials.py # Test script for Phantombuster credentials
│   │   ├── test_sheets_credentials.py   # Test script for Google Sheets credentials
│   │   ├── test_slack_credentials.py    # Test script for Slack credentials
├── .dockerignore                       # Docker ignore file
├── .pre-commit-config.yaml             # Pre-commit configuration file
├── Dockerfile                          # Dockerfile for project
├── Dockerfile.improvements             # Improved Dockerfile for project
├── Makefile                            # Makefile for project
├── README.md                           # Project documentation
├── TODOPROMPTS.txt                     # TODO prompts for project
├── comm_centralizer.log                # Log file for project
├── docker-compose.dev.yml              # Docker Compose file for development environment
├── docker-compose.prod.yml             # Docker Compose file for production environment
├── docker-compose.yml                  # Docker Compose file
├── package.json                        # Node.js package file
├── requirements.txt                    # Python requirements file
├── scratch.sh                          # Script for testing purposes
└── setup.sh                            # Setup script for project
```