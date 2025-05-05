My RPi LED Device
This repository contains the skeleton for a Raspberry Pi project that:

Connects to Amazon Seller API to fetch sales data.
Displays that data on a 64x32 LED matrix via rpi-rgb-led-matrix.
Offers a captive portal for Wi-Fi provisioning and credential entry.
Supports systemd auto-start and optional Docker builds for OTA updates.
Directory Structure
(Explain the structure you see above.)

Setup
Clone this repository:
git clone https://github.com/your-user/my-rpi-led-device.git

Install dependencies:
cd my-rpi-led-device
npm install

Configure environment variables:
cp .env.example .env

Edit .env with your Amazon Seller API keys, Wi-Fi SSID, etc.
(Optional) Set up Wi-Fi captive portal:
scripts/configure-ap.sh

This script uses hostapd + dnsmasq.
Then run scripts/start-captive-portal.sh as needed.
(Optional) Install as a systemd service:
scripts/install-systemd.sh

Usage
npm start

Docker Usage
docker build -t my-rpi-led-device:latest .
docker run --privileged -p 80:80 my-rpi-led-device:latest

Contributing
Pull requests welcome.
