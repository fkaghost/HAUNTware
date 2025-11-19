#!/usr/bin/env bash
set -e

IFACE="wlan1"

echo "[*] Stopping network manager on $IFACE"
sudo nmcli dev set $IFACE managed no || true
sudo ifconfig $IFACE down || true

echo "[*] Enabling monitor mode"
sudo iwconfig $IFACE mode monitor

sudo ifconfig $IFACE up

echo "[*] wlan1 is now in MONITOR MODE"
