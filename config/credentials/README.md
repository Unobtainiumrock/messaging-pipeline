# Credentials Configuration

This directory contains credential files for various APIs. These files are gitignored for security reasons.

## Required Credentials Files

1. **google_credentials.json** - Google API service account credentials
   - Used for Gmail API, Google Sheets API, and Google Calendar API
   - [Create credentials in Google Cloud Console](https://console.cloud.google.com/)

2. **gmail_token.json** - Gmail API user token
   - Generated during first run with Gmail authentication

3. **phantombuster_config.json** - PhantomBuster configuration
   ```json
   {
     "api_key": "your_phantombuster_api_key",
     "message_agent_id": "your_linkedin_message_agent_id"
   }
   ```

4. **calendly_credentials.json** - Calendly API credentials
   ```json
   {
     "api_key": "your_calendly_api_key",
     "user": "your_calendly_username"
   }
   ```

## Setting Up Credentials

1. Create a service account in Google Cloud Console
2. Download the JSON key file and save as `google_credentials.json`
3. Enable Gmail API, Google Sheets API, and Google Calendar API
4. Set up PhantomBuster account and create agents for LinkedIn
5. Create credentials for Slack and Discord bots if using those platforms 