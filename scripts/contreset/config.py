#!/bin/python3

## Config contreset

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_utils import setup_logger
from kora_config import TEMPLATE_DIR

logger = setup_logger("contreset")