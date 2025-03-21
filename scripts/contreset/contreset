#!/bin/python3

import sys
from utils import is_valid_ct_number, container_exists, get_container_config, stop_container, destroy_container, create_container
from config import logger

def main(CTNumber):
    """Main function to reset a container to its default state."""
    # Check if the CT number is valid
    if not is_valid_ct_number(CTNumber):
        logger.error(f"Invalid container number: {CTNumber} is out of valid range.")
        sys.exit(1)

    # Check if the container exists
    if not container_exists(CTNumber):
        logger.error(f"Container {CTNumber} does not exist.")
        sys.exit(1)

    # Retrieve the current configuration
    config = get_container_config(CTNumber)
    if config is None:
        logger.error(f"Failed to retrieve configuration for CT {CTNumber}.")
        sys.exit(1)

    # Stop the container if it's running
    stop_container(CTNumber)

    # Destroy the container
    destroy_container(CTNumber)

    # Recreate the container with the same settings
    create_container(CTNumber, config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: contreset.py <CTNumber>")
        sys.exit(1)

    # Attempt to convert the input to an integer and handle invalid input
    try:
        CTNumber = int(sys.argv[1])
    except ValueError:
        logger.error("Container number must be a valid integer.")
        sys.exit(1)

    main(CTNumber)
