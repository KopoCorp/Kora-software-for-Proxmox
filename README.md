# Kora software for Proxmox

## Kora c'est quoi ?
Kora est un outil open-source à déployer sur un **Proxmox vierge**. Il est destiné aux professeurs cherchant une solution sécurisée pour fournir des machines à leurs élèves. Ces machines seront utilisées pour des projets web, de compilation, de développement et de tests divers.

Lors du déploiement, Kora va configurer un **firewall**, fournir des scripts servant à lancer des conteneurs totalement automatisés (réseaux, update, accès SSH, ouverture de ports dans le firewall).

Kora déploiera également un **affichage web** ayant pour objectif de fournir une vue simple des conteneurs. Les élèves pourront allumer, réinitialiser ou éteindre leurs conteneurs attribués.

Le professeur pourra créer un conteneur et y intégrer les outils nécessaires à son cours ou utiliser ceux déjà conçus. Il pourra ensuite **déployer une copie** de ce conteneur à chaque élève. Kora gérera ces accès soit via une base de données autodeployée soit via un branchement à un **LDAP** déjà existant. L'accès au CT se fait via SSH. L'accès SSH se fait soit via le firewall soit via un VPN.

Le projet a pour objectif d'être en **"all in one"**, le rendant facile d'utilisation pour n'importe quel professeur avec des bases en Linux.


## Git

- changelog/
- scripts/
- installation/
- deploy.sh


### Changelog/

Ce répertoire va mettre en avant les modifications et les avancées du projet sous la forme **update-KV-x.x.md** au format Markdown.

### Installation/

Ce répertoire va lister toutes les dépendances nécessaires au déploiement de Kora. Il fournit également les scripts et les étapes du déploiement. *L'arborescence de ces scripts sera mise en place plus tard dans le projet.*

### Scripts/

Ce répertoire contient l'ensemble des scripts développés servant au lancement de conteneurs et aux fonctions de sécurité. Les scripts ne seront utilisables qu'une fois la configuration faite (voir deploy.sh).

### deploy.sh

Ce script est celui qu'il faut lancer pour configurer et installer Kora sur un Proxmox. Il va appeler différents scripts du répertoire **installation/** selon les besoins. Il va également configurer les scripts du répertoire **scripts/**.


## Installer Kora

Rien de plus simple, il vous suffit d'avoir un serveur Proxmox avec un accès internet.

Copiez le projet git, déplacez-vous dans le répertoire, et lancez le script deploy.sh. Celui-ci vous guidera dans le processus d'installation.

```bash
git clone https://github.com/ecole2600/SQ26A2S1007-Kora-software-for-Proxmox.git
cd SQ26A2S1007-Kora-software-for-Proxmox/
chmod +x deploy.sh
./deploy.sh
```