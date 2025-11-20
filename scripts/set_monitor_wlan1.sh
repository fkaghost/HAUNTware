#!/bin/bash
IFACE="wlan1"

sudo ip link set $IFACE down
sudo iw dev $IFACE set type monitor
sudo ip link set $IFACE up

iwconfig $IFACE
echo "[INFO] wlan1 is now in MONITOR MODE"
