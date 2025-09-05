"""Pytest configuration to make local package imports work.

This ensures tests can `import pycanze...` by adding the project
package root (the 'PyCanZE' folder) to sys.path during test discovery.
"""

from pathlib import Path
import sys

# Add '<repo>/PyCanZE' to sys.path so 'pycanze' is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
