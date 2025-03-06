"""Configure pytest for testing."""
import sys
from pathlib import Path

# Add project root to Python path to resolve 'src' imports
sys.path.insert(0, str(Path(__file__).parent.parent))
