import os
import sys

# Ajouter le répertoire parent au chemin d'import
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin absolu du répertoire courant
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../scripts"))  # Répertoire parent
sys.path.insert(0, PARENT_DIR)  # Ajouter le répertoire parent au sys.path

from kora_config import LOG_DIR  # Import LOG_DIR depuis kora_config

# Dossier contenant les fichiers de dépendances
DEPENDANCE_DIR = os.path.join(BASE_DIR, "Dependance")

# Chemin pour les logs
os.makedirs(LOG_DIR, exist_ok=True)  # Crée automatiquement le dossier des logs s'il n'existe pas
LOG_FILE = os.path.join(LOG_DIR, "install-dependancies.log")
