README.md
==========

LED Sales Tracker (Python Edition)
---------------------------------

A Raspberry Pi-powered gadget that fetches Amazon Seller sales metrics and shows them on a 64 × 32 RGB LED matrix.

* Runs **for real** on a Pi using `rpi-rgb-led-matrix`.  
* Runs **in emulation** on macOS / Windows / Linux via a `pygame` window for hassle-free development.  
* Provides a Wi-Fi access-point + captive-portal for first-time setup (enter home-network & Amazon creds).  
* Starts automatically on boot via **systemd**.  
* Optional Docker build for OTA updates.

---

Table of Contents
-----------------

1. Features  
2. Hardware / Software Requirements  
3. Quick-start (macOS / Dev machines)  
4. Deploy on Raspberry Pi  
5. Captive-Portal Workflow  
6. Configuration (.env)  
7. Directory Layout  
8. Service Management (systemd)  
9. Docker Usage (optional)  
10. Troubleshooting & Tips  

---

1  Features
-----------

* Real-time or periodic polling of Amazon Seller API.  
* Unified display API -> real matrix on Pi, `pygame` emulator elsewhere.  
* Flask web UI served as captive portal for onboarding.  
* Auto-recovery: if Wi-Fi or Amazon creds fail, device re-enters AP mode.  

---

2  Requirements
---------------

Hardware (production):

* Raspberry Pi 3/4  
* 64×32 or compatible RGB LED matrix + level shifter + ribbon cable  
* Micro-SD flashed with Raspberry Pi OS (Bullseye)

Software (dev):

* Python 3.9+  
* `pygame` (for emulation)  
* Git, make, etc.

Optional:

* Docker 20.x+ for container builds.

---

3  Quick-Start (Development on macOS / PC)
------------------------------------------

Clone & set up a virtual environment:

```bash
git clone https://github.com/your-user/led-sales-tracker.git
cd led-sales-tracker
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Copy the sample environment file and force emulator mode:

```bash
cp .env.example .env
export DISPLAY_BACKEND=emu   # or edit .env
python -m led_sales_tracker.main
```

A `pygame` window should open showing mocked sales numbers.  
Edit source files and restart the script (or use a file-watcher such as `watchfiles`) to live-reload while developing.

---

4  Deploy on Raspberry Pi
-------------------------

```bash
# On the Pi:
sudo apt-get update && sudo apt-get install -y git python3-pip
git clone https://github.com/your-user/led-sales-tracker.git
cd led-sales-tracker
sudo pip3 install -r requirements.txt
sudo pip3 install rpi-rgb-led-matrix        # real matrix bindings

# Configure access-point (first-boot provisioning)
sudo scripts/configure_ap.sh

# Enable auto-start service
sudo scripts/install_systemd.sh
```

Reboot. The Pi broadcasts a Wi-Fi SSID called **SalesTracker**; connect to it and finish onboarding (next section).

---

5  Captive-Portal Workflow
--------------------------

1. Device boots ➜ AP mode (`hostapd`, `dnsmasq`) ➜ DHCP hands out 192.168.4.0/24 addresses.  
2. `iptables` redirects all HTTP traffic to Flask server (`port 5000`).  
3. User visits any site ➜ browser lands on setup page.  
4. User submits:  
   * Home Wi-Fi SSID & password  
   * Amazon Seller API credentials  
5. Credentials are written to `.env`; device reboots, joins the provided Wi-Fi, and starts normal display mode.  
6. If later Wi-Fi or API auth fails, the service forces a return to AP/captive-portal for re-configuration.

---

6  Configuration (.env)
-----------------------

Key variables (see `.env.example`):

```
AMAZON_CLIENT_ID=
AMAZON_CLIENT_SECRET=
AMAZON_REFRESH_TOKEN=
WIFI_SSID=
WIFI_PASS=
REFRESH_INTERVAL=300           # seconds between polls
DISPLAY_BACKEND=auto           # auto | real | emu
```

`DISPLAY_BACKEND`  
• `auto` – choose real matrix on Pi, emulator elsewhere.  
• `real` – force hardware (useful in container).  
• `emu` – force pygame.

---

7  Directory Layout
-------------------

```
led-sales-tracker/
├─ led_sales_tracker/         ← main Python package
│   ├─ main.py                ← entry point
│   ├─ config.py              ← .env loader
│   ├─ display/               ← real-matrix & emulator drivers
│   ├─ api/                   ← Amazon Seller API wrapper
│   └─ portal/                ← Flask captive-portal app
├─ scripts/                   ← shell helpers (AP setup, systemd install)
├─ systemd/                   ← service file
├─ requirements.txt
├─ Dockerfile
└─ README.md
```

---

8  Service Management (systemd)
-------------------------------

The unit file `systemd/led-sales-tracker.service`:

```ini
[Service]
User=pi
WorkingDirectory=/home/pi/led-sales-tracker
ExecStart=/usr/bin/python3 -m led_sales_tracker.main
Restart=always
```

Install & enable:

```bash
sudo scripts/install_systemd.sh
# or manually:
sudo cp systemd/led-sales-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable led-sales-tracker
sudo systemctl start  led-sales-tracker
```

View logs:

```bash
journalctl -u led-sales-tracker -f
```

---

9  Docker Usage (Optional)
-------------------------

Build multi-arch image (works on desktop AND Pi):

```bash
docker build -t led-sales-tracker:latest .
docker run --privileged --env-file .env led-sales-tracker:latest
```

When running on Pi with real hardware, set `DISPLAY_BACKEND=real` and mount `/dev/mem` if required by `rpi-rgb-led-matrix`.

---

10  Troubleshooting & Tips
--------------------------

* **Emulator window freezes** – ensure the event loop isn’t blocked; the sample driver already pumps `pygame.event.get()`.  
* **AP not redirecting** – verify `iptables -t nat -L` shows the PREROUTING rule; see `scripts/start_captive_portal.sh`.  
* **rpi-rgb-led-matrix install errors** – make sure you’re on a Pi with headers: `sudo apt-get install -y build-essential python3-dev`.  
* **Logs** – service logs via `journalctl` are your friend (`-u led-sales-tracker -f`).  

---

Pull requests, bug reports, and feature suggestions are welcome!  
Happy hacking 🔴🟢🔵