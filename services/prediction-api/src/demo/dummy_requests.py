#!/usr/bin/env python3
"""
Background dummy request generator for the loan prediction API.
Runs inside the same container as the API to avoid network connectivity issues.
"""
import os
import time
import random
import requests
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000"  # Same container, so localhost works
INTERVAL_MIN = float(os.environ.get("DEMO_INTERVAL_MIN", "2.0"))
INTERVAL_MAX = float(os.environ.get("DEMO_INTERVAL_MAX", "5.0"))
ENABLED = os.environ.get("ENABLE_DEMO_REQUESTS", "false").lower() == "true"

def sample_payload():
    """Generate a random loan application payload"""
    return {
        "age": random.randint(21, 70),
        "annual_income": random.randint(30000, 150000),
        "credit_score": random.randint(550, 820),
        "experience": random.randint(1, 25),
        "loan_amount": random.randint(20000, 400000),
        "loan_duration": random.randint(1, 30),
        "number_of_dependents": random.randint(0, 4),
        "monthly_debt_payments": random.randint(200, 2500),
        "credit_card_utilization_rate": round(random.uniform(0.05, 0.8), 2),
        "number_of_open_credit_lines": random.randint(1, 8),
        "number_of_credit_inquiries": random.randint(0, 4),
        "debt_to_income_ratio": round(random.uniform(0.1, 0.6), 2),
        "bankruptcy_history": random.choice([0, 1]),
        "previous_loan_defaults": random.choice([0, 1]),
        "payment_history": round(random.uniform(0.7, 0.99), 2),
        "length_of_credit_history": random.randint(1, 25),
        "savings_account_balance": random.randint(1000, 80000),
        "checking_account_balance": random.randint(500, 20000),
        "total_assets": random.randint(50000, 500000),
        "total_liabilities": random.randint(10000, 250000),
        "monthly_income": random.randint(3000, 12000),
        "job_tenure": random.randint(0, 20),
        "net_worth": random.randint(-20000, 300000),
        "employment_status": random.choice(["Employed", "Self-Employed"]),
        "education_level": random.choice(["High School", "Bachelor", "Master"]),
        "marital_status": random.choice(["Single", "Married", "Divorced"]),
        "home_ownership_status": random.choice(["Own", "Rent", "Mortgage"]),
        "loan_purpose": random.choice(["Home", "Auto", "Education"]),
    }

def send_demo_request():
    """Send a demo request to the API"""
    try:
        payload = sample_payload()
        
        # Send prediction request
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', 'unknown')
            logger.info(f"🎯 Demo request - Prediction: {prediction}, Risk: {result.get('risk_score', 'N/A')}")
        else:
            logger.warning(f"⚠️ Demo prediction failed: {response.status_code}")
        
        # Send explain request (best effort)
        try:
            requests.post(f"{API_URL}/predict/explain", json=payload, timeout=8)
            logger.debug("🧠 Demo explain request sent")
        except Exception as e:
            logger.debug(f"Explain request failed: {e}")
        
        # Send drift collection request (best effort)
        try:
            requests.post(f"{API_URL}/drift/collect", json=payload, timeout=5)
            logger.debug("📈 Demo drift data collected")
        except Exception as e:
            logger.debug(f"Drift collection failed: {e}")
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"❌ Demo request failed: {e}")

def demo_request_loop():
    """Main loop for sending demo requests"""
    logger.info(f"🚀 Starting demo request generator...")
    logger.info(f"⏱️ Interval: {INTERVAL_MIN}-{INTERVAL_MAX} seconds")
    
    # Wait a bit for the API to start up
    time.sleep(10)
    
    # Test API connectivity
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ API is ready for demo requests")
        else:
            logger.error("❌ API health check failed")
            return
    except Exception as e:
        logger.error(f"❌ Cannot connect to API: {e}")
        return
    
    # Start sending requests
    while True:
        try:
            send_demo_request()
            sleep_time = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            logger.info("🛑 Demo request generator stopped")
            break
        except Exception as e:
            logger.error(f"Unexpected error in demo loop: {e}")
            time.sleep(5)  # Wait before retrying

def start_demo_generator():
    """Start the demo request generator in a background thread"""
    if not ENABLED:
        logger.info("Demo requests disabled (set ENABLE_DEMO_REQUESTS=true to enable)")
        return
    
    logger.info("🎭 Demo request generator enabled")
    demo_thread = threading.Thread(target=demo_request_loop, daemon=True)
    demo_thread.start()
    return demo_thread

if __name__ == "__main__":
    # Run directly for testing
    ENABLED = True
    demo_request_loop()


