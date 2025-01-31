import rich
from rich.console import Console
from rich import print
import subprocess
import os
import shutil
import sys

def get_default_interface():
    result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE, text=True)
    
    # Recherche la ligne contenant "default"
    for line in result.stdout.splitlines():
        if line.startswith("default"):
            return line.split()[4]
    
    return None

def ask_confirmation(interface):
    while True:
        # Demande à l'utilisateur de confirmer si l'interface est correcte
        print(f"Interface par défault détectée est '[bold #57b8ff]{interface}[/bold #57b8ff]'")
        response = input(f"Est-ce correct ? (Y/n): ").strip().lower()
        if response in ["o", "oui", "","yes","y"]:
            return interface  # Interface acceptée
        elif response in ["n", "non","no"]:
            return None  # Interface rejetée
        else:
            print("Réponse invalide. Veuillez répondre par O ou n.")

def ask_for_new_interface():
    while True:
        # Demande à l'utilisateur d'entrer manuellement une nouvelle interface
        new_interface = input("Veuillez entrer le nom de la nouvelle interface : ").strip()
        print(f"Vous avez entré [bold #57b8ff]{new_interface}[/bold #57b8ff]")
        confirmation = input(f"Est-ce correct ? (Y/n): ").strip().lower()
        if confirmation in ["o", "oui", "","yes","y"]:
            return new_interface  # Interface acceptée
        else:
            print("Veuillez réessayer.")

# Choix de l'interface réseaux
print("-------------------------------------------------------")
wan_if = get_default_interface()
wan_if=ask_confirmation(wan_if)
if not wan_if:
        response = input("Voulez-vous afficher la liste des interfaces avec la commande 'ip a' ? (Y/n): ").strip().lower()
        if response in ["o", "oui", "","yes","y"]:
            subprocess.run(['ip', 'a'])
            print("-------------------------------------------------------")
        wan_if = ask_for_new_interface()

    # Afficher l'interface validée

print(f"Interface validée : [bold #57b8ff]{wan_if}[/bold #57b8ff]")

# Écriture dans le fichier /etc/network/interfaces
print("Ecriture de l'interface virtuel")

with open("/etc/network/interfaces", "a") as interfaces:
    interfaces.write("\n\n#Configuration reseaux pour les CT\n")
    interfaces.write("auto vmbr1\n")
    interfaces.write("iface vmbr1 inet static\n")
    interfaces.write("        address 10.80.254.254/16\n")
    interfaces.write("        bridge-ports none\n")
    interfaces.write("        bridge-stp off\n")
    interfaces.write("        bridge-fd 0\n")
    interfaces.write("        post-up echo 1 > /proc/sys/net/ipv4/ip_forward\n")
    interfaces.write(f"        post-up iptables -t nat -A POSTROUTING -s '10.80.0.0/16' -o {wan_if} -j MASQUERADE\n")
    interfaces.write(f"        post-down iptables -t nat -D POSTROUTING -s '10.80.0.0/16' -o {wan_if} -j MASQUERADE\n")


print("-------------------------------------------------------")
print("Création du firewall et des règles nat...")
#copie des fichier nat & firewall
script_dir = os.path.dirname(os.path.realpath(__file__))
firewall_script = os.path.join(script_dir, 'kora_firewall.sh')
config_file = os.path.join(script_dir, 'kora_nat_rules.config')
dest_dir = '/etc/init.d/'
shutil.copy(firewall_script, dest_dir)
shutil.copy(config_file, dest_dir)

print("Configuration du firewall...")
#configuration du firewall

with open('/etc/init.d/kora_firewall.sh', 'r') as file:
    lines = file.readlines()

with open('/etc/init.d/kora_firewall.sh', 'w') as file:
    for line in lines:
    # Remplacer uniquement la ligne qui définit wan_if
        if line.startswith("wan_if='default'"):
            file.write(f"wan_if='{wan_if}'\n")
        else:
            file.write(line)


print("Démarrage du firewall...")
# activer le démarrage automatique du firewall
try:
    subprocess.run(['systemctl', 'enable', 'kora_firewall.sh'], check=True)
except subprocess.CalledProcessError as e:
    print("Erreur lors de la configuration du démarrage automatique.", file=sys.stderr)
    sys.exit(1)

# allumage du firewall
try:
    subprocess.run(['/etc/init.d/kora_firewall.sh', 'start'], check=True)
except subprocess.CalledProcessError as e:
    print("Erreur lors du démarrage du firewall.", file=sys.stderr)
    sys.exit(1)