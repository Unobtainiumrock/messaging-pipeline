#!/bin/bash
# Get Git user info from local config
GIT_USER_NAME=$(git config --get user.name)
GIT_USER_EMAIL=$(git config --get user.email)

echo "Running pre-commit hooks with Docker..."
echo "Files to check: $@"

# Export environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Run with environment variables explicitly set
docker-compose -f docker-compose.dev.yml run --rm -T \
  -e GIT_USER_NAME="$GIT_USER_NAME" \
  -e GIT_USER_EMAIL="$GIT_USER_EMAIL" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  app pre-commit run --verbose --files "$@"

EXIT_CODE=$?
echo "Pre-commit completed with exit code: $EXIT_CODE"
exit $EXIT_CODE
