#!/bin/python3

## Config contdestroy

import sys
import time
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Remonte d'un cran pour trouver la conf générale

from kora_config import LOG_DIR
from kora_utils import setup_logger

# Configuration pour contdestroy

force_stop = False  # Arrêt forcé des conteneurs par défaut
summary_output = False  # Affiche le résumé par défault
detailed_output = False  # Affiche les stats par défault
logger = setup_logger("contdestroy")

# Confirmation auto mode interactif


auto_confirm_deletion = False  # Confirme automatiquement la suppression des CTs
auto_confirm_force_stop = False  # Stop automatiquement les CTs
