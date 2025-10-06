"""Drift detection using statistical methods."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DriftDetector:
    """Detects data drift using statistical tests."""
    
    def __init__(self, reference_data: pd.DataFrame, drift_threshold: float = 0.05):
        self.reference_data = reference_data
        self.drift_threshold = drift_threshold
        self.numerical_features = self._get_numerical_features()
        self.categorical_features = self._get_categorical_features()
        
    def _get_numerical_features(self) -> List[str]:
        """Get numerical feature columns."""
        return self.reference_data.select_dtypes(include=[np.number]).columns.tolist()
    
    def _get_categorical_features(self) -> List[str]:
        """Get categorical feature columns."""
        return self.reference_data.select_dtypes(include=['object']).columns.tolist()
    
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect drift between reference and current data."""
        if current_data.empty:
            return {"status": "no_data", "message": "No current data available"}
        
        if len(current_data) < 10:
            return {"status": "insufficient_data", "message": f"Need at least 10 samples, got {len(current_data)}"}
        
        try:
            # Overall dataset drift
            dataset_drift = self._detect_dataset_drift(current_data)
            
            # Feature-level drift
            feature_drift = self._detect_feature_drift(current_data)
            
            # Calculate drift score
            drift_score = self._calculate_drift_score(feature_drift)
            
            return {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "dataset_drift": dataset_drift,
                "feature_drift": feature_drift,
                "drift_score": drift_score,
                "drift_detected": drift_score > 0.3,  # Threshold for drift detection
                "total_features": len(self.numerical_features) + len(self.categorical_features),
                "drifted_features": [f for f, d in feature_drift.items() if d.get('drift_detected', False)]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _detect_dataset_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect overall dataset drift."""
        try:
            # Compare basic statistics
            ref_stats = self.reference_data.describe()
            curr_stats = current_data.describe()
            
            # Calculate mean differences for numerical features
            mean_diffs = {}
            for col in self.numerical_features:
                if col in ref_stats.columns and col in curr_stats.columns:
                    ref_mean = ref_stats.loc['mean', col]
                    curr_mean = curr_stats.loc['mean', col]
                    mean_diffs[col] = abs(curr_mean - ref_mean) / (ref_mean + 1e-8)
            
            avg_mean_diff = np.mean(list(mean_diffs.values())) if mean_diffs else 0
            
            return {
                "drift_detected": avg_mean_diff > 0.2,
                "drift_score": avg_mean_diff,
                "mean_differences": mean_diffs
            }
            
        except Exception as e:
            return {"drift_detected": False, "drift_score": 0, "error": str(e)}
    
    def _detect_feature_drift(self, current_data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Detect drift for individual features."""
        feature_results = {}
        
        # Numerical features - KS test
        for col in self.numerical_features:
            if col in current_data.columns and col in self.reference_data.columns:
                try:
                    ref_values = self.reference_data[col].dropna()
                    curr_values = current_data[col].dropna()
                    
                    if len(ref_values) > 0 and len(curr_values) > 0:
                        # Kolmogorov-Smirnov test
                        ks_stat, ks_pvalue = stats.ks_2samp(ref_values, curr_values)
                        
                        # Calculate drift score
                        drift_score = 1 - ks_pvalue
                        
                        feature_results[col] = {
                            "drift_detected": ks_pvalue < self.drift_threshold,
                            "drift_score": drift_score,
                            "ks_statistic": ks_stat,
                            "ks_pvalue": ks_pvalue,
                            "feature_type": "numerical"
                        }
                    else:
                        feature_results[col] = {
                            "drift_detected": False,
                            "drift_score": 0,
                            "error": "Insufficient data"
                        }
                except Exception as e:
                    feature_results[col] = {
                        "drift_detected": False,
                        "drift_score": 0,
                        "error": str(e)
                    }
        
        # Categorical features - Chi-square test
        for col in self.categorical_features:
            if col in current_data.columns and col in self.reference_data.columns:
                try:
                    ref_values = self.reference_data[col].dropna()
                    curr_values = current_data[col].dropna()
                    
                    if len(ref_values) > 0 and len(curr_values) > 0:
                        # Get unique values
                        all_values = set(ref_values.unique()) | set(curr_values.unique())
                        
                        if len(all_values) > 1:
                            # Create frequency tables
                            ref_counts = ref_values.value_counts()
                            curr_counts = curr_values.value_counts()
                            
                            # Align counts
                            ref_aligned = [ref_counts.get(val, 0) for val in all_values]
                            curr_aligned = [curr_counts.get(val, 0) for val in all_values]
                            
                            # Chi-square test
                            chi2_stat, chi2_pvalue = stats.chisquare([ref_aligned, curr_aligned])
                            
                            drift_score = 1 - chi2_pvalue if not np.isnan(chi2_pvalue) else 0
                            
                            feature_results[col] = {
                                "drift_detected": chi2_pvalue < self.drift_threshold if not np.isnan(chi2_pvalue) else False,
                                "drift_score": drift_score,
                                "chi2_statistic": chi2_stat,
                                "chi2_pvalue": chi2_pvalue,
                                "feature_type": "categorical"
                            }
                        else:
                            feature_results[col] = {
                                "drift_detected": False,
                                "drift_score": 0,
                                "error": "Single category"
                            }
                    else:
                        feature_results[col] = {
                            "drift_detected": False,
                            "drift_score": 0,
                            "error": "Insufficient data"
                        }
                except Exception as e:
                    feature_results[col] = {
                        "drift_detected": False,
                        "drift_score": 0,
                        "error": str(e)
                    }
        
        return feature_results
    
    def _calculate_drift_score(self, feature_drift: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall drift score."""
        if not feature_drift:
            return 0.0
        
        drift_scores = [f.get('drift_score', 0) for f in feature_drift.values() if 'drift_score' in f]
        return np.mean(drift_scores) if drift_scores else 0.0
