import threading
import httpx
import time
from ping3 import ping  # You need to `pip install ping3`

class Monitor:
    def __init__(self, interval, get_targets_callback, update_callback):
        """
        interval: seconds between checks
        get_targets_callback: function to fetch current list of URLs/IPs
        update_callback: function to pass status updates to the GUI
        """
        self.interval = interval
        self.get_targets = get_targets_callback
        self.update_status = update_callback
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            targets = self.get_targets()
            results = {}

            for url in targets:
                try:
                    if url.startswith("http://") or url.startswith("https://"):
                        start = time.time()
                        r = httpx.get(url, timeout=3)
                        latency = (time.time() - start) * 1000
                        results[url] = (200 <= r.status_code < 400, latency)
                    else:
                        latency_sec = ping(url, timeout=3)  # ping returns seconds or None
                        is_online = latency_sec is not None
                        latency = latency_sec * 1000 if is_online else 0
                        results[url] = (is_online, latency)
                except Exception as e:
                    print(f"Error checking {url}: {e}")
                    results[url] = (False, 0)

            self.update_status(results)
            time.sleep(self.interval)
