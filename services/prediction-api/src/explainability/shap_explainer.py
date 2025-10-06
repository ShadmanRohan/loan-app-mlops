"""SHAP explainer for loan approval predictions."""

import shap
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def convert_to_python_type(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_python_type(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_type(item) for item in obj]
    return obj

class LoanSHAPExplainer:
    """SHAP-based explainer for loan approval model."""
    
    def __init__(self, model, feature_names: List[str]):
        """Initialize SHAP explainer."""
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer based on model type."""
        try:
            if hasattr(self.model, 'estimators_'):
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("Initialized TreeExplainer for RandomForest")
            elif hasattr(self.model, 'coef_'):
                background = np.zeros((1, len(self.feature_names)))
                self.explainer = shap.LinearExplainer(self.model, background)
                logger.info("Initialized LinearExplainer for LogisticRegression")
            else:
                background = np.zeros((1, len(self.feature_names)))
                self.explainer = shap.KernelExplainer(self.model.predict_proba, background)
                logger.info("Initialized KernelExplainer (fallback)")
        except Exception as e:
            logger.error(f"SHAP explainer initialization failed: {e}")
            self.explainer = None
    
    def explain_prediction(self, features: np.ndarray, 
                          feature_values_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SHAP explanation for a prediction."""
        
        if self.explainer is None:
            return {"error": "SHAP explainer not available"}
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # For binary classification, take positive class
            if isinstance(shap_values, list) and len(shap_values) == 2:
                shap_values = shap_values[1]
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                shap_values = shap_values[:, :, 1]
            
            # Get base value
            base_value = self._get_base_value()
            
            # Create feature explanations
            feature_explanations = []
            for i, feature_name in enumerate(self.feature_names):
                original_value = feature_values_dict.get(feature_name, float(features[0][i]))
                display_value = self._format_value(feature_name, original_value)
                
                feature_explanations.append({
                    "feature": feature_name,
                    "display_name": feature_name.replace('_', ' ').title(),
                    "value": convert_to_python_type(original_value),
                    "display_value": display_value,
                    "shap_value": float(shap_values[0][i]),
                    "impact": "positive" if float(shap_values[0][i]) > 0 else "negative",
                    "abs_impact": abs(float(shap_values[0][i]))
                })
            
            # Sort by absolute impact
            sorted_features = sorted(feature_explanations, key=lambda x: x['abs_impact'], reverse=True)
            
            # Get top contributors
            positive_features = [f for f in sorted_features if f['impact'] == 'positive'][:5]
            negative_features = [f for f in sorted_features if f['impact'] == 'negative'][:5]
            
            # Calculate final value
            final_value = float(base_value) + float(np.sum(shap_values[0]))
            
            return {
                "base_value": float(base_value),
                "final_value": float(final_value),
                "total_shap_contribution": float(np.sum(shap_values[0])),
                "all_features": sorted_features,
                "top_positive_features": positive_features,
                "top_negative_features": negative_features,
                "waterfall_data": self._prepare_waterfall_data(base_value, sorted_features[:10]),
                "feature_count": len(self.feature_names),
                "available": True
            }
            
        except Exception as e:
            logger.error(f"SHAP calculation failed: {e}")
            return {"error": str(e), "available": False}
    
    def _get_base_value(self) -> float:
        """Get the base value from explainer."""
        try:
            if hasattr(self.explainer, 'expected_value'):
                base_value = self.explainer.expected_value
                if isinstance(base_value, np.ndarray):
                    return float(base_value[1] if len(base_value) > 1 else base_value[0])
                return float(base_value)
            return 0.5
        except:
            return 0.5
    
    def _format_value(self, feature_name: str, value: Any) -> str:
        """Format value for display."""
        if not isinstance(value, (int, float)):
            return str(value)
        
        money_features = ['annual_income', 'loan_amount', 'savings_account_balance',
                         'checking_account_balance', 'total_assets', 'total_liabilities',
                         'monthly_income', 'net_worth', 'monthly_debt_payments']
        
        if feature_name in money_features:
            return f"${value:,.0f}"
        elif feature_name in ['credit_card_utilization_rate', 'debt_to_income_ratio']:
            return f"{value * 100:.1f}%"
        elif feature_name == 'payment_history':
            return f"{value:.2f}"
        else:
            return f"{value:.1f}"
    
    def _prepare_waterfall_data(self, base_value: float, top_features: List[Dict]) -> List[Dict]:
        """Prepare waterfall data for visualization."""
        waterfall = [{"step": "Base Value", "value": float(base_value), "contribution": 0.0, "impact": "neutral"}]
        
        cumulative = float(base_value)
        for feat in top_features:
            cumulative += feat['shap_value']
            waterfall.append({
                "step": feat['display_name'],
                "value": float(cumulative),
                "contribution": float(feat['shap_value']),
                "impact": feat['impact'],
                "display_value": feat['display_value']
            })
        
        waterfall.append({"step": "Final Prediction", "value": float(cumulative), "contribution": 0.0, "impact": "final"})
        
        return waterfall
