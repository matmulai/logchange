#!/usr/bin/env python3
"""Main entry point for LogChange."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logchange.cli import main

if __name__ == "__main__":
    main()
