"""Drift data collector that integrates data collection with drift detection."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path

from .data_collector import DataCollector
from .drift_detector import DriftDetector

class DriftDataCollector:
    """Combines data collection and drift detection functionality."""
    
    def __init__(self, max_buffer_size: int = 1000, drift_threshold: float = 0.05):
        self.data_collector = DataCollector(max_buffer_size)
        self.drift_detector = None
        self.drift_threshold = drift_threshold
        self.reference_data_path = None
        self.last_drift_check = None
        self.drift_metrics = {}
        
    def load_reference_data(self, data_path: str) -> bool:
        """Load reference dataset for drift comparison."""
        try:
            if self.data_collector.load_reference_data(data_path):
                self.reference_data_path = data_path
                # Initialize drift detector with reference data
                self.drift_detector = DriftDetector(
                    self.data_collector.reference_data, 
                    self.drift_threshold
                )
                print(f"Drift detector initialized with {len(self.data_collector.reference_data)} reference samples")
                return True
            return False
        except Exception as e:
            print(f"Error loading reference data: {e}")
            return False
    
    def collect_request_data(self, request_data: Dict[str, Any]) -> None:
        """Collect a single request for drift analysis."""
        self.data_collector.collect_request(request_data)
    
    def calculate_drift(self) -> Dict[str, Any]:
        """Calculate drift metrics from collected data."""
        try:
            # Get current data
            current_data = self.data_collector.get_current_dataframe()
            
            if current_data is None or current_data.empty:
                return {
                    "status": "no_data",
                    "message": "No data available for drift analysis",
                    "data_points": 0
                }
            
            if len(current_data) < 10:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 10 samples, got {len(current_data)}",
                    "data_points": len(current_data)
                }
            
            # Check if drift detector is available
            if self.drift_detector is None:
                return {
                    "status": "no_reference",
                    "message": "No reference data loaded for drift comparison",
                    "data_points": len(current_data)
                }
            
            # Perform drift detection
            drift_results = self.drift_detector.detect_drift(current_data)
            
            if drift_results.get("status") == "ok":
                # Extract drift metrics
                dataset_drift = drift_results.get("dataset_drift", {})
                feature_drift = drift_results.get("feature_drift", {})
                
                # Calculate feature drift scores
                feature_scores = {}
                drifted_features = []
                
                for feature, results in feature_drift.items():
                    if isinstance(results, dict) and 'drift_score' in results:
                        feature_scores[feature] = results['drift_score']
                        if results.get('drift_detected', False):
                            drifted_features.append(feature)
                
                # Calculate overall metrics
                total_features = drift_results.get("total_features", 0)
                num_drifted = len(drifted_features)
                share_drifted = num_drifted / total_features if total_features > 0 else 0
                
                # Store metrics
                self.drift_metrics = {
                    "status": "ok",
                    "timestamp": drift_results.get("timestamp"),
                    "data_points": len(current_data),
                    "dataset_drift_detected": dataset_drift.get("drift_detected", False),
                    "dataset_drift_score": dataset_drift.get("drift_score", 0),
                    "number_of_drifted_features": num_drifted,
                    "share_of_drifted_features": share_drifted,
                    "drifted_features": drifted_features,
                    "feature_drift_scores": feature_scores,
                    "total_features": total_features
                }
                
                self.last_drift_check = datetime.now().isoformat()
                
                return self.drift_metrics
            else:
                return {
                    "status": "error",
                    "message": drift_results.get("message", "Drift detection failed"),
                    "data_points": len(current_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Drift calculation error: {str(e)}",
                "data_points": len(current_data) if current_data is not None else 0
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get drift data collection summary."""
        collector_summary = self.data_collector.get_summary()
        
        return {
            "status": "ok",
            "data_points_collected": collector_summary.get("total_requests", 0),
            "last_update": collector_summary.get("last_collection"),
            "reference_data_loaded": self.drift_detector is not None,
            "reference_samples": len(self.data_collector.reference_data) if self.data_collector.reference_data is not None else 0,
            "last_drift_check": self.last_drift_check,
            "drift_threshold": self.drift_threshold,
            "numerical_features": self.drift_detector.numerical_features if self.drift_detector else [],
            "categorical_features": self.drift_detector.categorical_features if self.drift_detector else []
        }
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the latest drift metrics without recalculating."""
        if self.drift_metrics:
            return self.drift_metrics
        else:
            return {
                "status": "no_data",
                "message": "No drift metrics available",
                "data_points": 0
            }
