import rich
from rich.console import Console
from rich import print
import subprocess
import shutil
import sys

#recupere le hostname du proxmox
def get_hostname():
    result = subprocess.run(['hostname'], capture_output=True, text=True)
    return result.stdout.strip()


#modifie le  hostname des fichier script
def edit_file(hostname,file):

    with open(file, "r") as f:
        contenu = f.read()
        contenu = contenu.replace("[HOSTNAME]", hostname)

    with open(file, "w") as f:
        f.write(contenu)

    print("fichier",file,"modifier")


# Configuration du reverse proxy
print("-------------------------------------------------------")
print("Recuperation du hostname...")
hostname = get_hostname()

#modifcation du hostname dans les fichiers nginx
print("modifcation des fichier de configuration...")

edit_file(hostname,"installation/reverseproxy/default")
edit_file(hostname,"/etc/kora/script/reverseproxy/newrevprox.py")

#depalcement des fichier vers les bon repertoir et création des repertoir

subprocess.run(['mkdir', '-p', '/etc/nginx/Kora-reverse'])
subprocess.run(['ln', '-s', '/etc/nginx/Kora-reverse', '/root/reverse-proxy'])

shutil.copy("installation/reverseproxy/default","/etc/nginx/Kora-reverse/")
shutil.copy("installation/reverseproxy/nginx.conf",'/etc/nginx/')

print("Démarrage de nginx...")
# allumage de nginx
try:
    subprocess.run(['systemctl', 'start', 'nginx'], check=True)
except subprocess.CalledProcessError as e:
    print("Erreur lors du démarrage du firewall.", file=sys.stderr)
    sys.exit(1)
# allumage de nginx
try:
    subprocess.run(['systemctl', 'enable', 'nginx'], check=True)
except subprocess.CalledProcessError as e:
    print("Erreur lors du démarrage du firewall.", file=sys.stderr)
    sys.exit(1)