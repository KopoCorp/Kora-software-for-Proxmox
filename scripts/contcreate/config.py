#!/bin/python3

## Config contcreate

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_utils import setup_logger

# Utilise la fonction setup_logger pour configurer le logger avec le nom du script
logger = setup_logger("contcreate")

# Valeurs par défaut
DEFAULT_RAM = 512
DEFAULT_CPU = 1
DEFAULT_STORAGE = 10
DEFAULT_PASSWORD = "K0po*"  # MDP par défaut

# Configuration réseau
GATEWAY = "10.80.254.254"  # Passerelle statique
BRIDGE = "vmbr1"  # Pont par défaut
DEVICE_TYPE = "veth"  # Type de périphérique réseau