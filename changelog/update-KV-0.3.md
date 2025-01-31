### Mise à jour **V0.3** du projet Kora **KV-0.3**

- Ajout de plusieurs scripts de gestion des conteneurs LXC pour Proxmox
  - Ajout de **contcreate** : script pour creer des conteneurs a partir de modeles
    - Gestion des reseaux avec attribution automatique d'adresses IP statiques
    - Option pour choisir le mot de passe et le noeud d'installation du conteneur
    - Ajout de l'option d'interactivite ou d'automatisation complete
    - Gestion des logs avec `rich` pour ameliorer la lisibilite
  - Ajout de **contdestroy** : script pour detruire des conteneurs
    - Prise en charge de la destruction forcee des conteneurs
    - Gestion des conteneurs invalides et affichage des statistiques detaillees
    - Auto-confirmation pour l'arret et la destruction des conteneurs
    - Integration des logs pour chaque action realisee
  - Ajout de **contemplate** : script pour convertir un conteneur en modele (template)
    - Verification de l'etat du conteneur avant conversion
    - Renommage du fichier dump pour correspondre au nom du template
    - Option pour automatiser le processus ou suivre les confirmations manuelles
  - Ajout de **contreset** : script de reinitialisation des conteneurs
    - Gestion de la reinstallation des conteneurs a partir des modeles existants
