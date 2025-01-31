#!/bin/python3

from utils import update_and_clean_ct, shutdown_ct, dump_ct, move_and_rename_dump, is_valid_ct_number, \
    container_exists, check_ct_status, delete_hostname_and_net0


def confirm_actions(ct_number):
    """
    Avertir l'utilisateur des actions qui seront effectuées et demander confirmation.
    """
    print(f"Les actions suivantes seront effectuées sur le conteneur {ct_number} :")
    print("1. Nettoyage du conteneur.")
    print("2. Suppression de la configuration du hostname et de net0.")
    print("3. Arrêt du conteneur.")
    print("4. Sauvegarde du conteneur sous forme de template.")
    print("5. Déplacement et renommage du fichier de sauvegarde.")

    # Demander confirmation
    confirmation = input("Souhaitez-vous continuer avec ces actions ? (o/n) : ").lower()
    if confirmation not in ['o', 'oui', 'y', 'yes']:  # Accepter 'o', 'oui', 'y' et 'yes'
        print("Processus annulé.")
        exit(0)


def main():
    """
    Fonction principale pour transformer un conteneur en template
    """
    # Obtenir le numéro du conteneur
    CTNumber = input("Entrez le numéro du conteneur (CTNumber) : ").strip()

    # Valider le numéro du conteneur
    if not is_valid_ct_number(int(CTNumber)):
        print("Numéro de conteneur invalide. Il doit être compris entre 100 et 999999999.")
        exit(1)

    # Vérifier si le conteneur existe
    if not container_exists(int(CTNumber)):
        print(f"Le conteneur {CTNumber} n'existe pas.")
        exit(1)

    # Vérifier l'état du conteneur et le démarrer s'il est arrêté
    check_ct_status(CTNumber)

    # Demander confirmation des actions
    confirm_actions(CTNumber)

    # Étape 1 : Mettre à jour et nettoyer le conteneur
    update_and_clean_ct(CTNumber)

    # Étape 2 : Supprimer le hostname et net0 avant de faire le dump
    delete_hostname_and_net0(CTNumber)

    # Étape 3 : Arrêter le conteneur
    shutdown_ct(CTNumber)

    # Étape 4 : Faire un dump du conteneur et capturer le chemin du fichier dump
    dump_file_path = dump_ct(CTNumber)

    # Étape 5 : Déplacer et renommer le fichier dump
    move_and_rename_dump(dump_file_path)


if __name__ == "__main__":
    main()
