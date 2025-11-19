#!/usr/bin/env bash
set -e

IFACE="wlan1"

echo "[*] Launching bettercap on $IFACE..."

sudo bettercap -iface $IFACE
