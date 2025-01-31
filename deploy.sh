#!/bin/bash

# Initialisation de la variable de réponse
rep=""

# Installation des dépendances
read -p "Kora va installer les paquets nécessaires (Y/n) : " rep
if [[ "$rep" =~ ^[Yy]$ || -z "$rep" ]]; then
    echo "Installation des dépendances..."
    python3 installation/install-dependancies/install-dependancies.py
else
    echo "Skip de l'installation des dépendances. Kora risque de ne pas marcher correctement..."
fi

# Installation des répertoires de Kora et des addons visuels
read -p "Kora va installer ses addons (Y/n) : " rep
if [[ "$rep" =~ ^[Yy]$ || -z "$rep" ]]; then
    echo "Installation des répertoires de travail et des addons visuels..."
    bash installation/misc/kora_base.sh
else
    echo "Skip de l'installation des répertoires de travail. Kora risque de ne pas marcher correctement..."
fi

# Configuration des réseaux de CT et du firewall
echo "-----------"
echo "Kora va configurer son réseau et son firewall."
read -p "Si le réseau a déjà été configuré, refuser cette étape (Y/n) : " rep
if [[ "$rep" =~ ^[Yy]$ || -z "$rep" ]]; then
    echo "Configuration du réseau et du firewall..."
    python3 installation/reseau/kora_interfaces.py
else
    echo "Skip de la configuration réseau. Kora risque de ne pas marcher correctement..."
fi

## Creation du roles eleves

echo "-----------"
echo "ajout du role eleves"
pveum role add eleves -privs "VM.PowerMgmt VM.Audit VM.Console"


# Configuration des réseaux de CT et du firewall
echo "-----------"
read -p "Kora va installer un reverse proxy (Y/n) : " rep
if [[ "$rep" =~ ^[Yy]$ || -z "$rep" ]]; then
    echo "Configuration du reverse proxy..."
    python3 installation/reverseproxy/deploy_reverse_proxy.py
else
    echo "Pas d'installation du reverse proxy"
fi


#Fin de l'installation

python3 installation/misc/welcome.py
