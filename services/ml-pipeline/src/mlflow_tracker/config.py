"""MLflow configuration loader module."""
import os
from typing import Dict, Any

import yaml


class MLflowConfig:
    """Configuration loader for MLflow settings."""

    def __init__(self, config_path: str = "config/mlflow_config.yaml"):
        """Initialize MLflow configuration loader.

        Args:
            config_path (str): Path to the MLflow configuration file.
                Defaults to "config/mlflow_config.yaml".
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load MLflow configuration from YAML file.

        Returns:
            Dict[str, Any]: Configuration dictionary containing MLflow settings.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the configuration file is not valid YAML.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing configuration file: {e}")

    @property
    def tracking_uri(self) -> str:
        """Get MLflow tracking URI.

        Returns:
            str: MLflow tracking URI.
        """
        return self.config["tracking"]["uri"]

    @property
    def experiment_name(self) -> str:
        """Get MLflow experiment name.

        Returns:
            str: MLflow experiment name.
        """
        return self.config["tracking"]["experiment_name"]

    @property
    def artifact_location(self) -> str:
        """Get MLflow artifact location.

        Returns:
            str: MLflow artifact location.
        """
        return self.config["tracking"]["artifact_location"]

    @property
    def model_name(self) -> str:
        """Get MLflow model name.

        Returns:
            str: MLflow model name.
        """
        return self.config["model_registry"]["model_name"]

    @property
    def model_stage(self) -> str:
        """Get MLflow model stage.

        Returns:
            str: MLflow model stage.
        """
        return self.config["model_registry"]["stage"]

    @property
    def server_config(self) -> Dict[str, Any]:
        """Get MLflow server configuration.

        Returns:
            Dict[str, Any]: MLflow server configuration.
        """
        return self.config["server"] 