"""Drift trigger system for testing drift detection capabilities."""

import random
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DriftType(Enum):
    """Types of drift that can be triggered."""
    NUMERICAL_SHIFT = "numerical_shift"
    CATEGORICAL_SHIFT = "categorical_shift"
    DISTRIBUTION_CHANGE = "distribution_change"
    SUDDEN_DRIFT = "sudden_drift"
    GRADUAL_DRIFT = "gradual_drift"

class DriftTrigger:
    """Controls deliberate data drift injection for testing."""
    
    def __init__(self):
        self.is_active = False
        self.drift_type = None
        self.drift_intensity = 0.0
        self.drift_start_time = None
        self.drift_config = {}
        
    def start_drift(self, drift_type: str, intensity: float = 0.5, duration: Optional[int] = None) -> Dict[str, Any]:
        """Start drift injection with specified parameters."""
        try:
            drift_enum = DriftType(drift_type)
            self.is_active = True
            self.drift_type = drift_enum
            self.drift_intensity = intensity
            self.drift_start_time = datetime.now()
            self.drift_config = {
                "type": drift_type,
                "intensity": intensity,
                "duration": duration,
                "start_time": self.drift_start_time.isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Drift trigger activated: {drift_type} with intensity {intensity}",
                "config": self.drift_config
            }
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid drift type: {drift_type}. Valid types: {[t.value for t in DriftType]}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start drift: {str(e)}"
            }
    
    def stop_drift(self) -> Dict[str, Any]:
        """Stop drift injection and return to normal data generation."""
        self.is_active = False
        self.drift_type = None
        self.drift_intensity = 0.0
        self.drift_start_time = None
        self.drift_config = {}
        
        return {
            "status": "success",
            "message": "Drift trigger deactivated, returning to normal data generation"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current drift trigger status."""
        return {
            "is_active": self.is_active,
            "drift_type": self.drift_type.value if self.drift_type else None,
            "drift_intensity": self.drift_intensity,
            "start_time": self.drift_start_time.isoformat() if self.drift_start_time else None,
            "config": self.drift_config
        }
    
    def apply_drift_to_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply drift modifications to incoming data."""
        if not self.is_active or not self.drift_type:
            return data
        
        modified_data = data.copy()
        
        try:
            if self.drift_type == DriftType.NUMERICAL_SHIFT:
                modified_data = self._apply_numerical_shift(modified_data)
            elif self.drift_type == DriftType.CATEGORICAL_SHIFT:
                modified_data = self._apply_categorical_shift(modified_data)
            elif self.drift_type == DriftType.DISTRIBUTION_CHANGE:
                modified_data = self._apply_distribution_change(modified_data)
            elif self.drift_type == DriftType.SUDDEN_DRIFT:
                modified_data = self._apply_sudden_drift(modified_data)
            elif self.drift_type == DriftType.GRADUAL_DRIFT:
                modified_data = self._apply_gradual_drift(modified_data)
                
        except Exception as e:
            print(f"Error applying drift: {e}")
            return data
        
        return modified_data
    
    def _apply_numerical_shift(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply numerical drift by shifting means of numerical features."""
        # Key numerical features to shift
        numerical_features = [
            'age', 'annual_income', 'credit_score', 'loan_amount', 
            'monthly_debt_payments', 'savings_account_balance'
        ]
        
        for feature in numerical_features:
            if feature in data and isinstance(data[feature], (int, float)):
                # Shift by intensity * standard deviation
                shift_amount = self.drift_intensity * 50  # Base shift amount
                data[feature] = max(0, data[feature] + shift_amount)
        
        return data
    
    def _apply_categorical_shift(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply categorical drift by changing category distributions."""
        # Employment status drift - favor different employment types
        if 'employment_status' in data:
            if random.random() < self.drift_intensity:
                data['employment_status'] = random.choice(['Self-Employed', 'Contract'])
        
        # Education level drift - shift towards higher education
        if 'education_level' in data:
            if random.random() < self.drift_intensity:
                data['education_level'] = random.choice(['Master', 'PhD'])
        
        # Loan purpose drift - favor different purposes
        if 'loan_purpose' in data:
            if random.random() < self.drift_intensity:
                data['loan_purpose'] = random.choice(['Business', 'Personal'])
        
        return data
    
    def _apply_distribution_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply distribution changes to numerical features."""
        # Change the distribution of credit scores (make them generally lower)
        if 'credit_score' in data:
            if random.random() < self.drift_intensity:
                # Shift credit scores to be lower
                data['credit_score'] = max(300, data['credit_score'] - (self.drift_intensity * 100))
        
        # Change income distribution (make incomes generally higher)
        if 'annual_income' in data:
            if random.random() < self.drift_intensity:
                data['annual_income'] = data['annual_income'] * (1 + self.drift_intensity)
        
        return data
    
    def _apply_sudden_drift(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply sudden, dramatic changes to data."""
        # Sudden change in loan amounts (much higher)
        if 'loan_amount' in data:
            data['loan_amount'] = data['loan_amount'] * (1 + self.drift_intensity * 2)
        
        # Sudden change in credit scores (much lower)
        if 'credit_score' in data:
            data['credit_score'] = max(300, data['credit_score'] - (self.drift_intensity * 200))
        
        # Sudden change in employment patterns
        if 'employment_status' in data:
            data['employment_status'] = 'Self-Employed'  # Force to self-employed
        
        return data
    
    def _apply_gradual_drift(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply gradual drift that increases over time."""
        if not self.drift_start_time:
            return data
        
        # Calculate time elapsed since drift started
        elapsed_minutes = (datetime.now() - self.drift_start_time).total_seconds() / 60
        
        # Gradual increase in drift intensity
        time_factor = min(1.0, elapsed_minutes / 10)  # Max effect after 10 minutes
        current_intensity = self.drift_intensity * time_factor
        
        # Gradually shift numerical features
        if 'age' in data:
            data['age'] = max(18, data['age'] + (current_intensity * 10))
        
        if 'annual_income' in data:
            data['annual_income'] = data['annual_income'] * (1 + current_intensity * 0.5)
        
        return data
