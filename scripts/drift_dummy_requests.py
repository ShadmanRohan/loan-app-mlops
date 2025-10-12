#!/usr/bin/env python3
"""Dummy request generator with drift injection capabilities."""

import requests
import time
import random
import json
from datetime import datetime
import argparse

class DriftDummyRequestGenerator:
    """Generates dummy requests with optional drift injection."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.drift_active = False
        self.drift_type = None
        self.drift_intensity = 0.0
        
    def start_drift(self, drift_type: str, intensity: float = 0.5):
        """Start drift injection."""
        self.drift_active = True
        self.drift_type = drift_type
        self.drift_intensity = intensity
        print(f"🚀 Drift injection started: {drift_type} with intensity {intensity}")
    
    def stop_drift(self):
        """Stop drift injection."""
        self.drift_active = False
        self.drift_type = None
        self.drift_intensity = 0.0
        print("🛑 Drift injection stopped")
    
    def generate_sample_data(self) -> dict:
        """Generate sample loan application data."""
        # Base data generation
        data = {
            "age": random.randint(18, 80),
            "annual_income": random.randint(20000, 200000),
            "credit_score": random.randint(300, 850),
            "experience": random.randint(0, 50),
            "loan_amount": random.randint(5000, 500000),
            "loan_duration": random.randint(1, 30),
            "number_of_dependents": random.randint(0, 10),
            "monthly_debt_payments": random.randint(0, 5000),
            "credit_card_utilization_rate": random.uniform(0, 1),
            "number_of_open_credit_lines": random.randint(0, 20),
            "number_of_credit_inquiries": random.randint(0, 10),
            "debt_to_income_ratio": random.uniform(0, 1),
            "bankruptcy_history": random.randint(0, 1),
            "previous_loan_defaults": random.randint(0, 5),
            "payment_history": random.uniform(0, 1),
            "length_of_credit_history": random.randint(0, 50),
            "savings_account_balance": random.randint(0, 100000),
            "checking_account_balance": random.randint(0, 50000),
            "total_assets": random.randint(0, 1000000),
            "total_liabilities": random.randint(0, 500000),
            "monthly_income": random.randint(1000, 20000),
            "job_tenure": random.randint(0, 50),
            "net_worth": random.randint(-100000, 1000000),
            "employment_status": random.choice(["Employed", "Self-Employed"]),
            "education_level": random.choice(["High School", "Bachelor", "Master"]),
            "marital_status": random.choice(["Single", "Married", "Divorced"]),
            "home_ownership_status": random.choice(["Rent", "Own", "Mortgage"]),
            "loan_purpose": random.choice(["Home", "Auto", "Education"])
        }
        
        # Apply drift if active
        if self.drift_active:
            data = self._apply_drift(data)
        
        return data
    
    def _apply_drift(self, data: dict) -> dict:
        """Apply drift modifications to data."""
        modified_data = data.copy()
        
        try:
            if self.drift_type == "numerical_shift":
                # Shift numerical features
                if 'age' in modified_data:
                    modified_data['age'] = max(18, modified_data['age'] + (self.drift_intensity * 10))
                if 'annual_income' in modified_data:
                    modified_data['annual_income'] = modified_data['annual_income'] * (1 + self.drift_intensity)
                if 'credit_score' in modified_data:
                    modified_data['credit_score'] = max(300, modified_data['credit_score'] - (self.drift_intensity * 50))
                    
            elif self.drift_type == "categorical_shift":
                # Change categorical distributions
                if random.random() < self.drift_intensity:
                    if 'employment_status' in modified_data:
                        modified_data['employment_status'] = random.choice(['Self-Employed', 'Contract'])
                    if 'education_level' in modified_data:
                        modified_data['education_level'] = random.choice(['Master', 'PhD'])
                    if 'loan_purpose' in modified_data:
                        modified_data['loan_purpose'] = random.choice(['Business', 'Personal'])
                        
            elif self.drift_type == "sudden_drift":
                # Sudden dramatic changes
                if 'loan_amount' in modified_data:
                    modified_data['loan_amount'] = modified_data['loan_amount'] * (1 + self.drift_intensity * 2)
                if 'credit_score' in modified_data:
                    modified_data['credit_score'] = max(300, modified_data['credit_score'] - (self.drift_intensity * 100))
                if 'employment_status' in modified_data:
                    modified_data['employment_status'] = 'Self-Employed'
                    
            elif self.drift_type == "gradual_drift":
                # Gradual changes over time
                time_factor = min(1.0, time.time() / 1000)  # Gradual increase
                current_intensity = self.drift_intensity * time_factor
                
                if 'age' in modified_data:
                    modified_data['age'] = max(18, modified_data['age'] + (current_intensity * 5))
                if 'annual_income' in modified_data:
                    modified_data['annual_income'] = modified_data['annual_income'] * (1 + current_intensity * 0.3)
                    
        except Exception as e:
            print(f"Error applying drift: {e}")
            return data
        
        return modified_data
    
    def send_request(self, data: dict) -> bool:
        """Send request to API."""
        try:
            # Send to /predict endpoint
            response = requests.post(f"{self.api_url}/predict", json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prediction: {'Approved' if result['prediction']['approved'] else 'Rejected'} "
                      f"(Risk: {result['prediction']['risk_score']:.1f})")
                return True
            else:
                print(f"❌ Prediction failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def send_explanation_request(self, data: dict) -> bool:
        """Send request to /predict/explain endpoint."""
        try:
            response = requests.post(f"{self.api_url}/predict/explain", json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Explanation: {'Approved' if result['prediction']['approved'] else 'Rejected'} "
                      f"(Risk: {result['prediction']['risk_score']:.1f})")
                return True
            else:
                print(f"❌ Explanation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Explanation request failed: {e}")
            return False
    
    def send_drift_collect_request(self, data: dict) -> bool:
        """Send request to /drift/collect endpoint."""
        try:
            response = requests.post(f"{self.api_url}/drift/collect", json=data, timeout=5)
            if response.status_code == 200:
                print("✅ Drift data collected")
                return True
            else:
                print(f"❌ Drift collection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Drift collection request failed: {e}")
            return False
    
    def run_continuous_requests(self, interval: float = 1.0):
        """Run continuous requests with drift injection."""
        print(f"🚀 Starting continuous requests (interval: {interval}s)")
        if self.drift_active:
            print(f"   Drift active: {self.drift_type} (intensity: {self.drift_intensity})")
        print("=" * 60)
        
        request_count = 0
        while True:
            try:
                # Generate sample data
                data = self.generate_sample_data()
                
                # Send requests
                self.send_request(data)
                self.send_explanation_request(data)
                self.send_drift_collect_request(data)
                
                request_count += 1
                print(f"📊 Request #{request_count} completed")
                print("-" * 40)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping request generator...")
                break
            except Exception as e:
                print(f"❌ Error in request loop: {e}")
                time.sleep(interval)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Dummy request generator with drift injection")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--interval", type=float, default=1.0, help="Request interval in seconds")
    parser.add_argument("--drift-type", choices=[
        "numerical_shift", "categorical_shift", "sudden_drift", "gradual_drift"
    ], help="Type of drift to inject")
    parser.add_argument("--drift-intensity", type=float, default=0.5, help="Drift intensity (0.0-1.0)")
    parser.add_argument("--duration", type=int, help="Duration to run in seconds")
    
    args = parser.parse_args()
    
    generator = DriftDummyRequestGenerator(args.api_url)
    
    if args.drift_type:
        generator.start_drift(args.drift_type, args.drift_intensity)
    
    try:
        if args.duration:
            print(f"⏰ Running for {args.duration} seconds...")
            start_time = time.time()
            while time.time() - start_time < args.duration:
                data = generator.generate_sample_data()
                generator.send_request(data)
                generator.send_explanation_request(data)
                generator.send_drift_collect_request(data)
                time.sleep(args.interval)
        else:
            generator.run_continuous_requests(args.interval)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        if generator.drift_active:
            generator.stop_drift()

if __name__ == "__main__":
    main()
