"""Data collection for drift detection."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path

class DataCollector:
    """Collects and manages data for drift detection."""
    
    def __init__(self, max_buffer_size: int = 1000):
        self.max_buffer_size = max_buffer_size
        self.data_buffer = []
        self.reference_data = None
        self.last_drift_check = None
        self.drift_metrics = {}
        
    def load_reference_data(self, data_path: str) -> bool:
        """Load reference dataset for drift comparison."""
        try:
            if os.path.exists(data_path):
                self.reference_data = pd.read_csv(data_path)
                print(f"Loaded reference data: {len(self.reference_data)} samples")
                return True
            else:
                print(f"Reference data not found at {data_path}")
                return False
        except Exception as e:
            print(f"Error loading reference data: {e}")
            return False
    
    def collect_request(self, request_data: Dict[str, Any]) -> None:
        """Collect a single request for drift analysis."""
        # Add timestamp
        request_data['timestamp'] = datetime.now().isoformat()
        
        # Add to buffer
        self.data_buffer.append(request_data)
        
        # Maintain buffer size
        if len(self.data_buffer) > self.max_buffer_size:
            self.data_buffer = self.data_buffer[-self.max_buffer_size:]
    
    def get_current_dataframe(self) -> Optional[pd.DataFrame]:
        """Get current data as DataFrame."""
        if not self.data_buffer:
            return None
        
        try:
            df = pd.DataFrame(self.data_buffer)
            return df
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get data collection summary."""
        return {
            "total_requests": len(self.data_buffer),
            "buffer_size": self.max_buffer_size,
            "last_collection": self.data_buffer[-1]['timestamp'] if self.data_buffer else None,
            "reference_data_loaded": self.reference_data is not None,
            "reference_samples": len(self.reference_data) if self.reference_data is not None else 0
        }
