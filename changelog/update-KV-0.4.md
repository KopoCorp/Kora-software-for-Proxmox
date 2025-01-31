### Mise à jour **V0.4** du projet Kora **KV-0.4**

- Ajout d'un script de gestion des dépendances pour les environnements Proxmox
  - Ajout de **install-dependancies** : script pour gérer l'installation automatique des dépendances
    - Détection automatique des fichiers de dépendances dans un dossier dédié
    - Gestion des dépendances **Python** avec `pip`
      - Vérification préalable si le package est déjà installé
      - Installation des packages manquants
    - Gestion des logiciels système avec **apt**
      - Vérification préalable si le logiciel est déjà installé
      - Installation des logiciels manquants avec confirmation automatique
    - Log détaillé des actions effectuées pour chaque dépendance
      - Nombre de dépendances installées, déjà présentes ou ignorées
      - Gestion des fichiers vides ou mal formés avec des avertissements clairs
    - Identification des types de dépendances via la première ligne des fichiers (e.g., `# Python`, `# Apt`)
      - Flexibilité pour ajouter d'autres types de gestionnaires de dépendances dans le futur
    - Exécution du script possible depuis n'importe quel répertoire grâce à une résolution dynamique des chemins

- Optimisation et modularité
  - Intégration de la gestion centralisée des logs
  - Réorganisation des fonctions utilitaires dans un fichier `utils.py`
  - Centralisation de la configuration dans un fichier `config.py` pour une maintenance simplifiée
