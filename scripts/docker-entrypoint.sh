#!/bin/bash
set -e  # Exit on error

echo "=== Docker Environment Setup ==="

# Get the UID/GID from environment or use defaults
USER_ID=${UID:-1000}
GROUP_ID=${GID:-1000}

echo "Running as UID:GID = $USER_ID:$GROUP_ID"

# Handle user creation only if needed (when running as root but should be a different user)
if [ "$(id -u)" = "0" ] && [ "$USER_ID" != "0" ]; then
    echo "Creating user with UID:GID = $USER_ID:$GROUP_ID..."
    # Create group if it doesn't exist
    if ! getent group $GROUP_ID > /dev/null; then
        groupadd -g $GROUP_ID appuser
    fi
    # Create user if it doesn't exist
    if ! getent passwd $USER_ID > /dev/null; then
        useradd -u $USER_ID -g $GROUP_ID -m appuser
    fi

    # Make sure our working directory exists and is owned by the user
    mkdir -p /app
    chown -R $USER_ID:$GROUP_ID /app
fi

# Set up Git safe directory
echo "Setting up Git safe directory..."
git config --global --add safe.directory /app

# Set Git identity if environment variables are provided
echo "Setting up Git identity..."
if [ ! -z "$GIT_USER_NAME" ] && [ ! -z "$GIT_USER_EMAIL" ]; then
  git config --global user.name "$GIT_USER_NAME"
  git config --global user.email "$GIT_USER_EMAIL"
  echo "✅ Git identity set to: $GIT_USER_NAME <$GIT_USER_EMAIL>"
else
  echo "⚠️ Git identity not set (GIT_USER_NAME and GIT_USER_EMAIL not provided)"
fi

# Set up SSH (with graceful error handling for read-only mounts)
echo "Setting up SSH..."
if [ -d "/root/.ssh" ]; then
  # Try to set permissions, but don't fail if it doesn't work
  chmod 700 /root/.ssh || echo "⚠️ Cannot modify SSH directory permissions (read-only mount, this is OK)"

  # Check for SSH keys
  if [ -f "/root/.ssh/id_rsa" ] || [ -f "/root/.ssh/id_ed25519" ]; then
    echo "✅ SSH keys found"
    # Try to set permissions, but don't fail
    chmod 600 /root/.ssh/id_* || echo "⚠️ Cannot modify SSH key permissions (read-only mount, this is OK)"
  else
    echo "⚠️ No SSH keys found in mounted directory"
  fi
else
  echo "⚠️ SSH directory not mounted"
fi
# Network test
echo "Testing network connectivity..."
ping -c 1 github.com > /dev/null 2>&1 && \
  echo "✅ Network connection to GitHub OK" || \
  echo "⚠️ Cannot ping GitHub (this may be normal depending on your network)"

# If we created a different user and we're root, switch to that user to run the command
if [ "$(id -u)" = "0" ] && [ "$USER_ID" != "0" ]; then
    echo "=== Setup complete. Running command as appuser ==="
    exec su appuser -c "$*"
else
    # We're already running as the correct user or explicitly as root
    echo "=== Setup complete. Running command: $* ==="
    exec "$@"
fi
