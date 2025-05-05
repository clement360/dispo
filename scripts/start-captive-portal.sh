#!/usr/bin/env bash

Start Node captive portal on port 80, forcibly redirect DNS with dnsmasq, etc.
echo "Starting captive portal..."

In practice, you might add iptables rules to redirect all HTTP traffic to localhost:80
For example:
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:80
For now, just start the Node server:
npm start