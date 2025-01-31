#!/bin/python3

## Config ct2template

import os
import sys
from datetime import datetime
import logging
from rich.logging import RichHandler

# Remonte d'un cran pour trouver la conf générale
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_config import LOG_DIR, DUMP_DIR, TEMPLATE_DIR

# Set up log file path (one log per day)
log_file = os.path.join(LOG_DIR, f"ct2template_{datetime.now().strftime('%Y-%m-%d')}.log")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(), logging.FileHandler(log_file)]
)

logger = logging.getLogger("ct2template")
