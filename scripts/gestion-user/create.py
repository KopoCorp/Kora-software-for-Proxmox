import csv
import subprocess
import os
import argparse

# Script Proxmox User and Group Manager
# -------------------------------------
# Ce script permet de :
# 1. Créer des utilisateurs à partir d'un fichier CSV.
# 2. Créer des groupes si nécessaire.
# 3. Assigner les utilisateurs à plusieurs groupes.
# 4. Utiliser des ACL pour gérer les permissions des groupes.
# 
# Structure du fichier CSV attendu :
# - Nom : Nom de famille de l'utilisateur.
# - Prenom : Prénom de l'utilisateur.
# - Password : Mot de passe de l'utilisateur.
# - Groupe : Liste des groupes séparés par des virgules (ex. "group1,group2").
#
# Exemple d'exécution :
# python script.py --file /chemin/vers/fichier.csv

#Éxécution de la commande
def run_command(command):
    """Éxécution de la commande"""
    try:
        subprocess.run(command, shell=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {command}")
        print(str(e))

#Vérification et création des groupes
def ensure_group_exists(group_name):
    """Vérification et création des groupes"""
    check_command = f"pveum group list | grep -w {group_name}"
    result = subprocess.run(check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:  # Si le groupe n'existe pas
        create_command = f"pveum group add {group_name}"
        run_command(create_command)

#Vérification et création des users
def create_user(username, firstname, lastname, password):
    """Vérification et création des users"""
    check_user_command = f"pveum user list | grep -w {username}@pve"
    result = subprocess.run(check_user_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:  # Si l'utilisateur n'existe pas
        create_user_command = f"pveum user add {username}@pve -firstname {firstname} -lastname {lastname} -password {password}"
        run_command(create_user_command)
        print(f"Utilisateur créé : Username={username}, Prénom={firstname}, Nom={lastname}")
    else:
        print(f"Utilisateur déjà existant : Username={username}")

#Assignation des users dans les groupes
def assign_user_to_groups(username, groups):
    """Assignation des users dans les groupes"""
    groups_str = ",".join(groups)
    modify_command = f"pveum user modify {username}@pve --groups {groups_str}"
    try:
        run_command(modify_command)
        print(f"Utilisateur {username} assigné aux groupes : {groups_str}")
    except Exception as e:
        print(f"Erreur lors de l'assignation des groupes pour l'utilisateur {username} : {e}")

def main():
    """Fonction principale gérant la création d'utilisateur et de groupes en associant les utilisateurs à ce dernier"""
    parser = argparse.ArgumentParser(description="Script pour créer des utilisateurs et les ajouter à des groupes depuis un fichier CSV.")
    parser.add_argument("-f", "--file", type=str, help="Chemin du fichier CSV contenant les utilisateurs \nFormat du fichier : Nom;Prénom;password;groupe1,groupe2,...,groupex", required=True)
    args = parser.parse_args()

    csv_file_path = args.file

    if not os.path.exists(csv_file_path):
        print(f"Le fichier spécifié n'existe pas : {csv_file_path}")
        return

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file, delimiter=';')

        # Parcours des utilisateurs dans le CSV
        for row in reader:
            lastname = row.get('Nom')
            firstname = row.get('Prenom')
            password = row.get('Password')
            group_field = row.get('Groupe')

            if not lastname or not firstname or not password or not group_field:
                print(f"Ligne invalide ou incomplète dans le fichier CSV : {row}")
                continue

            username = f"{firstname.lower()}{lastname.lower()}"

            # Extraire les groupes en les séparant par des virgules
            groups = [group.strip() for group in group_field.split(',') if group.strip()]

            # Créer les groupes nécessaires
            for group in groups:
                ensure_group_exists(group)

            # Créer l'utilisateur
            create_user(username, firstname, lastname, password)

            # Assigner les groupes à l'utilisateur
            assign_user_to_groups(username, groups)

            print(f"Création terminée pour l'utilisateur {username} ({firstname} {lastname}) avec les groupes {', '.join(groups)}")

if __name__ == "__main__":
    main()