#!/bin/bash

# Check if the script is running as root (or with sudo)
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root or with sudo."
  exit 1
fi

# Define the username and password for the new user
username="prem"
password="PremR1s2B3w4N5p"

# Create the new user
useradd -m "$username"

# Set a password for the new user
echo -e "$password\n$password" | passwd "$username"

# Define a directory to which you want to grant permissions
directory="/app/mail"

# Grant read and write permissions to the new user for the specified directory
chmod -R 700 "$directory"
chown -R "$username:$username" "$directory"

# Add the user to additional groups as needed
# For example, adding the user to the sudo group for administrative privileges:
sudo usermod -aG sudo "$username"

# Print a message indicating that the user has been created and permissions granted
echo "User '$username' has been created with appropriate permissions."

cd /app/mail
su -c "celery -A your_app_name worker --loglevel=info" - "$username"