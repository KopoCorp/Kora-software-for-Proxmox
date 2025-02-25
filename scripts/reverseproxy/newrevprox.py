#!/usr/bin/python3
import sys
import os

def create_revproxy_file(domain_name, destination_url):
    """ajoute un fichier de configuration du revprox"""
    directory = "/etc/nginx/Kora-reverse/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, domain_name)
    
    file_content = f"""server {{
    listen 443 ssl;
    server_name {domain_name};
    ssl_certificate /etc/pve/nodes/[HOSTNAME]/pveproxy-ssl.pem;
    ssl_certificate_key /etc/pve/nodes/[HOSTNAME]/pveproxy-ssl.key;

    location / {{
        proxy_pass http://{destination_url};
    }}
}}"""
    
    with open(file_path, 'w') as file:
        file.write(file_content)
    
    print(f"File created at {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: newrevprox.py <domain_name> <destination_url>:<destination_port>")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    destination_url = sys.argv[2]
    
    create_revproxy_file(domain_name, destination_url)
