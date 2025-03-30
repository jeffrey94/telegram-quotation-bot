#!/usr/bin/env python
"""
Launcher script for the Telegram Quotation Bot.
Run this script from the project root directory.
"""

import os
import sys

# Add the current directory to the Python path to ensure imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and run the application
from app.main import main

if __name__ == "__main__":
    main() 