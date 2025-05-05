#!/usr/bin/env bash
SERVICE_NAME="led-sales-tracker"
sudo cp systemd/$SERVICE_NAME.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start  $SERVICE_NAME
echo "Systemd service installed & started."