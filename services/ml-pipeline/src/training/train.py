"""Loan approval model training module with MLflow integration."""

import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import mlflow
import joblib
import yaml

logger = logging.getLogger(__name__)

class LoanApprovalTrainer:
    """Class for training loan approval models with MLflow tracking."""
    
    def __init__(self, config):
        """Initialize LoanApprovalTrainer with configuration."""
        self.config = config
        self.model_config = config["model"]
        self.data_config = config["data"]
        self.model = None
        self.label_encoders = {}
        self.metrics = {}
        
        # Ensure model directory exists
        self.model_dir = Path(self.model_config["model_dir"])
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self):
        """Load and preprocess loan data for training."""
        raw_data_path = Path(self.data_config["raw_dir"]) / "Loan.csv"
        df = pd.read_csv(raw_data_path)
        
        logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        
        # Create binary target: 1 if RiskScore < 50 (low risk = approved), 0 otherwise
        df['loan_approved'] = (df['RiskScore'] < 50).astype(int)
        
        # Select features for training
        feature_columns = [
            'Age', 'AnnualIncome', 'CreditScore', 'Experience', 'LoanAmount',
            'LoanDuration', 'NumberOfDependents', 'MonthlyDebtPayments',
            'CreditCardUtilizationRate', 'NumberOfOpenCreditLines',
            'NumberOfCreditInquiries', 'DebtToIncomeRatio', 'BankruptcyHistory',
            'PreviousLoanDefaults', 'PaymentHistory', 'LengthOfCreditHistory',
            'SavingsAccountBalance', 'CheckingAccountBalance', 'TotalAssets',
            'TotalLiabilities', 'MonthlyIncome', 'JobTenure', 'NetWorth'
        ]
        
        # Handle categorical variables
        categorical_columns = ['EmploymentStatus', 'EducationLevel', 'MaritalStatus', 
                            'HomeOwnershipStatus', 'LoanPurpose']
        
        X = df[feature_columns].copy()
        
        # Encode categorical variables
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        y = df['loan_approved']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        logger.info(f"Approval rate: {y.mean():.2%}")
        
        return X_train, X_test, y_train, y_test
    
    def train(self):
        """Train the loan approval model and track with MLflow."""
        logger.info("Starting loan approval model training")
        
        # Load data
        X_train, X_test, y_train, y_test = self.load_data()
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=self.model_config["hyperparameters"]["n_estimators"],
            max_depth=self.model_config["hyperparameters"]["max_depth"],
            random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        self.metrics = {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "approval_rate": y_test.mean()
        }
        
        logger.info(f"Training completed. Metrics: {self.metrics}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_test_pred)}")
        
        return self.metrics
    
    def save_model(self):
        """Save the trained model and encoders."""
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        # Save model
        model_path = self.model_dir / "model.joblib"
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save label encoders
        encoders_path = self.model_dir / "label_encoders.joblib"
        joblib.dump(self.label_encoders, encoders_path)
        logger.info(f"Label encoders saved to {encoders_path}")
        
        # Log model to MLflow
        mlflow.sklearn.log_model(self.model, "model")
        
        return str(model_path)

def train_model(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Train a loan approval model using the specified configuration.
    
    Args:
        config_path: Path to the pipeline configuration file
        
    Returns:
        Dictionary containing training metrics
    """
    try:
        # Load configuration
        with open(config_path) as f:
            config = yaml.safe_load(f)["pipeline"]
        
        # Set up MLflow tracking
        mlflow.set_tracking_uri("http://localhost:5000")
        experiment_name = "loan_approval_pipeline"
        
        # Create experiment if it doesn't exist
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
            else:
                experiment_id = experiment.experiment_id
        except Exception as e:
            logger.warning(f"Error setting up MLflow experiment: {str(e)}")
            experiment_id = mlflow.create_experiment(experiment_name)
        
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run():
            # Initialize and train model
            trainer = LoanApprovalTrainer(config)
            metrics = trainer.train()
            
            # Log metrics to MLflow
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            
            # Save model
            model_path = trainer.save_model()
            logger.info(f"Model saved to {model_path}")
            
            return metrics
        
    except Exception as e:
        logger.error(f"Error in train_model: {str(e)}")
        raise
