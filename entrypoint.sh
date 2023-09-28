#!/bin/bash

# Check if the script is running as root (or with sudo)
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root or with sudo."
  exit 1
fi

# Define the username and password for the new user
 Define the username and password for the new user
username="prem"
password="PremR1s2B3w4N5p"

# Create the new user
useradd -m "$username"

# Set a password for the new user
echo -e "$password\n$password" | passwd "$username"

# Set the working directory
cd /app

# Run the Celery worker with the correct app name and log level
su -c "celery -A mail worker --loglevel=info" - "$username"

# Grant permissions and perform other tasks as needed
# ...
# Add the user to additional groups as needed
# For example, adding the user to the sudo group for administrative privileges:
usermod -aG sudo "$username"


exec "$@"

