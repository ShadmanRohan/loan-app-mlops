import os
import shutil
import mlflow
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml
from pathlib import Path
import joblib
from sklearn.base import BaseEstimator
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    model_dir: str = "model_registry"
    production_dir: str = "production"
    min_r2_score: float = 0.7
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'DeploymentConfig':
        """Load configuration from YAML file"""
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        return cls()

def validate_model(run_id: str, config: DeploymentConfig) -> bool:
    """
    Validate model metrics against deployment criteria
    """
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    metrics = run.data.metrics
    
    # Check R² score
    if metrics.get('r2', 0) < config.min_r2_score:
        logger.warning(f"Model R² score {metrics.get('r2')} below threshold {config.min_r2_score}")
        return False
    
    return True

def deploy_model(config: Optional[DeploymentConfig] = None) -> Dict[str, Any]:
    """
    Deploy the latest model to production if it meets quality criteria.
    
    Args:
        config: Deployment configuration
        
    Returns:
        Dictionary containing deployment information
        
    Raises:
        ValueError: If no suitable model found or deployment criteria not met
    """
    try:
        config = config or DeploymentConfig()
        logger.info("Starting model deployment")
        
        # Get the latest run
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=["0"],
            order_by=["start_time DESC"],
            max_results=1
        )
        
        if not runs:
            raise ValueError("No model runs found")
            
        latest_run = runs[0]
        
        # Validate model
        if not validate_model(latest_run.info.run_id, config):
            raise ValueError("Model did not meet deployment criteria")
        
        # Set up production directory
        prod_dir = Path(config.production_dir)
        prod_dir.mkdir(exist_ok=True, parents=True)
        
        # Load model from MLflow
        model_path = f"runs:/{latest_run.info.run_id}/model"
        model = mlflow.sklearn.load_model(model_path)
        
        # Save to production
        timestamp = latest_run.info.start_time
        prod_model_path = prod_dir / f"model_{timestamp}.joblib"
        joblib.dump(model, prod_model_path)
        
        # Create symlink for latest
        latest_link = prod_dir / "model_latest.joblib"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(prod_model_path)
        
        # Save deployment metadata
        metadata = {
            "model_id": latest_run.info.run_id,
            "deployment_timestamp": latest_run.info.start_time,
            "metrics": latest_run.data.metrics,
            "parameters": latest_run.data.params
        }
        
        metadata_path = prod_dir / "deployment_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Log deployment to MLflow
        with mlflow.start_run(run_id=latest_run.info.run_id):
            mlflow.log_param("deployment_status", "deployed")
            mlflow.log_param("production_path", str(prod_model_path))
        
        logger.info(f"Model {latest_run.info.run_id} deployed to {prod_model_path}")
        logger.info(f"Deployment metadata saved to {metadata_path}")
        
        return {
            "model_id": latest_run.info.run_id,
            "production_path": str(prod_model_path),
            "metrics": latest_run.data.metrics
        }
        
    except Exception as e:
        logger.error(f"Error during model deployment: {str(e)}")
        raise 