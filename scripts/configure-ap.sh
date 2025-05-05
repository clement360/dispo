#!/usr/bin/env bash

Example script to install/configure hostapd + dnsmasq for AP mode.
This is heavily simplified and should be adapted to your exact environment.
set -e

echo "Installing hostapd and dnsmasq..."
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq

Stop services so we can configure them
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

Write minimal configs (very simplified example)
/etc/dhcpcd.conf changes might be required
cat <<EOF | sudo tee /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.50,255.255.255.0,24h
EOF

cat <<EOF | sudo tee /etc/hostapd/hostapd.conf
interface=wlan0
ssid=RPiCaptivePortal
hw_mode=g
channel=7
wmm_enabled=0
auth_algs=1
ignore_broadcast_ssid=0
EOF

Update /etc/default/hostapd to point to hostapd.conf
sudo sed -i 's|#DAEMON_CONF="".*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

Start services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo systemctl restart dnsmasq

echo "AP mode configured. Wi-Fi SSID is RPiCaptivePortal (default)."