# #!/bin/bash
# set -e

# echo "Running pre-commit hooks with Docker..."
# echo "Files to check: $@"

# # Load environment variables from .env file if it exists
# if [ -f .env ]; then
#   echo "Loading environment variables from .env file"
#   source .env
# fi

# # Check if we're already running inside Docker
# if [ -f "/.dockerenv" ]; then
#   echo "🐳 Already inside Docker, running pre-commit directly"
#   # Run pre-commit directly since we're already in Docker
#   pre-commit run --files "$@"
# else
#   echo "🖥️ Running on host, using Docker for pre-commit"
#   # Run pre-commit in Docker
#   GIT_USER_NAME="$(git config --get user.name)" \
#   GIT_USER_EMAIL="$(git config --get user.email)" \
#   USER_ID=$(id -u) \
#   GROUP_ID=$(id -g) \
#   docker-compose -f docker-compose.dev.yml run --rm -T \
#     -e GIT_USER_NAME \
#     -e GIT_USER_EMAIL \
#     -e USER_ID \
#     -e GROUP_ID \
#     -e OPENAI_API_KEY="$OPENAI_API_KEY" \
#     app pre-commit run --verbose --files "$@"
# fi
#!/bin/bash
set -e

echo "Running pre-commit hooks..."
echo "Files to check: $@"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  source .env
fi

# Check if we're already running inside Docker
if [ -f "/.dockerenv" ]; then
  echo "🐳 Already inside Docker, running pre-commit directly"
  # Run pre-commit directly since we're already in Docker
  pre-commit run --files "$@"
else
  echo "🖥️ Running on host, using Docker for pre-commit"
  # Run pre-commit in Docker with the same environment as the app
  GIT_USER_NAME="$(git config --get user.name)" \
  GIT_USER_EMAIL="$(git config --get user.email)" \
  USER_ID=$(id -u) \
  GROUP_ID=$(id -g) \
  docker-compose -f docker-compose.dev.yml run --rm -T \
    -e GIT_USER_NAME \
    -e GIT_USER_EMAIL \
    -e USER_ID \
    -e GROUP_ID \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    app bash -c "cd /app && pre-commit run --verbose --files $@"
fi 