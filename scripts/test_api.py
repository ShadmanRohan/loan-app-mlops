#!/usr/bin/env python3
import requests
import json

def test_api():
    api_url = "http://localhost:8000"
    
    print("🔍 Testing API connectivity...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test prediction endpoint with sample data
    sample_payload = {
        "age": 30,
        "annual_income": 50000,
        "credit_score": 700,
        "experience": 5,
        "loan_amount": 100000,
        "loan_duration": 10,
        "number_of_dependents": 1,
        "monthly_debt_payments": 500,
        "credit_card_utilization_rate": 0.3,
        "number_of_open_credit_lines": 3,
        "number_of_credit_inquiries": 1,
        "debt_to_income_ratio": 0.2,
        "bankruptcy_history": 0,
        "previous_loan_defaults": 0,
        "payment_history": 0.95,
        "length_of_credit_history": 8,
        "savings_account_balance": 10000,
        "checking_account_balance": 3000,
        "total_assets": 150000,
        "total_liabilities": 50000,
        "monthly_income": 4000,
        "job_tenure": 3,
        "net_worth": 100000,
        "employment_status": "Employed",
        "education_level": "Bachelor",
        "marital_status": "Married",
        "home_ownership_status": "Mortgage",
        "loan_purpose": "Home"
    }
    
    try:
        response = requests.post(f"{api_url}/predict", json=sample_payload, timeout=10)
        print(f"✅ Prediction test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Prediction: {result.get('prediction', 'unknown')}")
            print(f"   Risk Score: {result.get('risk_score', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_api():
        print("\n🎉 API is working correctly!")
        print("You can now run the dummy request script.")
    else:
        print("\n❌ API has issues. Check the service status.")










