import os
import time
import requests
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'prediction-api', 'src'))

from demo.dummy_requests import sample_payload

API_URL = os.environ.get("API_URL", "http://localhost:8000")
INTERVAL_MIN = float(os.environ.get("INTERVAL_MIN", "0.5"))
INTERVAL_MAX = float(os.environ.get("INTERVAL_MAX", "1.5"))

def main():
    while True:
        payload = sample_payload()
        try:
            requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            requests.post(f"{API_URL}/predict/explain", json=payload, timeout=8)
            requests.post(f"{API_URL}/drift/collect", json=payload, timeout=5)
        except Exception:
            pass
        time.sleep(random.uniform(INTERVAL_MIN, INTERVAL_MAX))

if __name__ == "__main__":
    main()


