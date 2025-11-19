#!/usr/bin/env bash
set -e

IFACE="wlan1"

echo "[*] Returning wlan1 to managed mode"
sudo ifconfig $IFACE down || true
sudo iwconfig $IFACE mode managed
sudo ifconfig $IFACE up

sudo nmcli dev set $IFACE managed yes || true

echo "[*] wlan1 is now in MANAGED MODE"
