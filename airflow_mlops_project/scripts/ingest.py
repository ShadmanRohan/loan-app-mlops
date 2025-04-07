from sklearn.datasets import make_regression
import pandas as pd
import os
import logging
from typing import Tuple, Optional
from dataclasses import dataclass
import yaml
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataConfig:
    n_samples: int = 100
    n_features: int = 5
    noise: float = 0.1
    random_state: int = 42
    output_dir: str = "data"
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'DataConfig':
        """Load configuration from YAML file"""
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        return cls()  # Return default config if file doesn't exist

def ingest_data(config: Optional[DataConfig] = None) -> Path:
    """
    Generate synthetic regression data and save to CSV.
    
    Args:
        config: Configuration for data generation
        
    Returns:
        Path to the saved data file
        
    Raises:
        OSError: If unable to create output directory or save file
    """
    try:
        config = config or DataConfig()
        logger.info(f"Generating synthetic data with {config.n_features} features")
        
        # Generate data
        X, y = make_regression(
            n_samples=config.n_samples,
            n_features=config.n_features,
            noise=config.noise,
            random_state=config.random_state
        )
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        df["target"] = y
        
        # Save data
        output_dir = Path(config.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        output_path = output_dir / "regression_data.csv"
        df.to_csv(output_path, index=False)
        
        # Save metadata
        metadata = {
            "n_samples": config.n_samples,
            "n_features": config.n_features,
            "noise": config.noise,
            "random_state": config.random_state,
            "feature_names": df.columns.tolist(),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Data saved to {output_path}")
        logger.info(f"Metadata saved to {metadata_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}")
        raise 