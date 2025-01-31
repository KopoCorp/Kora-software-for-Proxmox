import argparse
import subprocess
import getpass
from utils import create_multiple_containers, create_container, list_templates, get_next_ct_number, get_users_from_group, assign_permissions, list_roles
from config import logger, DEFAULT_RAM, DEFAULT_CPU, DEFAULT_STORAGE, DEFAULT_PASSWORD

def main():
    """Fonction principale pour créer des conterneurs"""
    parser = argparse.ArgumentParser(description="Script pour créer un conteneur Proxmox")
    parser.add_argument("-c", "--cpu", help="Nombre de cœurs CPU", default=DEFAULT_CPU)
    parser.add_argument("-l", "--loop", help="Nombre de conteneurs à créer", type=int, default=1)
    parser.add_argument("-n", "--number", help="Numéro de conteneur", default=None, type=int)
    parser.add_argument("--name", help="Nom du conteneur", default=None)
    parser.add_argument("-o", "--node", help="Nom du noeud (node) où installer le conteneur (pas implémenté)", default="local")
    parser.add_argument("-p", "--password", help="Mot de passe pour le conteneur", action="store_true")
    parser.add_argument("-r", "--ram", help="Taille de RAM en Mo", default=DEFAULT_RAM)
    parser.add_argument("-s", "--storage", help="Taille du stockage en Go", default=DEFAULT_STORAGE)
    parser.add_argument("--start", help="Démarrer le conteneur après la création", action="store_true")
    parser.add_argument("-t", "--template", help="Nom du template", default=None)
    parser.add_argument("-g", "--group", help="Nom du groupe d'utilisateurs", default=None)
    args = parser.parse_args()

    CTNumber = args.number if args.number else get_next_ct_number()
    template = args.template or list_templates()

    if args.password:
        password = getpass.getpass(prompt='Veuillez entrer le mot de passe pour le conteneur: ')
    else:
        password = DEFAULT_PASSWORD

    if args.group:
        users = get_users_from_group(args.group)
        if not users:
            logger.error(f"Aucun utilisateur trouvé dans le groupe {args.group}.")
            return

        roles = list_roles()
        if not roles:
            logger.error("Impossible de récupérer les rôles disponibles.")
            return

        role_choice = input("Veuillez entrer le numéro du rôle à attribuer aux utilisateurs : ")
        try:
            role_selected = roles[int(role_choice)]
        except (ValueError, KeyError):
            logger.error("Choix invalide. Opération annulée.")
            return

        for user in users:
            container_id = get_next_ct_number()
            container_name = f"CT{container_id}-{user}"
            create_container(
                password=password,
                ram=args.ram,
                cpu=args.cpu,
                storage=args.storage,
                CTNumber=container_id,
                template=template,
                node=args.node,
                name=container_name
            )
            assign_permissions(container_id, user, role_selected)
            logger.info(f"Conteneur '{container_name}' créé avec ID {container_id} et rôle '{role_selected}' attribué à {user}.")
    elif args.loop > 1:
        create_multiple_containers(
            password=password,
            ram=args.ram,
            cpu=args.cpu,
            storage=args.storage,
            CTNumber=CTNumber,
            template=template,
            node=args.node,
            base_name=args.name if args.name else f"CT{CTNumber}",
            loop_count=args.loop,
            start_after_creation=args.start
        )
    else:
        create_container(
            password=password,
            ram=args.ram,
            cpu=args.cpu,
            storage=args.storage,
            CTNumber=CTNumber,
            template=template,
            node=args.node,
            name=args.name if args.name else f"CT{CTNumber}"
        )
        logger.info(f"Conteneur '{args.name if args.name else f'CT{CTNumber}'}' créé avec succès !")
        if args.start:
            subprocess.run(f"pct start {CTNumber}", shell=True, check=True)
            logger.info(f"Conteneur {CTNumber} démarré.")

if __name__ == "__main__":
    main()