# This makes the root directory a proper Python package
import sys
from pathlib import Path

# Add the project root to Python path
ROOT_DIR = str(Path(__file__).parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
