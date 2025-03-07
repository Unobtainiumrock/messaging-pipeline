"""Configure pytest for testing the Communication Centralizer."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path to resolve 'src' imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """
    Register custom pytest markers.

    This is a pytest hook that runs during test collection setup
    to register custom markers used throughout the test suite.

    Args:
        config: The pytest configuration object
    """
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")


# Get the absolute path to the project root
project_root = Path(__file__).parent.parent
# Load environment variables from the .env file in the project root
load_dotenv(os.path.join(project_root, ".env"))
