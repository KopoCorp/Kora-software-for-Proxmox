import os
import subprocess
import logging
from config import DEPENDANCE_DIR, LOG_FILE

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("utils")


def find_dependency_files():
    """Trouver tous les fichiers de dépendances dans le dossier DEPENDANCE_DIR."""
    try:
        files = [
            os.path.join(DEPENDANCE_DIR, file)
            for file in os.listdir(DEPENDANCE_DIR)
            if os.path.isfile(os.path.join(DEPENDANCE_DIR, file))
        ]
        if not files:
            logger.warning(f"Aucun fichier de dépendances trouvé dans {DEPENDANCE_DIR}.")
        return files
    except FileNotFoundError:
        logger.error(f"Le dossier {DEPENDANCE_DIR} est introuvable.")
        return []


def identify_file_type(file_path):
    """Identifier le type de dépendances en fonction de la première ligne du fichier."""
    try:
        with open(file_path, "r") as f:
            first_line = f.readline().strip()
            if first_line == "# Python":
                return "python"
            elif first_line == "# Apt":
                return "software"
            elif not first_line:
                return "empty"
            else:
                return "unknown"
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier {file_path} : {e}")
        return "unknown"


def read_dependencies(file_path):
    """Lire les dépendances depuis un fichier."""
    try:
        with open(file_path, "r") as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        if not dependencies:
            logger.info(f"Le fichier {file_path} est vide ou ne contient que des commentaires.")
        return dependencies
    except FileNotFoundError:
        logger.error(f"Le fichier {file_path} est introuvable.")
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier des dépendances : {e}")
        return []


def is_package_installed(package):
    """Vérifier si un package Python est déjà installé."""
    try:
        subprocess.run(
            ["pip", "show", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_python_package(package):
    """Installer un package Python avec apt."""
    aptpackage='python3-'+package
    try:
        subprocess.run(
            ["apt", "install", aptpackage],
            check=True
        )
        logger.info(f"Package Python {package} installé avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'installation du package Python {package} : {e}")
        return False


def is_software_installed(software):
    """Vérifier si un logiciel est installé via dpkg (pour apt)."""
    try:
        subprocess.run(
            ["dpkg", "-s", software],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_software(software):
    """Installer un logiciel avec apt."""
    try:
        logger.info(f"Installation du logiciel {software}...")
        subprocess.run(
            ["sudo", "apt", "install", "-y", software],
            check=True
        )
        logger.info(f"Logiciel {software} installé avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'installation du logiciel {software} : {e}")
        return False


def print_summary(installed_python, already_installed_python, installed_software, already_installed_software):
    """Afficher un résumé des dépendances installées."""
    logger.info("=== Résumé global ===")
    logger.info(f"  - {installed_python} package(s) Python installé(s).")
    logger.info(f"  - {already_installed_python} package(s) Python déjà présent(s).")
    logger.info(f"  - {installed_software} logiciel(s) installé(s).")
    logger.info(f"  - {already_installed_software} logiciel(s) déjà présent(s).")
