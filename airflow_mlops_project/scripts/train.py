import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os
import logging
from typing import Tuple, Dict, Any
from dataclasses import dataclass
import yaml
import json
from pathlib import Path
from datetime import datetime

# Configure MLflow
mlflow.set_tracking_uri("http://localhost:5000")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    test_size: float = 0.2
    random_state: int = 42
    model_dir: str = "model_registry"
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'TrainingConfig':
        """Load configuration from YAML file"""
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        return cls()

def load_and_validate_data(data_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and validate the training data"""
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
        
    # Load data
    df = pd.read_csv(data_path)
    
    # Load metadata if exists
    metadata_path = data_path.parent / "metadata.json"
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    # Validate data
    if "target" not in df.columns:
        raise ValueError("Data must contain 'target' column")
    
    return df, metadata

def evaluate_model(model: LinearRegression, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """Evaluate model performance"""
    y_pred = model.predict(X_test)
    return {
        "mse": mean_squared_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred)
    }

def train_model(data_path: str = "data/regression_data.csv", config: TrainingConfig = None) -> Dict[str, Any]:
    """
    Train and evaluate a regression model.
    
    Args:
        data_path: Path to training data
        config: Training configuration
        
    Returns:
        Dictionary containing model metrics and paths
        
    Raises:
        FileNotFoundError: If data file not found
        ValueError: If data validation fails
    """
    try:
        config = config or TrainingConfig()
        logger.info("Starting model training")
        
        # Load and validate data
        data_path = Path(data_path)
        df, metadata = load_and_validate_data(data_path)
        
        # Prepare data
        X = df.drop("target", axis=1)
        y = df["target"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=config.test_size,
            random_state=config.random_state
        )
        
        # Train model
        logger.info("Training model")
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Evaluate model
        metrics = evaluate_model(model, X_test, y_test)
        logger.info(f"Model metrics: {metrics}")
        
        # Save model and log to MLflow
        model_dir = Path(config.model_dir)
        model_dir.mkdir(exist_ok=True, parents=True)
        
        # Create versioned model path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_version = f"model_{timestamp}"
        model_path = model_dir / f"{model_version}.joblib"
        
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_params({
                "model_type": "LinearRegression",
                "test_size": config.test_size,
                "random_state": config.random_state,
                **metadata  # Log data generation parameters
            })
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            joblib.dump(model, model_path)
            
            # Log feature names
            mlflow.log_dict({"feature_names": X.columns.tolist()}, "feature_names.json")
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"MLflow run ID: {run.info.run_id}")
            
            return {
                "model_path": str(model_path),
                "mlflow_run_id": run.info.run_id,
                "metrics": metrics
            }
            
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise 