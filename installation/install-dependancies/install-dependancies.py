from config import DEPENDANCE_DIR
from utils import (
    find_dependency_files,
    identify_file_type,
    read_dependencies,
    is_software_installed,
    install_software,
    is_package_installed,
    install_python_package,
    print_summary,
    logger
)


def main():
    """Script principal pour installer les dépendances."""
    dependency_files = sorted(find_dependency_files())  # Trie les fichiers par ordre alphabétique

    if not dependency_files:
        logger.info("Aucun fichier de dépendances trouvé.")
        return

    # Compteurs
    installed_python = 0
    already_installed_python = 0
    installed_software = 0
    already_installed_software = 0
    empty_files = 0
    unknown_files = 0

    for dep_file in dependency_files:
        file_type = identify_file_type(dep_file)

        if file_type == "python":
            logger.info(f"Traitement des dépendances Python depuis : {dep_file}")
            python_dependencies = read_dependencies(dep_file)

            for package in python_dependencies:
                if is_package_installed(package):
                    logger.info(f"Le package Python {package} est déjà installé, passage.")
                    already_installed_python += 1
                else:
                    if install_python_package(package):
                        installed_python += 1

        elif file_type == "software":
            logger.info(f"Traitement des logiciels via apt depuis : {dep_file}")
            apt_dependencies = read_dependencies(dep_file)

            for software in apt_dependencies:
                if is_software_installed(software):
                    logger.info(f"Le logiciel {software} est déjà installé, passage.")
                    already_installed_software += 1
                else:
                    if install_software(software):
                        installed_software += 1

        elif file_type == "empty":
            logger.info(f"Le fichier {dep_file} est vide ou ne contient que des commentaires, passage.")
            empty_files += 1

        else:
            logger.warning(f"Type de fichier inconnu pour {dep_file}. Ignoré.")
            unknown_files += 1

    # Résumé
    logger.info("=== Résumé global ===")
    logger.info(f"  - {empty_files} fichier(s) vide(s).")
    logger.info(f"  - {unknown_files} fichier(s) de type inconnu.")
    print_summary(installed_python, already_installed_python, installed_software, already_installed_software)


if __name__ == "__main__":
    main()
