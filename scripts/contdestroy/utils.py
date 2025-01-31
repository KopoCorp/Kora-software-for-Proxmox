#!/bin/python3

## Utils contdestroy

import logging
import os
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_config import CT_CONFIG_DIR  # Importer le répertoire de configuration des CTs depuis la config générale

logger = logging.getLogger("contdestroy")

def handle_ranges(containers):
    """Convertit les plages de conteneurs en liste."""
    CTNumbers = []
    for item in containers:
        if '-' in item:
            start, end = map(int, item.split('-'))
            CTNumbers.extend(range(start, end + 1))
        else:
            CTNumbers.append(int(item))
    return CTNumbers

def container_exists(container_id):
    """Vérifie si le fichier de configuration du conteneur existe."""
    config_path = os.path.join(CT_CONFIG_DIR, f"{container_id}.conf")
    return os.path.isfile(config_path)

def is_container_running(container_id):
    """Vérifie si le conteneur est en cours d'exécution."""
    result = subprocess.run(["pct", "status", str(container_id)], capture_output=True, text=True)
    return "status: running" in result.stdout.lower()

def pct_destroy(container_id, params):
    """Exécute la commande pct destroy et journalise le succès/échec."""
    command = ["pct", "destroy", str(container_id)] + params
    result = subprocess.run(command, capture_output=True, text=True)

    success = result.returncode == 0
    reason = result.stderr.strip() if not success else ""

    # Journaliser l'action sur le conteneur
    logger.info(f"Tentative de destruction du conteneur {container_id} avec les paramètres : {params}")
    if success:
        logger.info(f"Conteneur {container_id} détruit avec succès.")
    else:
        logger.error(f"Échec de la destruction du conteneur {container_id}. Raison : {reason}")

    return success, reason

def print_summary(destroyed, failed, invalid, detailed, total_duration, CTNumbers=None):
    """Affiche le résumé ou les statistiques détaillées."""
    containers_processed = len(destroyed) + len(failed) + len(invalid)

    logger.info(f"Conteneurs détruits : {len(destroyed)}")
    if destroyed:
        logger.info(f"Conteneurs détruits : {destroyed}")
    logger.info(f"Conteneurs échoués : {len(failed)}")
    logger.info(f"Conteneurs invalides : {len(invalid)}")

    if detailed:
        logger.info(f"Durée totale d'exécution : {total_duration:.2f} secondes")
        if containers_processed > 0:
            average_time = total_duration / containers_processed
            logger.info(f"Temps moyen par conteneur : {average_time:.2f} secondes")

