#!/usr/bin/env python3
"""
Simple dummy request generator for testing the loan prediction API
"""
import os
import time
import requests
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'prediction-api', 'src'))

from demo.dummy_requests import sample_payload

API_URL = os.environ.get("API_URL", "http://localhost:8000")
INTERVAL_MIN = float(os.environ.get("INTERVAL_MIN", "1.0"))
INTERVAL_MAX = float(os.environ.get("INTERVAL_MAX", "3.0"))

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API is accessible at {API_URL}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API at {API_URL}: {e}")
        return False

def send_request(payload):
    """Send a request to the prediction API"""
    try:
        # Send prediction request
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', 'unknown')
            print(f"📊 Request sent - Prediction: {prediction}")
        else:
            print(f"⚠️  Prediction request failed with status {response.status_code}")
        
        # Send explain request (best effort)
        try:
            requests.post(f"{API_URL}/predict/explain", json=payload, timeout=8)
            print("🧠 Explain request sent")
        except Exception as e:
            print(f"⚠️  Explain request failed: {e}")
        
        # Send drift collection request (best effort)
        try:
            requests.post(f"{API_URL}/drift/collect", json=payload, timeout=5)
            print("📈 Drift data collected")
        except Exception as e:
            print(f"⚠️  Drift collection failed: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    print(f"🚀 Starting dummy request generator...")
    print(f"📍 Target API: {API_URL}")
    print(f"⏱️  Interval: {INTERVAL_MIN}-{INTERVAL_MAX} seconds")
    print("=" * 50)
    
    # Test API connection first
    if not test_api_connection():
        print("💡 Make sure the prediction API is running:")
        print("   docker-compose -f infrastructure/docker-compose.yml up prediction-api")
        sys.exit(1)
    
    print("🔄 Starting request generation loop...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        while True:
            payload = sample_payload()
            send_request(payload)
            
            sleep_time = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
            print(f"😴 Sleeping for {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping dummy request generator...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


