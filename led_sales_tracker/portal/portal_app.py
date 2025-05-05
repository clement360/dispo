"""
Flask mini-app that serves the captive-portal page.
"""
import os
from flask import Flask, render_template, request, redirect
from ..config import ENV_PATH

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ssid = request.form.get("ssid")
        passwd = request.form.get("password")
        amazon_id = request.form.get("amazon_id")
        amazon_secret = request.form.get("amazon_secret")
        refresh = request.form.get("refresh")

        # Save to .env
        with open(ENV_PATH, "a") as fp:
            fp.write(f"\nWIFI_SSID={ssid}")
            fp.write(f"\nWIFI_PASS={passwd}")
            fp.write(f"\nAMAZON_CLIENT_ID={amazon_id}")
            fp.write(f"\nAMAZON_CLIENT_SECRET={amazon_secret}")
            fp.write(f"\nAMAZON_REFRESH_TOKEN={refresh}")

        # TODO: trigger network reconfiguration / reboot
        return "Credentials saved. Rebooting..."

    return render_template("index.html")