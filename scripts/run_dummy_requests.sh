#!/usr/bin/env bash
set -euo pipefail

# Start/stop a lightweight generator that sends requests to the Prediction API every few seconds
# Usage: ./scripts/run_dummy_requests.sh start|stop|status

GEN_NAME="loan-dummy-requests"
IMAGE="python:3.11-slim"
# Default to host API; works regardless of Docker network
API_URL_DEFAULT="http://host.docker.internal:8000"

start() {
  local api_url="${API_URL:-$API_URL_DEFAULT}"
  local interval_min="${INTERVAL_MIN:-2}"
  local interval_max="${INTERVAL_MAX:-4}"

  # If already running, exit
  if docker ps -q -f name="$GEN_NAME" >/dev/null 2>&1 && [ -n "$(docker ps -q -f name=$GEN_NAME)" ]; then
    echo "[INFO] $GEN_NAME already running"
    exit 0
  fi

  echo "[INFO] Starting dummy request generator against ${api_url} ..."
  docker run -d --rm \
    --name "$GEN_NAME" \
    --add-host=host.docker.internal:host-gateway \
    "$IMAGE" \
    bash -lc "pip install --no-cache-dir requests >/dev/null 2>&1 && python - <<'PY'
import requests, json, random, time
import os

api_url = os.environ.get('API_URL', 'http://prediction-api:8000')
interval_min = float(os.environ.get('INTERVAL_MIN', '2'))
interval_max = float(os.environ.get('INTERVAL_MAX', '4'))

def sample_payload():
    return {
        "age": random.randint(21, 70),
        "annual_income": random.randint(30000, 150000),
        "credit_score": random.randint(550, 820),
        "experience": random.randint(1, 25),
        "loan_amount": random.randint(20000, 400000),
        "loan_duration": random.randint(1, 30),  # years
        "number_of_dependents": random.randint(0, 4),
        "monthly_debt_payments": random.randint(200, 2500),
        "credit_card_utilization_rate": round(random.uniform(0.05, 0.8), 2),
        "number_of_open_credit_lines": random.randint(1, 8),
        "number_of_credit_inquiries": random.randint(0, 4),
        "debt_to_income_ratio": round(random.uniform(0.1, 0.6), 2),
        "bankruptcy_history": random.choice([0, 1]),
        "previous_loan_defaults": random.choice([0, 1]),
        "payment_history": round(random.uniform(0.7, 0.99), 2),
        "length_of_credit_history": random.randint(1, 25),  # years
        "savings_account_balance": random.randint(1000, 80000),
        "checking_account_balance": random.randint(500, 20000),
        "total_assets": random.randint(50000, 500000),
        "total_liabilities": random.randint(10000, 250000),
        "monthly_income": random.randint(3000, 12000),
        "job_tenure": random.randint(0, 20),  # years
        "net_worth": random.randint(-20000, 300000),
        "employment_status": random.choice(["Employed", "Self-Employed"]),
        "education_level": random.choice(["High School", "Bachelor", "Master"]),
        "marital_status": random.choice(["Single", "Married", "Divorced"]),
        "home_ownership_status": random.choice(["Own", "Rent", "Mortgage"]),
        "loan_purpose": random.choice(["Home", "Auto", "Education"]),
    }

while True:
    try:
        payload = sample_payload()
        # hit predict
        r = requests.post(f"{api_url}/predict", json=payload, timeout=5)
        # hit explain (best-effort)
        try:
            rexp = requests.post(f"{api_url}/predict/explain", json=payload, timeout=8)
        except Exception:
            pass
        # send to drift collector (best-effort)
        try:
            requests.post(f"{api_url}/drift/collect", json=payload, timeout=5)
        except Exception:
            pass
        print("OK", r.status_code)
    except Exception as e:
        print("ERR", e)
    time.sleep(random.uniform(interval_min, interval_max))
PY" \
    API_URL="$api_url" INTERVAL_MIN="$interval_min" INTERVAL_MAX="$interval_max"
}

stop() {
  echo "[INFO] Stopping $GEN_NAME ..."
  docker rm -f "$GEN_NAME" >/dev/null 2>&1 || true
}

status() {
  if [ -n "$(docker ps -q -f name=$GEN_NAME)" ]; then
    echo "[OK] $GEN_NAME is running"
  else
    echo "[STOPPED] $GEN_NAME is not running"
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) echo "Usage: $0 {start|stop|status}" ; exit 1 ;;
esac


