"""MLflow tracking module for experiment tracking and model registry."""

import os
from typing import Any, Dict, Optional, Union

import mlflow
from mlflow.tracking import MlflowClient


class MLflowTracker:
    """MLflow tracking class for managing experiments and logging metrics."""

    def __init__(
        self,
        experiment_name: str,
        tracking_uri: str = None,
        artifact_location: Optional[str] = None,
    ) -> None:
        """Initialize MLflow tracking.

        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: URI of the MLflow tracking server (defaults to env var or local)
            artifact_location: Location to store artifacts (defaults to env var or local)
        """
        self.experiment_name = experiment_name
        # Prefer docker-compose env; fallback to legacy local defaults
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.artifact_location = artifact_location or os.getenv("MLFLOW_ARTIFACT_ROOT")
        self.client = None
        self.experiment = None
        self.run = None

        self._initialize_tracking()

    def _initialize_tracking(self) -> None:
        """Initialize MLflow tracking client and experiment."""
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient()

        try:
            self.experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if self.experiment is None:
                experiment_id = mlflow.create_experiment(
                    name=self.experiment_name,
                    artifact_location=self.artifact_location,
                )
                self.experiment = mlflow.get_experiment(experiment_id)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MLflow tracking: {str(e)}")

    def start_run(self, run_name: Optional[str] = None) -> None:
        """Start a new MLflow run.

        Args:
            run_name: Optional name for the run
        """
        self.run = mlflow.start_run(
            experiment_id=self.experiment.experiment_id,
            run_name=run_name,
        )

    def end_run(self) -> None:
        """End the current MLflow run."""
        if self.run:
            mlflow.end_run()
            self.run = None

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to MLflow.

        Args:
            params: Dictionary of parameters to log
        """
        mlflow.log_params(params)

    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """Log metrics to MLflow.

        Args:
            metrics: Dictionary of metrics to log
        """
        mlflow.log_metrics(metrics)

    def log_model(
        self,
        model: Any,
        artifact_path: str,
        registered_model_name: Optional[str] = None,
    ) -> None:
        """Log a model to MLflow.

        Args:
            model: Model object to log
            artifact_path: Path to store the model artifact
            registered_model_name: Optional name to register the model
        """
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name,
        )

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log an artifact to MLflow.

        Args:
            local_path: Local path to the artifact
            artifact_path: Optional path to store the artifact
        """
        mlflow.log_artifact(local_path, artifact_path)

    def get_best_run(self, metric_name: str, mode: str = "max") -> Optional[str]:
        """Get the run ID with the best metric value.

        Args:
            metric_name: Name of the metric to optimize
            mode: Either 'max' or 'min'

        Returns:
            Run ID of the best run, or None if no runs found
        """
        runs = self.client.search_runs(
            [self.experiment.experiment_id],
            order_by=[f"metrics.{metric_name} {'DESC' if mode == 'max' else 'ASC'}"]
        )
        
        if not runs:
            return None
            
        return runs[0].info.run_id 