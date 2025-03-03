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
2. Run the setup script: `bash scripts/setup.sh`
3. Configure credentials in `config/credentials/` following the README there
4. Set environment variables in `.env` (copy from `.env.example`)
5. Run the main application: `python src/main.py`

## Requirements

- Python 3.9+
- Node.js 14+ (for Puppeteer scripts)
- Google Cloud Platform account for API access
- PhantomBuster account for LinkedIn automation
- Calendly account

## Development

- Install Python dependencies: `pip install -r requirements.txt`
- Install Node.js dependencies: `npm install` 


## Project Structure

```bash
comm-centralizer/
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies (for Puppeteer)
├── config/                    # Configuration files
│   ├── config.py              # Main configuration 
│   └── credentials/           # Store credentials (gitignored)
│       ├── .gitkeep
│       └── README.md          # Instructions for credential setup
├── src/                       # Source code
│   ├── connectors/            # API connections to various platforms
│   │   ├── __init__.py
│   │   ├── email_connector.py     # Gmail/Outlook API
│   │   ├── linkedin_connector.py  # PhantomBuster integration
│   │   ├── handshake_connector.py # Selenium/Puppeteer for Handshake
│   │   ├── slack_connector.py     # Slack API integration
│   │   └── discord_connector.py   # Discord API integration
│   ├── storage/               # Data storage handlers
│   │   ├── __init__.py
│   │   └── google_sheets.py   # Google Sheets API integration
│   ├── processing/            # Message processing modules
│   │   ├── __init__.py
│   │   ├── nlp_processor.py   # spaCy NLP with LLM integration
│   │   └── message_classifier.py  # Classify messages by intent
│   ├── scheduling/            # Interview scheduling components
│   │   ├── __init__.py
│   │   ├── calendly.py        # Calendly API integration
│   │   └── google_calendar.py # Google Calendar API integration
│   ├── automation/            # Browser automation
│   │   ├── __init__.py
│   │   ├── selenium_utils.py  # Selenium utilities
│   │   └── puppeteer_scripts/ # JavaScript Puppeteer scripts
│   │       ├── handshake.js   # Handshake automation
│   │       └── utils.js       # Shared JS utilities
│   └── main.py                # Main application entry point
├── scripts/                   # Utility scripts
│   ├── setup.sh               # Initial setup script
│   └── schedule_job.py        # For scheduled runs
└── tests/                     # Testing modules
    ├── __init__.py
    ├── test_connectors.py
    ├── test_processing.py
    └── test_scheduling.py
```