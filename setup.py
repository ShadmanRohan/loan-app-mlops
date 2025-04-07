from setuptools import setup, find_packages

setup(
    name="airflow_mlops_project",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "scikit-learn",
        "mlflow",
        "joblib",
        "apache-airflow"
    ],
    package_data={
        "airflow_mlops_project": ["scripts/*", "dags/*"]
    }
) 