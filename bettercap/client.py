# bettercap/client.py

import threading
import time
import requests


class BettercapWifiClient:
    """
    Polls Bettercap's API for WiFi AP data.
    Stores results in self.devices (list of dicts).
    """
    def __init__(self, poll_interval=1.0):
        self.poll_interval = poll_interval
        self.stop_ev = threading.Event()
        self.thread = None

        self.devices = []         # [{'ssid':..., 'bssid':..., 'signal':...}]
        self.last_update = 0.0
        self._lock = threading.Lock()

        # Bettercap API endpoint for WiFi
        self.url = "http://127.0.0.1:8081/api/wifi.ap"

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_ev.clear()
        self.thread = threading.Thread(target=self._poll, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_ev.set()
        if self.thread:
            self.thread.join(timeout=2)
        self.thread = None

        with self._lock:
            self.devices = []
            self.last_update = 0.0

    def get_snapshot(self):
        with self._lock:
            return list(self.devices), self.last_update

    def _poll(self):
        s = requests.Session()
        while not self.stop_ev.is_set():
            try:
                r = s.get(self.url, timeout=2)
                if r.status_code == 200:
                    data = r.json()

                    parsed = []
                    for ap in data.get("aps", []):
                        parsed.append({
                            "ssid": ap.get("ssid") or "<hidden>",
                            "bssid": ap.get("mac")  or "??:??:??:??:??:??",
                            "signal": int(ap.get("rssi", -100)),
                        })

                    parsed.sort(key=lambda x: x["signal"], reverse=True)

                    with self._lock:
                        self.devices = parsed[:200]
                        self.last_update = time.time()

            except Exception:
                pass

            self.stop_ev.wait(self.poll_interval)
