#!/bin/python3

## Utils contreset

import os
import getpass
import sys
import subprocess
import re
from urllib.parse import unquote
from config import logger, TEMPLATE_DIR

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kora_utils import is_valid_ct_number, container_exists

def get_container_status(CTNumber):
    """Check if the container is running using pct status."""
    try:
        command = ["pct", "status", str(CTNumber)]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        status_line = result.stdout.strip()  # Get the status output
        if "status: running" in status_line:
            return "running"
        elif "status: stopped" in status_line:
            return "stopped"
        else:
            return "unknown"  # Just in case it's neither
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get the status of container {CTNumber}: {e}")
        return None

def get_container_config(CTNumber):
    """Retrieve the configuration of a container using pct config."""
    try:
        command = ["pct", "config", str(CTNumber)]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout  # Return the configuration as text
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving configuration for CT {CTNumber}: {e}")
        return None

def stop_container(CTNumber):
    """Stop the container only if it's running."""
    status = get_container_status(CTNumber)
    if status == "running":
        try:
            logger.info(f"Stopping container {CTNumber}...")
            subprocess.run(["pct", "stop", str(CTNumber)], check=True)
            logger.info(f"Container {CTNumber} stopped successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop container {CTNumber}: {e}")
    elif status == "stopped":
        logger.info(f"Container {CTNumber} is already stopped, skipping stop.")
    else:
        logger.error(f"Unable to determine the status of container {CTNumber}.")

def destroy_container(CTNumber):
    """Destroy the container."""
    try:
        logger.info(f"Destroying container {CTNumber}...")
        subprocess.run(["pct", "destroy", str(CTNumber)], check=True)
        logger.info(f"Container {CTNumber} destroyed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to destroy container {CTNumber}: {e}")

def create_container(CTNumber, config):
    """Recreate the container using the saved configuration."""
    try:
        logger.info(f"Recreating container {CTNumber}...")
        template = extract_template_from_config(config)
        cpu = extract_cores_from_config(config)
        memory = extract_memory_from_config(config)
        rootfs = extract_rootfs_from_config(config)
        hostname = extract_hostname_from_config(config)

        net_interfaces = extract_net_interfaces_from_config(config)

        password = getpass.getpass(prompt='Veuillez entrer le mot de passe pour le conteneur: (5 caractères minimum sinon vous perdez le conteneur) ')

        # Construct the base command for pct create
        create_command = [
            "pct", "create", str(CTNumber),
            template,
            "--cores", str(cpu),
            "--memory", str(memory),
            "--rootfs", rootfs,
            "--hostname", hostname,
            "--password", password,
        ]

        # Add all the netX interfaces (net0, net1, etc.)
        for i, net in enumerate(net_interfaces):
            mac_address = parse_mac_address(net)
            if mac_address:
                create_command.extend([f"--net{i}", net])

        # Use subprocess.Popen to capture and filter the output
        process = subprocess.Popen(create_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Filter both the SSH key generation and SHA256 lines
        for line in process.stdout:
            if 'Creating SSH host key' not in line and 'done: SHA256:' not in line:
                print(line, end='')  # Print other output as usual

        # Wait for the process to complete
        process.wait()

        if process.returncode == 0:
            logger.info(f"Container {CTNumber} recreated successfully.")
        else:
            logger.error(f"Failed to recreate container {CTNumber}: {process.stderr.read()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to recreate container {CTNumber}: {e}")


def extract_hostname_from_config(config_text):
    """Extract the hostname from the configuration."""
    for line in config_text.splitlines():
        if "hostname" in line:
            return line.split(":")[1].strip()
    return None

def extract_template_from_config(config_text):
    """Extract the template from the configuration and ensure the full path."""
    for line in config_text.splitlines():
        if "description" in line:
            # Extraire la partie après "description:"
            parts = line.split(":", 1)
            if len(parts) > 1:
                raw_description = parts[1].strip()
                decoded_description = unquote(raw_description)  # Décoder les caractères encodés
                logger.debug(f"Description décodée : {decoded_description}")

                # Vérifier si la description contient "Template :"
                if "Template :" in decoded_description:
                    template_name = decoded_description.split("Template :")[1].strip()
                    logger.debug(f"Template extrait : {template_name}")
                    return os.path.join(TEMPLATE_DIR, template_name)

    logger.error("Template introuvable dans la configuration.")
    return None

def extract_cores_from_config(config_text):
    """Extract the number of cores from the configuration."""
    for line in config_text.splitlines():
        if "cores" in line:
            return line.split(":")[1].strip()
    return None

def extract_memory_from_config(config_text):
    """Extract the memory size from the configuration."""
    for line in config_text.splitlines():
        if "memory" in line:
            return line.split(":")[1].strip()
    return None

def extract_rootfs_from_config(config_text):
    """Extract the rootfs information, ensuring storage pool, disk number, and size are correctly formatted."""
    for line in config_text.splitlines():
        if "rootfs" in line:
            parts = line.split(":")
            storage_pool = parts[1].strip()  # e.g., "local-lvm"
            disk_info = parts[2].strip()  # Extract the disk information (e.g., "vm-101-disk-0,size=1G")
            size = disk_info.split("size=")[1]  # Extract the size part (e.g., "1G")
            return f"{storage_pool}:1,size={size}"  # Return the correct format (e.g., "local-lvm:1,size=1G")
    return None

def extract_net_interfaces_from_config(config_text):
    """Extract all netX interfaces from the configuration."""
    net_interfaces = []
    for line in config_text.splitlines():
        if line.startswith("net"):
            net_interfaces.append(line.split(": ", 1)[1].strip())  # Extract everything after "netX: "
    return net_interfaces

def parse_mac_address(net_config):
    """Extract and validate the MAC address from the network configuration."""
    # Search for the hwaddr key in the net_config string
    match = re.search(r'hwaddr=([A-Fa-f0-9:]+)', net_config)
    if match:
        mac_address = match.group(1)
        # Check if the MAC address is in the correct format
        if validate_mac_address(mac_address):
            return mac_address
        else:
            logger.error(f"Invalid MAC address format: {mac_address}")
            return None
    else:
        logger.error("No MAC address (hwaddr) found in network configuration")
        return None

def validate_mac_address(mac_address):
    """Validate the MAC address format (XX:XX:XX:XX:XX:XX)."""
    # Regular expression for a valid MAC address
    mac_regex = re.compile(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$')
    return bool(mac_regex.match(mac_address))
