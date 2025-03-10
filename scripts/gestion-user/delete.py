import csv
import subprocess
import os
import argparse

# Script Proxmox User and Group Manager
# -------------------------------------
# Ce script permet de :
# 1. Supprimer des utilisateurs à partir d'un fichier CSV (une seule valeur par ligne : le username).
# 2. Supprimer des utilisateurs associés à un groupe donné.
# 3. Supprimer des groupes à partir d'un fichier CSV.
# 
# Structure du fichier CSV attendu :
# - Pour les utilisateurs : Une seule colonne avec les usernames.
# - Pour les groupes : Un nom de groupe par ligne.
#
# Exemple d'exécution :
# python script.py --file /chemin/vers/fichier_utilisateurs.csv
# python script.py --group <group_name>
# python script.py --delete-groups /chemin/vers/fichier_groupes.csv

def run_command(command):
    """Éxécution de la commande"""
    try:
        subprocess.run(command, shell=True, check=True, text=True)
        print(f"Commande réussie : {command}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {command}")
        print(str(e))

# Supprime un utilisateur
def delete_user(username):
    """Supprime un utilisateur"""
    check_user_command = f"pveum user list | grep -w {username}@pve"
    result = subprocess.run(check_user_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:  # Si l'utilisateur existe
        delete_user_command = f"pveum user delete {username}@pve"
        run_command(delete_user_command)
        print(f"Utilisateur supprimé : {username}")
    else:
        print(f"Utilisateur non trouvé : {username}")

# Supprime tous les utilisateurs d'un groupe
def delete_users_in_group(group_name):
    """Supprime tous les utilisateurs d'un groupe"""
    # Utiliser `cat` pour récupérer les utilisateurs du groupe dans user.cfg
    list_users_command = f"cat /etc/pve/user.cfg | grep '^group:{group_name}:'"
    try:
        result = subprocess.run(list_users_command, shell=True, check=True, capture_output=True, text=True)
        line = result.stdout.strip()

        if not line:
            print(f"Aucun utilisateur trouvé dans le groupe {group_name}.")
            return

        # Extraire les utilisateurs de la ligne correspondante
        parts = line.split(':')
        if len(parts) > 2 and parts[2]:
            users = [user.split('@')[0].strip() for user in parts[2].split(',')]
            print(f"Utilisateurs trouvés dans le groupe {group_name} : {users}")

            # Supprimer les utilisateurs trouvés
            for user in users:
                print(f"Suppression de l'utilisateur : {user}")
                delete_user(user)
        else:
            print(f"Aucun utilisateur listé pour le groupe {group_name}.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la récupération des utilisateurs du groupe {group_name} : {e}")



# Supprime un groupe si existant
def delete_group(group_name):
    """Supprime un groupe si existant"""
    check_group_command = f"pveum group list | grep -w {group_name}"
    result = subprocess.run(check_group_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:  # Si le groupe existe
        delete_group_command = f"pveum group delete {group_name}"
        run_command(delete_group_command)
        print(f"Groupe supprimé : {group_name}")
    else:
        print(f"Groupe non trouvé : {group_name}")

def main():
    """ Fonction principale gérant la suppresions des utilisateurs et des groupes"""
    parser = argparse.ArgumentParser(description="Script pour supprimer des utilisateurs ou des groupes spécifiques.")
    parser.add_argument("--file", type=str, help="Chemin du fichier CSV contenant les usernames à supprimer \nFormat du fichier : username")
    parser.add_argument("--group", type=str, help="Nom du groupe dont les utilisateurs doivent être supprimés")
    parser.add_argument("--delete-groups", type=str, help="Chemin du fichier CSV contenant les groupes à supprimer \nFormat du fichier : group_name")
    args = parser.parse_args()

    if args.file:
        csv_file_path = args.file

        if not os.path.exists(csv_file_path):
            print(f"Le fichier spécifié n'existe pas : {csv_file_path}")
            return

        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                if len(row) != 1:
                    print(f"Ligne invalide dans le fichier CSV : {row}")
                    continue
                username = row[0].strip()
                delete_user(username)

    elif args.group:
        delete_users_in_group(args.group)

    elif args.delete_groups:
        csv_file_path = args.delete_groups

        if not os.path.exists(csv_file_path):
            print(f"Le fichier spécifié n'existe pas : {csv_file_path}")
            return

        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file, delimiter=';')

            for row in reader:
                if len(row) != 1:
                    print(f"Ligne invalide dans le fichier CSV : {row}")
                    continue
                group_name = row[0].strip()
                delete_group(group_name)

    else:
        print("Veuillez spécifier soit un fichier CSV avec --file, soit un groupe avec --group, soit des groupes avec --delete-groups.")

if __name__ == "__main__":
    main()