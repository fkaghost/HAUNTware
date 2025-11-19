# bettercap/client_wifi.py
import requests
import threading
import time


class BettercapWifiClient:
    """
    Simple polling client for Bettercap Wi-Fi access points.
    Uses the /api/wifi/ap endpoint and enables wifi.recon.
    """

    def __init__(self, poll_interval=1.0):
        self.poll_interval = poll_interval
        self.devices = []      # list of {"ssid", "bssid", "signal"}
        self.last_update = 0.0
        self._lock = threading.Lock()
        self._stop_ev = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_ev.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_ev.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._thread = None
        with self._lock:
            self.devices = []
            self.last_update = 0.0

    def get_snapshot(self):
        with self._lock:
            return list(self.devices), self.last_update

    def _run(self):
        base = "http://127.0.0.1:8081/api"
        wifi_ap_url = f"{base}/wifi/ap"
        session_url = f"{base}/session"

        s = requests.Session()

        # Try to enable wifi.recon
        try:
            s.post(session_url, json={"cmd": "wifi.recon on"}, timeout=1.0)
        except Exception:
            pass

        while not self._stop_ev.is_set():
            try:
                r = s.get(wifi_ap_url, timeout=1.0)
                if r.status_code == 200:
                    aps = r.json()
                    parsed = []
                    for ap in aps:
                        ssid  = ap.get("ssid") or "<hidden>"
                        bssid = ap.get("mac") or "?"
                        sig   = ap.get("rssi", -100)

                        try:
                            sig = int(sig)
                        except Exception:
                            sig = -100

                        if bssid != "?":
                            parsed.append({"ssid": ssid, "bssid": bssid, "signal": sig})

                    parsed.sort(key=lambda x: x["signal"], reverse=True)
                    with self._lock:
                        self.devices = parsed
                        self.last_update = time.time()

            except Exception:
                # Ignore timeouts / brief API hiccups
                pass

            self._stop_ev.wait(self.poll_interval)
