#!/usr/bin/env bash
#
# Redirect all HTTP to Flask server & start portal.
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:5000
export FLASK_APP=led_sales_tracker.portal.portal_app
flask run --host=0.0.0.0 --port=5000