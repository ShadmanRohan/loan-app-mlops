import os
import time
import random
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")
INTERVAL_MIN = float(os.environ.get("INTERVAL_MIN", "0.5"))
INTERVAL_MAX = float(os.environ.get("INTERVAL_MAX", "1.5"))

def sample_payload():
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


