#!/bin/bash

# Installation script for auto-power-profile service
# Must be run with sudo

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "python3 is required but not installed. Aborting."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 is required but not installed. Aborting."; exit 1; }
command -v powerprofilesctl >/dev/null 2>&1 || { echo "powerprofilesctl is required but not installed. Aborting."; exit 1; }

# Define file paths
SCRIPT_SRC="auto-power-profile.py"
SERVICE_SRC="auto-power-profile.service"
SCRIPT_DEST="/usr/local/bin/auto-power-profile.py"
SERVICE_DEST="/etc/systemd/system/auto-power-profile.service"

# Check if source files exist
for file in "$SCRIPT_SRC" "$SERVICE_SRC"; do
    if [ ! -f "$file" ]; then
        echo "Source file $file not found in current directory. Aborting."
        exit 1
    fi
done

# Copy Python script
echo "Installing Python script to $SCRIPT_DEST..."
cp "$SCRIPT_SRC" "$SCRIPT_DEST"
chmod 755 "$SCRIPT_DEST"
chown root:root "$SCRIPT_DEST"

# Copy systemd service file
echo "Installing systemd service to $SERVICE_DEST..."
cp "$SERVICE_SRC" "$SERVICE_DEST"
chmod 644 "$SERVICE_DEST"
chown root:root "$SERVICE_DEST"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload || { echo "Failed to reload systemd."; exit 1; }

# Enable and start service
echo "Enabling and starting auto-power-profile.service..."
systemctl enable auto-power-profile.service || { echo "Failed to enable service."; exit 1; }
systemctl restart auto-power-profile.service || { echo "Failed to start service."; exit 1; }

# Verify service status
echo "Checking service status..."
systemctl status auto-power-profile.service --no-pager

echo "Installation completed successfully."
echo "View logs with: journalctl -u auto-power-profile.service"