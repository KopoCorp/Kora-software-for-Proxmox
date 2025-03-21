#!/bin/python3

import argparse
import time
from utils import handle_ranges, pct_destroy, print_summary, is_container_running, container_exists
from config import logger, auto_confirm_deletion, auto_confirm_force_stop


def main():
    """Fonction principale gérant la destruction d'un ou plusieurs conteneurs"""
    global auto_confirm_deletion  # Utilisé pour gérer l'auto-confirmation après la première suppression
    global auto_confirm_force_stop  # Utilisé pour l'auto-confirmation de l'arrêt forcé
    
    # Configuration de l'analyse des arguments
    parser = argparse.ArgumentParser(description="Détruire des conteneurs Proxmox avec options de confirmation automatique et force")
    parser.add_argument("containers", nargs="*", help="ID des conteneurs ou plages (ex : 101 102 105-110)", default=[])
    parser.add_argument("-d", action="store_true", help="Retirer --destroy-unreferenced-disks (activé par défaut)")
    parser.add_argument("-p", action="store_true", help="Retirer --purge (activé par défaut)")
    parser.add_argument("-y", action="store_true", help="Confirmer automatiquement la suppression des conteneurs (passer les invites)")
    parser.add_argument("-f", action="store_true", help="Forcer l'arrêt et la suppression des conteneurs en cours d'exécution (remplace la config)")
    parser.add_argument("-s", action="store_true", help="Afficher uniquement le résumé (remplace la config)")
    parser.add_argument("--detailed", action="store_true", help="Afficher les statistiques détaillées incluant le temps d'exécution (remplace la config)")
    
    args = parser.parse_args()

    # Paramètres par défaut
    params = ["--destroy-unreferenced-disks", "--purge"]
    if args.d:
        params.remove("--destroy-unreferenced-disks")
    if args.p:
        params.remove("--purge")
    if args.f:
        params.append("--force")

    # Mode interactif si aucun conteneur n'est fourni
    if not args.containers:
        containers_input = input("Quel(s) conteneur(s) souhaitez-vous supprimer ? (séparé par des espaces) : ")
        args.containers = containers_input.split()

    # Traiter les conteneurs
    CTNumbers = handle_ranges(args.containers)

    # Journaliser la commande exécutée
    pct_command = f"pct destroy {' '.join(map(str, CTNumbers))} {' '.join(params)}"
    logger.info(f"Exécution de la commande : {pct_command}")

    # Démarrer le chronométrage de l'exécution
    start_time = time.time()

    destroyed = []
    failed = {}
    invalid = []

    for i, CTNumber in enumerate(CTNumbers):
        if container_exists(CTNumber):
            running_before = is_container_running(CTNumber)
            forced = False

            # Demander confirmation avant la suppression si -y n'est pas passé
            if not args.y and not auto_confirm_deletion:
                confirm = input(f"Confirmez-vous la suppression du conteneur n°{CTNumber} ? (y/n) : ").lower()
                if confirm not in ['o', 'y']:
                    print(f"Suppression annulée pour le conteneur {CTNumber}")
                    logger.info(f"Suppression annulée pour le conteneur {CTNumber}")
                    continue

                # Ne pas demander d'auto-confirmation si c'est le dernier conteneur
                if i != len(CTNumbers) - 1:
                    auto_confirm = input("Voulez-vous auto-confirmer la suppression pour les autres conteneurs ? (y/n) : ").lower()
                    if auto_confirm in ['o', 'y']:
                        auto_confirm_deletion = True

            # Vérifier si le conteneur est en cours d'exécution et demander pour l'arrêt forcé
            if running_before and not args.f and not auto_confirm_force_stop:
                confirm_force = input(f"Le conteneur n°{CTNumber} est en cours d'exécution. Voulez-vous le forcer à s'arrêter ? (y/n) : ").lower()
                if confirm_force in ['o', 'y']:
                    params.append("--force")
                    forced = True

                    # Ne pas demander d'auto-confirmation si c'est le dernier conteneur
                    if i != len(CTNumbers) - 1:
                        auto_confirm_force = input("Voulez-vous auto-confirmer l'arrêt forcé pour les autres conteneurs en cours d'exécution ? (y/n) : ").lower()
                        if auto_confirm_force in ['o', 'y']:
                            auto_confirm_force_stop = True

            # Appel à pct_destroy depuis utils.py
            success, reason = pct_destroy(CTNumber, params)
            if success:
                destroyed.append(CTNumber)
                logger.info(f"Conteneur {CTNumber} détruit avec succès. En cours avant : {running_before}, Forcé : {forced}")
            else:
                failed[CTNumber] = reason
                logger.error(f"Échec de la destruction du conteneur {CTNumber}. Raison : {reason}")
        else:
            invalid.append(CTNumber)
            logger.warning(f"ID de conteneur invalide : {CTNumber}")

    # Calculer le temps d'exécution
    end_time = time.time()
    total_duration = end_time - start_time

    # Déterminer s'il faut afficher le résumé ou les statistiques détaillées
    if args.detailed:
        print_summary(destroyed, failed, invalid, detailed=True, total_duration=total_duration, CTNumbers=CTNumbers)
    elif args.s:
        print_summary(destroyed, failed, invalid, detailed=False, total_duration=None)


if __name__ == "__main__":
    main()

