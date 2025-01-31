#!/bin/python3

import logging
import os
import subprocess

from datetime import datetime
from kora_config import CT_CONFIG_DIR, LOG_DIR
from rich.logging import RichHandler



def is_valid_ct_number(CTNumber):
    """
    Vérifie si le CTNumber est valide
    """
    return 100 <= CTNumber <= 999999999

def container_exists(CTNumber):
    """
    Vérifie l'existence du CT avec son fichier de configuration
    """
    config_path = os.path.join(CT_CONFIG_DIR, f"{CTNumber}.conf")
    return os.path.exists(config_path)

def get_ct_status(CTNumber):
    """
    Récupère le statut d'un CT en utilisant la commande pct status <CTNumber>.
    Renvoie le statut sous forme de chaîne de caractères (par exemple : 'running', 'stopped').
    """
    try:
        result = subprocess.run(f"pct status {CTNumber}", shell=True, check=True, capture_output=True, text=True)
        # Extract status from the command output
        # Assuming the output looks like: "status: running" or "status: stopped"
        status_line = result.stdout.strip().split(": ")
        if len(status_line) == 2 and status_line[0] == "status":
            return status_line[1]
        else:
            return "unknown"
    except subprocess.CalledProcessError as e:
        return "error"

def setup_logger(script_name):
    """
    Permet de configurer le logging avec le fichier et retourne un logger au nom du script qui l'utilise
    """
    log_file = os.path.join(LOG_DIR, f"{script_name}_{datetime.now().strftime('%Y-%m-%d')}.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(), logging.FileHandler(log_file)]
    )
    return logging.getLogger(script_name)
