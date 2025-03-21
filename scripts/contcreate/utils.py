#!/bin/python3

## Utils contcreate

import os
import subprocess
import getpass
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_utils import is_valid_ct_number, container_exists
from kora_config import TEMPLATE_DIR
from config import logger, GATEWAY, BRIDGE, DEVICE_TYPE, DEFAULT_PASSWORD

def assign_ip(CTNumber):
    """Assigner une adresse IP statique basée sur CTNumber selon la logique correcte"""
    base_ip = (CTNumber - 100) // 100 + 1  # Ensure base IP starts from 1 for CT 100
    last_octet = 100 + (CTNumber % 100)  # Utiliser 100 + (CTNumber % 100) pour l'octet final
    return f"10.80.{base_ip}.{last_octet}"


def get_next_ct_number():
    """Récupérer le premier numéro de conteneur disponible en vérifiant les écarts dans les conteneurs existants"""
    try:
        result = subprocess.run("pct list", shell=True, check=True, capture_output=True, text=True)
        ct_numbers = sorted([int(line.split()[0]) for line in result.stdout.splitlines()[1:]])

        # If there are no CTs, start with 100
        if not ct_numbers:
            return 100

        # Find the first gap in the sequence
        for i in range(100, ct_numbers[-1] + 1):
            if i not in ct_numbers:
                return i

        # If no gaps, return the next number in sequence
        return ct_numbers[-1] + 1 if ct_numbers else 100
    except subprocess.CalledProcessError:
        logger.error("Impossible de récupérer le prochain numéro de conteneur.")
        return None


def create_container(password, ram, cpu, storage, CTNumber, template, name, storage_type="local-lvm"):
    """ Fonction créant un conteneur"""
    if not is_valid_ct_number(int(CTNumber)):  # S'assurer que CTNumber est un entier
        print(f"Numéro de conteneur invalide: {CTNumber}")
        return False

    if container_exists(CTNumber):
        print(f"Le conteneur avec le numéro {CTNumber} existe déjà.")
        return False
    
    ram = int(ram)
    if ram < 16:
        print("La RAM ne doit pas être inférieure à 16.")
        exit(1)
    
    # Assigner une IP basée sur le CTNumber
    ip_address = assign_ip(CTNumber)

    try:
        # Ajouter la configuration réseau, le nom du conteneur et la description comme tag
        description = f"Template : {template}".strip()
        create_command = (
            f"pct create {CTNumber} {TEMPLATE_DIR}{template} --cores {cpu} "
            f"--memory {ram} "
            f"--rootfs {storage_type}:{storage},size={storage} "
            f"--password {password} "
            f"--hostname {name} "
            f"--features nesting=1 "
            f"--unprivileged 1 "
            f"--description \"{description}\" "
            f"--net0 name=eth0,bridge={BRIDGE},firewall=1,gw={GATEWAY},ip={ip_address}/24,type={DEVICE_TYPE}"
        )

        print(f"Tentative de création d'un conteneur : {create_command}")

        # Exécuter la commande tout en filtrant la sortie SSH
        process = subprocess.Popen(create_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate()

        for line in stdout.splitlines():
            # Filtrer les lignes SSH
            if "Creating SSH host key" not in line and "done: SHA256:" not in line:
                print(line.strip())  # Imprimer directement sans le logger

        if process.returncode == 0:
            return True
        else:
            print(f"Erreur lors de la création du conteneur {CTNumber}: {stderr.strip()}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la création du conteneur {CTNumber}: {str(e)}")
        return False


def create_multiple_containers(password, ram, cpu, storage, CTNumber, template, base_name, loop_count,
                               start_after_creation, storage_type="local-lvm"):
    """
    Créer plusieurs conteneurs avec les mêmes paramètres, mais des noms et CTNumber différents.
    Gère également les options de mot de passe.
    """
    use_same_password = True
    if password != DEFAULT_PASSWORD:
        # Demander à l'utilisateur s'il souhaite utiliser le même mot de passe pour tous les conteneurs
        choice = input("Utiliser le même mot de passe pour tous les conteneurs? (o/n): ").lower()
        if choice not in ['o', 'y']:
            use_same_password = False

    created_ct_count = 0
    current_ct_number = CTNumber

    while created_ct_count < loop_count:
        # Vérifier si le numéro de conteneur existe déjà, et l'incrémenter si c'est le cas
        while container_exists(current_ct_number):
            logger.error(f"Le conteneur avec le numéro {current_ct_number} existe déjà.")
            current_ct_number += 1

        # Nom du conteneur avec suffixe
        if base_name:
            name = f"{base_name}-{created_ct_count}" if created_ct_count > 0 else base_name
        else:
            name = str(current_ct_number)  # Utilise directement le numéro comme nom par défaut

        # Mot de passe personnalisé pour chaque conteneur
        current_password = password
        if not use_same_password:
            while True:
                current_password = getpass.getpass(prompt='Veuillez entrer le mot de passe pour le conteneur (5 caractères minimum): ')
                if len(current_password) >= 5:
                    break
                else:
                    print("Le mot de passe doit comporter au moins 5 caractères.")

        # Création du conteneur
        success = create_container(
            password=current_password,
            ram=ram,
            cpu=cpu,
            storage=storage,
            CTNumber=current_ct_number,  # Utiliser le numéro de conteneur actuel
            template=template,
            # node=node,
            name=name,
            storage_type=storage_type
        )

        if success:
            log_creation(template, current_ct_number)
            logger.info(f"Conteneur '{name}' créé avec succès !")

            # Démarrer le conteneur si demandé
            if start_after_creation:
                logger.info(f"Démarrage du conteneur {current_ct_number}...")
                subprocess.run(f"pct start {current_ct_number}", shell=True, check=True)
                logger.info(f"Conteneur {current_ct_number} démarré.")

            created_ct_count += 1  # Incrémenter le nombre de conteneurs créés
            current_ct_number += 1  # Passer au prochain numéro de conteneur
        else:
            logger.error(f"Échec de la création du conteneur '{name}'.")
            return False

    return True


def list_templates():
    """Renvoi une liste des templates disponibles"""
    templates = os.listdir(TEMPLATE_DIR)
    if not templates:
        logger.error("Aucun template disponible.")
        return None
    print("Templates disponibles:")
    for idx, template in enumerate(templates, 1):
        print(f"{idx}. {template}")
    choice = input("Veuillez entrer le numéro du template: ")
    try:
        return templates[int(choice) - 1]
    except (IndexError, ValueError):
        logger.error("Choix de template invalide.")
        return None

def get_users_from_group(group_name):
    """Récupère les utilisateurs d'un groupe spécifique."""
    users = []
    try:
        with open("/etc/pve/user.cfg", "r") as file:
            for line in file:
                if line.startswith(f"group:{group_name}:"):
                    users_list = line.strip().split(":")[2]
                    users = [user.split('@')[0] for user in users_list.split(",") if user]
                    break  # Une seule ligne correspondante suffit
    except FileNotFoundError:
        logger.error("Erreur : Fichier /etc/pve/user.cfg introuvable.")
    return users

def assign_permissions(container_id, username, role):
    """Attribue les permissions de gestion du conteneur à l'utilisateur avec un rôle spécifique."""
    command = f"pveum aclmod /vms/{container_id} -user {username}@pve -role {role}"
    subprocess.run(command, shell=True, check=True)
    logger.info(f"Rôle '{role}' assigné au conteneur {container_id} pour {username}.")


def list_roles():
    """Récupère et retourne uniquement les noms des rôles disponibles à partir du fichier de configuration."""
    roles = {0: "Aucun rôle"}  # Option pour ne donner aucun rôle  # Option pour ne donner aucun rôle
    try:
        with open("/etc/pve/user.cfg", "r") as file:
            for line in file:
                match = re.match(r'role:(\S+):', line)  # Trouver uniquement les titres des rôles
                if match:
                    role_name = match.group(1).split(':')[0].strip()
                    roles[len(roles)] = role_name  # Ajouter le rôle avec un index
        print("Rôles disponibles :")
        for index, role_name in roles.items():
            print(f"{index}: {role_name}")
    except FileNotFoundError:
        logger.error("Fichier de configuration des utilisateurs introuvable.")
    return {k: v.split(':')[0] for k, v in roles.items()}


def log_creation(template, CTNumber):
    """Log la création d'un conteneur avec le template utilisé"""
    logger.info(f"Conteneur créé: {CTNumber} avec le template {template}")


def get_storage_types():
    """Récupère les types de stockage disponibles en utilisant la commande `pvesm status`."""
    try:
        result = subprocess.run(["pvesm", "status"], capture_output=True, text=True, check=True)
        storage_types = []
        for line in result.stdout.splitlines()[1:]:  # Ignorer la première ligne d'en-tête
            storage_name = line.split()[0]
            storage_types.append(storage_name)
        return storage_types
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution de `pvesm status`: {e}")
        return []

def choose_storage_type():
    """Demande à l'utilisateur de choisir le type de stockage parmi les options disponibles."""
    storage_types = get_storage_types()
    if not storage_types:
        logger.error("Aucun type de stockage disponible.")
        return None

    if len(storage_types) == 1:
        return storage_types[0]

    print("Types de stockage disponibles:")
    for idx, storage_type in enumerate(storage_types, 1):
        print(f"{idx}. {storage_type}")
    choice = input("Veuillez entrer le numéro du type de stockage: ")
    try:
        return storage_types[int(choice) - 1]
    except (IndexError, ValueError):
        logger.error("Choix de type de stockage invalide.")
        return None
    