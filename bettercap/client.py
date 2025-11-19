import requests
import threading
import time

class BettercapClient:
    def __init__(self, poll_interval=1.0):
        self.api = "http://127.0.0.1:8081/api"
        self.poll_interval = poll_interval
        self.stop_ev = threading.Event()
        self.thread = None
        self.probes = []
        self.last_update = 0

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_ev.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_ev.set()

    def get_snapshot(self):
        return list(self.probes), self.last_update

    def _run(self):
        session = requests.Session()

        while not self.stop_ev.is_set():
            try:
                r = session.get(f"{self.api}/wifi/probes")
                if r.status_code == 200:
                    data = r.json()
                    parsed = []

                    for p in data:
                        ssid = p.get("ssid", "<hidden>")
                        station = p.get("station", "?")
                        parsed.append({"ssid": ssid, "station": station})

                    self.probes = parsed[:300]
                    self.last_update = time.time()
            except:
                pass

            time.sleep(self.poll_interval)
