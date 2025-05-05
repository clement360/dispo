#!/usr/bin/env bash
#
# Simplified install of hostapd + dnsmasq for AP mode.
set -e

echo "[*] Installing hostapd & dnsmasq..."
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq

echo "[*] Stopping services for configuration..."
sudo systemctl stop hostapd || true
sudo systemctl stop dnsmasq || true

echo "[*] Writing minimal /etc/dnsmasq.conf ..."
cat <<EOF | sudo tee /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
EOF

echo "[*] Writing /etc/hostapd/hostapd.conf ..."
cat <<EOF | sudo tee /etc/hostapd/hostapd.conf
interface=wlan0
ssid=SalesTracker
hw_mode=g
channel=7
wmm_enabled=0
EOF

sudo sed -i 's|#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

echo "[*] Enabling and starting services..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq

echo "[+] AP configured. SSID: SalesTracker"