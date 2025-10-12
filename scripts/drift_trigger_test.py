#!/usr/bin/env python3
"""Drift trigger test script to test drift detection capabilities."""

import requests
import time
import json
import argparse
from datetime import datetime

class DriftTriggerTester:
    """Test drift detection by triggering various drift patterns."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        
    def start_drift(self, drift_type: str, intensity: float = 0.5, duration: int = None):
        """Start drift injection."""
        try:
            response = requests.post(
                f"{self.api_url}/drift/trigger",
                params={
                    "drift_type": drift_type,
                    "intensity": intensity,
                    "duration": duration
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error starting drift: {e}")
            return None
    
    def stop_drift(self):
        """Stop drift injection."""
        try:
            response = requests.delete(f"{self.api_url}/drift/trigger")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error stopping drift: {e}")
            return None
    
    def get_drift_status(self):
        """Get current drift trigger status."""
        try:
            response = requests.get(f"{self.api_url}/drift/trigger/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting drift status: {e}")
            return None
    
    def get_drift_metrics(self):
        """Get current drift metrics."""
        try:
            response = requests.get(f"{self.api_url}/drift/metrics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting drift metrics: {e}")
            return None
    
    def monitor_drift_detection(self, duration: int = 300):
        """Monitor drift detection for specified duration."""
        print(f"🔍 Monitoring drift detection for {duration} seconds...")
        print("=" * 60)
        
        start_time = time.time()
        check_interval = 30  # Check every 30 seconds
        
        while time.time() - start_time < duration:
            # Get drift trigger status
            trigger_status = self.get_drift_status()
            if trigger_status:
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Drift Trigger: {'ACTIVE' if trigger_status['is_active'] else 'INACTIVE'}")
                if trigger_status['is_active']:
                    print(f"   Type: {trigger_status['drift_type']}, Intensity: {trigger_status['drift_intensity']}")
            
            # Get drift metrics
            metrics = self.get_drift_metrics()
            if metrics:
                print(f"📊 Drift Metrics:")
                print(f"   Data Points: {metrics.get('data_points', 0)}")
                print(f"   Dataset Drift: {'DETECTED' if metrics.get('dataset_drift_detected', False) else 'NOT DETECTED'}")
                print(f"   Drift Score: {metrics.get('dataset_drift_score', 0):.3f}")
                print(f"   Drifted Features: {metrics.get('number_of_drifted_features', 0)}/{metrics.get('total_features', 0)}")
                print(f"   Share Drifted: {metrics.get('share_of_drifted_features', 0):.1%}")
                
                if metrics.get('drifted_features'):
                    print(f"   Drifted Features List: {metrics['drifted_features']}")
            
            print("-" * 60)
            time.sleep(check_interval)
    
    def test_drift_scenarios(self):
        """Test various drift scenarios."""
        scenarios = [
            {
                "name": "Numerical Shift",
                "type": "numerical_shift",
                "intensity": 0.3,
                "duration": 120
            },
            {
                "name": "Categorical Shift", 
                "type": "categorical_shift",
                "intensity": 0.5,
                "duration": 120
            },
            {
                "name": "Sudden Drift",
                "type": "sudden_drift", 
                "intensity": 0.8,
                "duration": 120
            },
            {
                "name": "Gradual Drift",
                "type": "gradual_drift",
                "intensity": 0.4,
                "duration": 180
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🧪 Testing Scenario: {scenario['name']}")
            print("=" * 50)
            
            # Start drift
            result = self.start_drift(
                scenario['type'], 
                scenario['intensity'], 
                scenario['duration']
            )
            
            if result and result.get('status') == 'success':
                print(f"✅ Drift started: {result['message']}")
                
                # Monitor for the duration
                self.monitor_drift_detection(scenario['duration'])
                
                # Stop drift
                stop_result = self.stop_drift()
                if stop_result and stop_result.get('status') == 'success':
                    print(f"✅ Drift stopped: {stop_result['message']}")
                
                # Wait a bit before next scenario
                print("⏳ Waiting 30 seconds before next scenario...")
                time.sleep(30)
            else:
                print(f"❌ Failed to start drift: {result}")

def main():
    parser = argparse.ArgumentParser(description="Test drift detection capabilities")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--scenario", choices=[
        "numerical_shift", "categorical_shift", "distribution_change", 
        "sudden_drift", "gradual_drift"
    ], help="Specific drift scenario to test")
    parser.add_argument("--intensity", type=float, default=0.5, help="Drift intensity (0.0-1.0)")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    parser.add_argument("--all-scenarios", action="store_true", help="Test all drift scenarios")
    
    args = parser.parse_args()
    
    tester = DriftTriggerTester(args.api_url)
    
    print("🚀 Drift Trigger Test Suite")
    print("=" * 40)
    
    if args.all_scenarios:
        tester.test_drift_scenarios()
    elif args.scenario:
        print(f"🧪 Testing single scenario: {args.scenario}")
        result = tester.start_drift(args.scenario, args.intensity, args.duration)
        if result and result.get('status') == 'success':
            print(f"✅ Drift started: {result['message']}")
            tester.monitor_drift_detection(args.duration)
            tester.stop_drift()
        else:
            print(f"❌ Failed to start drift: {result}")
    else:
        print("📊 Current drift status:")
        status = tester.get_drift_status()
        print(json.dumps(status, indent=2))
        
        print("\n📈 Current drift metrics:")
        metrics = tester.get_drift_metrics()
        print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
