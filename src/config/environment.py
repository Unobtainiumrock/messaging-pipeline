import os

# Get environment from env var, default to development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "t")

# Environment-specific settings
if ENVIRONMENT == "production":
    LOG_LEVEL = "INFO"
    RETRY_ATTEMPTS = 5
    TIMEOUT = 30
else:  # development
    LOG_LEVEL = "DEBUG"
    RETRY_ATTEMPTS = 2
    TIMEOUT = 10

def is_production():
    """Check if running in production environment"""
    return ENVIRONMENT == "production"

def is_development():
    """Check if running in development environment"""
    return ENVIRONMENT == "development" 