# Loan Approval System

A production-ready MLOps platform for automated loan approval decisions with real-time predictions, model explainability, and comprehensive monitoring.

## Overview

This system provides an end-to-end solution for loan approval automation, featuring machine learning model training, real-time prediction APIs, SHAP-based explainability, data drift detection, and operational monitoring dashboards.

## Architecture

The system follows a microservices architecture with three core services:

```
├── services/
│   ├── ml-pipeline/          # Model training and MLflow tracking
│   ├── prediction-api/        # FastAPI prediction service with SHAP
│   └── monitoring/            # Streamlit and Grafana dashboards
├── infrastructure/            # Docker Compose configurations
├── scripts/                  # Deployment and utility scripts
└── local_storage/            # Model artifacts and frontend assets
```

## Features

### Machine Learning Pipeline
- Automated model training with MLflow experiment tracking
- Model versioning and registry management
- Batch processing for scheduled retraining
- Data validation and quality checks

### Prediction API
- Real-time loan approval predictions via FastAPI
- SHAP-based model explainability
- Statistical data drift detection
- RESTful API with OpenAPI documentation
- Web-based application interface

### Monitoring & Observability
- Real-time monitoring dashboard (Streamlit)
- Advanced metrics visualization (Grafana)
- Prometheus metrics collection
- Automated drift detection and alerts
- Service health monitoring

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Git

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd ml-orchestration

# Start all services
./scripts/start_loan_pipeline.sh

# Verify services are running
curl http://localhost:8000/health
```

### Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Prediction API | http://localhost:8000 | Loan approval prediction API |
| API Documentation | http://localhost:8000/docs | Interactive API documentation |
| Web Interface | http://localhost:8000/app | Loan application interface |
| MLflow UI | http://localhost:5000 | Experiment tracking and model registry |
| Monitoring Dashboard | http://localhost:8501 | Real-time monitoring interface |
| Grafana Dashboard | http://localhost:3001 | Advanced metrics visualization |
| Prometheus | http://localhost:9090 | Metrics collection endpoint |

## API Endpoints

### Core Endpoints
- `POST /predict` - Generate loan approval prediction
- `POST /predict/explain` - Get prediction with SHAP explanations
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics

### Drift Detection
- `POST /drift/collect` - Collect data for drift analysis
- `GET /drift/metrics` - Retrieve current drift metrics
- `GET /drift/summary` - Get drift data collection summary

## Development

### Service Structure

Each service is self-contained with its own:
- Source code (`src/`)
- Tests (`tests/`)
- Configuration (`config/`)
- Dependencies (`pyproject.toml`)
- Dockerfile

### Building Services

```bash
# Build ML pipeline service
cd services/ml-pipeline
docker build -t ml-pipeline .

# Build prediction API service
cd services/prediction-api
docker build -t prediction-api .

# Build monitoring service
cd services/monitoring
docker build -t monitoring .
```

### Running Tests

```bash
# Test API service
cd services/prediction-api
python -m pytest tests/

# Test ML pipeline
cd services/ml-pipeline
python -m pytest tests/
```

## Deployment

### CI/CD Pipeline

The project includes automated deployment via GitHub Actions. See [CICD_SETUP.md](CICD_SETUP.md) for configuration details.

### Manual Deployment

```bash
# Run deployment script
./scripts/deploy.sh

# Check service status
docker-compose -f infrastructure/docker-compose.yml ps

# View logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

## Configuration

### Environment Variables

Key configuration files:
- `services/prediction-api/config/api_config.yaml` - API settings
- `services/ml-pipeline/config/mlflow_config.yaml` - MLflow configuration
- `infrastructure/docker-compose.yml` - Service orchestration

### Model Management

Trained models are stored in `local_storage/models/champion/`:
- `model.joblib` - Production model artifact
- `label_encoders.joblib` - Feature encoders

## Monitoring

### Metrics Collected
- Request rate and latency
- Error rates
- Model prediction distributions
- Data drift statistics
- Service health status

### Drift Detection

The system monitors:
- Statistical distribution changes (Kolmogorov-Smirnov test)
- Categorical feature drift (Chi-square test)
- Feature-level drift indicators
- Automated alert generation

## Documentation

- [CI/CD Setup Guide](CICD_SETUP.md)
- [Frontend Documentation](frontend/README.md)
- [Service Status](docs/RUNNING_STATUS.md)

## License

MIT License
