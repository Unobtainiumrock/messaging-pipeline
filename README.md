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

1. Clone this repository
2. Run the setup script: `bash setup.sh`
3. Configure credentials in `config/credentials/` following the README there
4. Set environment variables in `.env` (copy from `.env.example`)
5. Run the main application: `python src/main.py`

## VS Code Configuration

If you're using VS Code, set up the correct Python interpreter to avoid import resolution issues:

1. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Type "Python: Select Interpreter"
3. Select the "**Pyenv**" option (e.g., `Python 3.12.3 64-bit ('3.12.3') ~/.pyenv/versions/3.12.3/bin/python`)
4. **Important**: Make sure to select the "Pyenv" option specifically, not the similar "Recommended" or "Workspace" options
5. Restart VS Code or reload the window

This ensures that VS Code correctly resolves all imports, including the `crontab` module used in scheduling scripts.

## Requirements

- Python 3.9+
- Node.js 14+ (for Puppeteer scripts)
- Puppeteer 24.3.1+ (earlier versions have security vulnerabilities)
- Google Cloud Platform account for API access
- PhantomBuster account for LinkedIn automation
- Calendly account

## Development

- Install Python dependencies: `pip install -r requirements.txt`
- Install Node.js dependencies: `npm install` 

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
│   ├── directory_printer.py         # Script to print directory structure
│   ├── schedule_job.py              # Script to schedule jobs
│   ├── update_readme_structure.py   # Script to update README structure
├── config/
│   ├── config.py                    # Configuration file
│   ├── credentials/
│   │   ├── .gitkeep                  # Placeholder file for git
│   │   ├── README.md                 # Credentials README
│   │   ├── google_credentials.json    # Google API credentials
├── src/
│   ├── main.py                      # Main script
│   ├── automation/
│   │   ├── selenium_utils.py         # Utility functions for Selenium
│   │   ├── puppeteer_scripts/
│   │   │   ├── handshake.js          # Puppeteer script for handshake
│   │   │   ├── utils.js              # Utility functions for Puppeteer
│   ├── connectors/
│   │   ├── discord_connector.py      # Discord API integration
│   │   ├── email_connector.py        # Email API integration
│   │   ├── handshake_connector.py    # Handshake API integration
│   │   ├── linkedin_connector.py     # LinkedIn API integration
│   │   ├── slack_connector.py        # Slack API integration
│   ├── processing/
│   │   ├── message_classifier.py     # Message classifier
│   │   ├── nlp_processor.py          # NLP processor
│   ├── scheduling/
│   │   ├── calendly.py               # Calendly API integration
│   │   ├── google_calendar.py        # Google Calendar API integration
│   ├── storage/
│   │   ├── google_sheets.py          # Google Sheets API integration
├── tests/
│   ├── run_all_tests.py              # Script to run all tests
│   ├── run_component_tests.py        # Script to run component tests
│   ├── run_credential_tests.py       # Script to run credential tests
│   ├── component/
│   │   ├── test_automation.py        # Automation tests
│   │   ├── test_connectors.py        # Connector tests
│   │   ├── test_processing.py        # Processing tests
│   │   ├── test_scheduling.py        # Scheduling tests
│   │   ├── test_storage.py           # Storage tests
│   ├── credentials/
│   │   ├── README.md                 # Credentials README
│   │   ├── test_calendly_credentials.py  # Calendly credentials test
│   │   ├── test_discord_credentials.py   # Discord credentials test
│   │   ├── test_email_credentials.py     # Email credentials test
│   │   ├── test_phantombuster_credentials.py  # PhantomBuster credentials test
│   │   ├── test_sheets_credentials.py     # Google Sheets credentials test
│   │   ├── test_slack_credentials.py      # Slack credentials test
├── .pre-commit-config.yaml          # Pre-commit configuration
├── README.md                        # Project documentation
├── TODOPROMPTS.txt                  # To-do prompts
├── comm_centralizer.log             # Log file
├── package.json                     # Node package file
├── requirements.txt                 # Project requirements
└── setup.sh                         # Setup script
```