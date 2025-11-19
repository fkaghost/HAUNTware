#!/usr/bin/env bash
IFACE="wlx74da38e26865"
LOGDIR="$HOME/kismet-logs"
mkdir -p "$LOGDIR"

case "${1:-start}" in
    start)
        nmcli dev set "$IFACE" managed no || true
        exec /usr/local/bin/kismet --log-prefix "$LOGDIR" -c "$IFACE"
        ;;
    stop)
        kill -SIGTERM $(pidof kismet) 2>/dev/null || true
        nmcli dev set "$IFACE" managed yes || true
        ;;
esac

