#!/bin/bash
IFACE="wlan1"

sudo ip link set $IFACE down
sudo iw dev $IFACE set type managed
sudo ip link set $IFACE up

iwconfig $IFACE
echo "[INFO] wlan1 is now in MANAGED MODE"
