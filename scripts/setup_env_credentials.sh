#!/bin/bash
ENVIRONMENT=$1

# Create credentials directory if it doesn't exist
mkdir -p config/credentials

# Use environment variables to create credential files
if [ "$ENVIRONMENT" = "production" ]; then
  echo "$GOOGLE_PRODUCTION_CREDENTIALS" > config/credentials/google_credentials.json
  echo "$PHANTOMBUSTER_PRODUCTION_API_KEY" > config/credentials/phantombuster_api_key.txt
else
  echo "$GOOGLE_STAGING_CREDENTIALS" > config/credentials/google_credentials.json
  echo "$PHANTOMBUSTER_STAGING_API_KEY" > config/credentials/phantombuster_api_key.txt
fi
