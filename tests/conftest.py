"""Configure pytest for testing the Communication Centralizer."""

import sys
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path to resolve 'src' imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """
    Register custom pytest markers and clear cache.

    This is a pytest hook that runs during test collection setup
    to register custom markers used throughout the test suite.

    Args:
        config: The pytest configuration object
    """
    # Register markers
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")

    # Clear the pytest cache
    cache_dir = Path(config.rootdir) / ".pytest_cache"
    if cache_dir.exists():
        print("Clearing pytest cache...")
        shutil.rmtree(cache_dir)
        print("Pytest cache cleared.")


# Get the absolute path to the project root
project_root = Path(__file__).parent.parent

# Force reload of environment variables with override
print("Loading environment variables from .env file...")
load_dotenv(os.path.join(project_root, ".env"), override=True)
print("Environment variables loaded.")


# Add a debug function you can call from any test if needed
def print_env_vars():
    """Print environment variables to help with debugging."""
    print("\nCurrent environment variables:")
    print(f"EMAIL_TYPE: {os.getenv('EMAIL_TYPE')}")
    print(f"EMAIL_USERNAME: {os.getenv('EMAIL_USERNAME')}")
    print(f"EMAIL_PASSWORD exists: {'Yes' if os.getenv('EMAIL_PASSWORD') else 'No'}")
    print(f"OPENAI_API_KEY exists: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print("--------------------\n")


print_env_vars()
