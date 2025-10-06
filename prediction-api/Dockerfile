FROM python:3.11-slim

WORKDIR /app

# Install dependencies with compatible numpy version for SHAP
RUN pip install "numpy<2.0" && \
    pip install fastapi uvicorn mlflow scikit-learn pandas pyyaml pydantic prometheus-client scipy shap==0.44.0

COPY src ./src
COPY config ./config

EXPOSE 8000

# Set PYTHONPATH and run the app
ENV PYTHONPATH=/app/src
CMD ["python", "-m", "src.api.app"]
