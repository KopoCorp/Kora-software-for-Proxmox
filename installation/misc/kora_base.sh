#!/bin/bash

# Configuration du répertoire de Kora
echo "Création des répertoires de Kora"
mkdir -p /etc/kora
mkdir -p /etc/kora/script

# Deplacement des scripts
echo "Ajout du Kobot"
cp -rf scripts/* /etc/kora/script/.

# Configuration du bashrc
echo "Ajout dans profile.d"
cp installation/misc/kora_rules.sh /etc/profile.d/kora_rules.sh

# Configuration du logo de Kora
echo "Ajout du nouveau logo Kora"
mkdir -p /usr/share/pve-manager/kora_image
cp installation/misc/image/kora_logo.png /usr/share/pve-manager/kora_image/logo-128.png
cp installation/misc/image/kora_prox_banner.png /usr/share/pve-manager/kora_image/proxmox_logo.png
ln -s /usr/share/pve-manager/kora_image/ /etc/kora/image
bash /etc/kora/script/misc/logo_update.sh

# Ajout de la mise à jour du logo dans la crontab
echo "Ajout du script pour le logo dans la crontab"
echo "0 2 * * * bash /etc/kora/script/misc/logo_update.sh" >> /var/spool/cron/crontabs/root
