#!/usr/bin/env bash

Copies the service file to systemd, enables it, and starts it.
SERVICE_NAME="my-rpi-led-device"
SERVICE_FILE="systemd/${SERVICE_NAME}.service"
INSTALL_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Installing systemd service..."
sudo cp "${SERVICE_FILE}" "${INSTALL_PATH}"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"

echo "Systemd service installed and started."