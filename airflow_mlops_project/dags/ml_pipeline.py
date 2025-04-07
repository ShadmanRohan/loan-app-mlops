from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from airflow_mlops_project.scripts.ingest import ingest_data
from airflow_mlops_project.scripts.train import train_model
from airflow_mlops_project.scripts.deploy import deploy_model

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

dag = DAG(
    dag_id="mlops_regression_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="ML pipeline for training and deploying a regression model"
)

def ingest_task():
    """Generate synthetic regression data and save to CSV"""
    ingest_data()

def train_task():
    """Train model, evaluate, and save to model registry"""
    train_model()

def deploy_task():
    """Deploy the model and log deployment status"""
    deploy_model()

with dag:
    t1 = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_task,
        doc_md="""Generate synthetic regression data and save to CSV file.
        Creates features and target variable using scikit-learn."""
    )
    
    t2 = PythonOperator(
        task_id="train_model",
        python_callable=train_task,
        doc_md="""Train a linear regression model on the generated data.
        Evaluates performance and logs metrics to MLflow."""
    )
    
    t3 = PythonOperator(
        task_id="deploy_model",
        python_callable=deploy_task,
        doc_md="""Deploy the trained model by logging deployment status
        and recording final metrics."""
    )

    # Define task dependencies
    t1 >> t2 >> t3