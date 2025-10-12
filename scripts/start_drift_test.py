#!/usr/bin/env python3
"""Standalone drift test script that modifies the dummy request generator to introduce drift."""

import requests
import time
import random
import json
from datetime import datetime

class DriftTestController:
    """Controls drift testing by modifying dummy request generation."""
    
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
        return {
            "status": "success",
            "message": f"Drift injection started: {drift_type}",
            "type": drift_type,
            "intensity": intensity
        }
    
    def stop_drift(self):
        """Stop drift injection."""
        self.drift_active = False
        self.drift_type = None
        self.drift_intensity = 0.0
        
        print("🛑 Drift injection stopped")
        return {
            "status": "success",
            "message": "Drift injection stopped"
        }
    
    def get_drift_status(self):
        """Get current drift status."""
        return {
            "is_active": self.drift_active,
            "drift_type": self.drift_type,
            "drift_intensity": self.drift_intensity
        }
    
    def modify_request_data(self, data: dict) -> dict:
        """Modify request data to introduce drift."""
        if not self.drift_active:
            return data
        
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
    
    def monitor_drift_detection(self, duration: int = 300):
        """Monitor drift detection for specified duration."""
        print(f"🔍 Monitoring drift detection for {duration} seconds...")
        print("=" * 60)
        
        start_time = time.time()
        check_interval = 30  # Check every 30 seconds
        
        while time.time() - start_time < duration:
            # Get drift metrics
            try:
                response = requests.get(f"{self.api_url}/drift/metrics", timeout=5)
                if response.status_code == 200:
                    metrics = response.json()
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Drift Metrics:")
                    print(f"   Data Points: {metrics.get('data_points', 0)}")
                    print(f"   Dataset Drift: {'DETECTED' if metrics.get('dataset_drift_detected', False) else 'NOT DETECTED'}")
                    print(f"   Drift Score: {metrics.get('dataset_drift_score', 0):.3f}")
                    print(f"   Drifted Features: {metrics.get('number_of_drifted_features', 0)}/{metrics.get('total_features', 0)}")
                    print(f"   Share Drifted: {metrics.get('share_of_drifted_features', 0):.1%}")
                    
                    if metrics.get('drifted_features'):
                        print(f"   Drifted Features: {metrics['drifted_features']}")
                else:
                    print(f"❌ Failed to get drift metrics: {response.status_code}")
            except Exception as e:
                print(f"❌ Error getting drift metrics: {e}")
            
            print("-" * 60)
            time.sleep(check_interval)

def main():
    """Main function to run drift tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test drift detection capabilities")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--drift-type", choices=[
        "numerical_shift", "categorical_shift", "sudden_drift", "gradual_drift"
    ], help="Type of drift to test")
    parser.add_argument("--intensity", type=float, default=0.5, help="Drift intensity (0.0-1.0)")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    
    args = parser.parse_args()
    
    controller = DriftTestController(args.api_url)
    
    if args.drift_type:
        print(f"🧪 Testing drift type: {args.drift_type}")
        print(f"   Intensity: {args.intensity}")
        print(f"   Duration: {args.duration} seconds")
        print()
        
        # Start drift
        result = controller.start_drift(args.drift_type, args.intensity)
        print(f"✅ {result['message']}")
        
        # Monitor drift detection
        controller.monitor_drift_detection(args.duration)
        
        # Stop drift
        controller.stop_drift()
    else:
        print("📊 Current drift status:")
        status = controller.get_drift_status()
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
