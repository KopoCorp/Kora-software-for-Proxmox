#! /bin/bash
### BEGIN INIT INFO
# Provides:       my-start-script
# Required-Start:    $local_fs $syslog
# Required-Stop:     $local_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts my-start-script
# Description:       starts my-start-script using start-stop-daemon
### END INIT INFO

# script /etc/init.d/kora_firewall.sh  (mode 700 - root)

# Déclaration des interfaces
wan_if='default'
lxc_if='vmbr1'

# Activation le IPv4 FORWARDING
echo 1 > /proc/sys/net/ipv4/ip_forward

# PROTECTION ANTI-SPOOFING
if [ -e /proc/sys/net/ipv4/conf/all/rp_filter ]
then
    for filtre in /proc/sys/net/ipv4/conf/*/rp_filter
    do
        echo 1 > $filtre
    done
fi

# BLOCAGE COMPLET ICMP (Optionnel)
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

# On flush le tout avant de débuter
iptables -F
iptables -X
iptables -t nat -F

# On définit les règles par défaut
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT

# Autoriser les connexions locales
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A FORWARD -o lo -j ACCEPT

# Autoriser tout le trafic sur LXC
iptables -A INPUT -i $lxc_if -j ACCEPT
iptables -A OUTPUT -o $lxc_if -j ACCEPT

# Ne pas casser les connexions établies
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

# Nat des conteneur vers internet
iptables -t nat -A POSTROUTING -s 10.80.0.0/16 -o $wan_if -j MASQUERADE

# HTTP + HTTPS Out
iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

# HTTP + HTTPS In
iptables  -A INPUT -i $wan_if -p tcp --dport 80 -j ACCEPT
iptables  -A INPUT -i $wan_if -p tcp --dport 443 -j ACCEPT

# SSH serveur
iptables  -A INPUT -i $wan_if -p tcp --dport 22 -j ACCEPT

# DNS client
iptables -A INPUT -i $wan_if -p udp --dport 53 -j ACCEPT

# REQUETES HTTPS POUR L'INTERFACE WEB DE PROXMOX
iptables -A INPUT -i $wan_if -p tcp --dport 8006 -j ACCEPT

# REQUETES PVE-EXPORTER - GRAFANA/PROMETHEUS
iptables -A INPUT -i $wan_if -p tcp --dport 9221 -j ACCEPT

# Inclure des règles NAT supplémentaires (facultatif)
source /etc/init.d/kora_nat_rules.config

echo "===== Firewall configuration completed on KORA ====="
