#!/bin/python3

## Utils ct2template

import os
import time
import sys
import subprocess
from config import logger, DUMP_DIR, TEMPLATE_DIR

# Remonte d'un cran pour trouver la conf générale
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_utils import is_valid_ct_number, container_exists, get_ct_status


def update_and_clean_ct(CTNumber):
    """Mettre à jour et nettoyer le conteneur avant de l'arrêter."""
    try:
        logger.info(f"Nettoyage du conteneur {CTNumber}...")
        subprocess.run(f"pct exec {CTNumber} -- apt-get clean", shell=True, check=True)
        subprocess.run(f"pct exec {CTNumber} -- rm -rf /tmp/* /var/tmp/*", shell=True, check=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la mise à jour ou du nettoyage du conteneur : {e}")
        exit(1)


def shutdown_ct(CTNumber):
    """Arrêter le conteneur."""
    try:
        logger.info(f"Arrêt du conteneur {CTNumber}...")
        subprocess.run(f"pct shutdown {CTNumber}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'arrêt du conteneur : {e}")
        exit(1)


def dump_ct(CTNumber):
    """Faire un dump du conteneur et capturer le nom du fichier dump."""
    try:
        logger.info(f"Sauvegarde du conteneur {CTNumber} avec vzdump...")

        # Capturer la sortie de vzdump
        result = subprocess.run(f"vzdump {CTNumber} --compress zstd", shell=True, check=True, capture_output=True,
                                text=True)

        # Extraire le chemin du fichier de dump
        for line in result.stdout.splitlines():
            if "creating vzdump archive" in line:
                dump_file_path = line.split("'")[1]
                return dump_file_path

        logger.error(f"Impossible de trouver le chemin du fichier de dump dans la sortie de vzdump.")
        exit(1)

    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la création du dump : {e}")
        exit(1)


def move_and_rename_dump(dump_file_path):
    """Déplacer et renommer le fichier dump dans le répertoire des templates."""
    try:
        # Demander le nom du template
        template_name = input("Entrez le nom souhaité pour le template (ex : template-1ere) : ").strip()

        if not template_name:
            logger.error("Nom du template invalide.")
            exit(1)

        # Déplacer et renommer le fichier
        new_template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.tar.zst")
        os.rename(dump_file_path, new_template_path)

        logger.info(f"Le template a été sauvegardé sous {new_template_path}")

    except FileNotFoundError:
        logger.error("Fichier de dump non trouvé.")
        exit(1)
    except OSError as e:
        logger.error(f"Erreur lors du déplacement ou du renommage du fichier de dump : {e}")
        exit(1)


def delete_hostname_and_net0(CTNumber):
    """Supprimer le hostname et la configuration net0 du conteneur avant le dump."""
    try:
        logger.info(f"Suppression du hostname et de net0 pour le conteneur {CTNumber}...")

        # Vérifier si le hostname est défini avant de le supprimer
        result = subprocess.run(f"pct config {CTNumber}", shell=True, check=True, capture_output=True, text=True)

        # Parcourir la configuration pour vérifier le hostname
        hostname_exists = any("hostname" in line for line in result.stdout.splitlines())

        # Supprimer le hostname uniquement s'il est défini
        if hostname_exists:
            subprocess.run(f"pct set {CTNumber} -delete hostname", shell=True, check=True)
            logger.info(f"Hostname supprimé pour le conteneur {CTNumber}.")
        else:
            logger.info(f"Pas de hostname défini pour le conteneur {CTNumber}, aucune suppression nécessaire.")

        # Supprimer la configuration de net0
        subprocess.run(f"pct set {CTNumber} -delete net0", shell=True, check=True)
        logger.info(f"Configuration net0 supprimée pour le conteneur {CTNumber}.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la suppression du hostname ou de net0 pour le conteneur {CTNumber} : {e}")
        exit(1)


def check_ct_status(CTNumber):
    """Vérifier l'état du conteneur et attendre qu'il soit démarré s'il est arrêté."""
    status = get_ct_status(CTNumber)

    if status == "stopped":
        print(f"Le conteneur {CTNumber} est arrêté. Démarrage du conteneur...")
        try:
            subprocess.run(f"pct start {CTNumber}", shell=True, check=True)
            print(f"Conteneur {CTNumber} démarré. Attente de l'état 'running'...")

            # Attendre que le conteneur soit en cours d'exécution
            while status != "running":
                print(f"Le conteneur {CTNumber} est toujours en cours de démarrage...")
                time.sleep(5)  # Attendre 5 secondes avant de vérifier à nouveau
                status = get_ct_status(CTNumber)

            print(f"Le conteneur {CTNumber} est maintenant en cours d'exécution.")

        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du démarrage du conteneur {CTNumber} : {e}")
            exit(1)

    elif status == "error":
        print(f"Erreur lors de la récupération de l'état du conteneur {CTNumber}.")
        exit(1)
