# ML Orchestration Platform

A comprehensive MLOps platform with service-oriented architecture, featuring ML pipeline automation, real-time prediction API, drift detection, and monitoring dashboards.

## 🏗️ Architecture

```
ml-orchestration/
├── 📁 ml-pipeline/                  # ML Pipeline Service (Self-sufficient)
│   ├── db/                          # MLflow database directory
│   │   └── mlflow.db                # SQLite database (188KB)
│   ├── mlflow.db                    # MLflow database (root level)
│   ├── mlruns/                      # MLflow experiment runs directory
│   ├── src/                         # Source code directory
│   │   ├── mlflow_tracker/          # MLflow experiment tracking
│   │   │   ├── __init__.py          # Package initialization
│   │   │   ├── config.py            # MLflow configuration (2.5KB)
│   │   │   └── tracking.py          # Experiment tracking logic (4KB)
│   │   └── training/                # Model training pipeline
│   │       ├── __init__.py          # Package initialization (empty)
│   │       └── train.py             # Training pipeline (6.7KB)
│   ├── Dockerfile                   # Container configuration (272B)
│   ├── poetry.lock                  # Poetry lock file (292KB)
│   ├── pyproject.toml               # Python dependencies (596B)
│   └── README.md                    # Service documentation (498B)
├── 📁 prediction-api/               # Prediction API Service (Self-sufficient)
│   ├── src/
│   │   ├── api/                     # FastAPI application
│   │   │   ├── app.py               # Main API endpoints
│   │   │   └── schemas.py           # Pydantic models
│   │   ├── drift/                   # Data drift detection
│   │   │   ├── __init__.py          # Package initialization
│   │   │   ├── drift_collector.py   # Unified drift collector
│   │   │   ├── drift_detector.py    # Statistical drift detection
│   │   │   └── data_collector.py    # Data collection
│   │   └── explainability/          # SHAP model explanations
│   │       ├── __init__.py          # Package initialization
│   │       └── shap_explainer.py    # SHAP explainer
│   ├── config/                      # API configuration
│   │   └── api_config.yaml          # API settings
│   ├── models/champion/             # Production model artifacts
│   │   ├── model.joblib             # Trained model (6.8MB)
│   │   └── label_encoders.joblib    # Label encoders (2KB)
│   ├── Dockerfile                   # Container configuration
│   ├── pyproject.toml               # Python dependencies
│   └── README.md                    # Service documentation
├── 📁 monitoring/                   # Monitoring Service (Self-sufficient)
│   ├── src/orchestration/           # Streamlit monitoring dashboard
│   │   └── start_evidently.py       # Monitoring dashboard (13KB)
│   ├── grafana/                     # Grafana dashboards & provisioning
│   │   ├── loan_approval_dashboard.json  # Dashboard configuration (19KB)
│   │   └── provisioning/             # Grafana provisioning
│   │       ├── dashboards/          # Dashboard provisioning (empty)
│   │       └── datasources/         # Data source configuration
│   │           └── api_datasource.yml # API data source (239B)
│   ├── prometheus/                  # Prometheus configuration
│   │   └── prometheus.yml           # Prometheus config (386B)
│   ├── Dockerfile                   # Container configuration
│   ├── pyproject.toml               # Python dependencies
│   └── README.md                    # Service documentation
├── 📁 infrastructure/               # Infrastructure & DevOps
│   └── docker-compose/              # Docker Compose configurations
│       ├── docker-compose.services.yml  # Main services orchestration (2.1KB)
│       └── monitoring/              # Monitoring stack configuration
│           ├── grafana/             # Grafana configuration
│           │   └── provisioning/     # Grafana provisioning (empty)
│           └── prometheus/          # Prometheus configuration
│               └── prometheus.yml   # Prometheus config
├── 📁 local_storage/frontend_dist/  # Professional UI (CDN-based)
│   ├── index.html                  # Main UI entry point
│   └── app.js                      # React application with professional design
├── 📁 data/                         # Data Storage
│   └── raw/                        # Raw datasets
│       └── Loan.csv                # Loan approval dataset
├── 📁 models/                       # Model artifacts storage
│   ├── model.joblib                # Trained model (6.8MB)
│   └── label_encoders.joblib       # Label encoders (2KB)
├── 📁 .cleanup_backup/              # Backup files
├── 🚀 start_loan_pipeline.sh        # Main orchestration script
├── 🔧 deploy_drift.sh               # Deploy drift monitoring
├── 🔄 rollback_drift.sh             # Rollback drift monitoring
├── 📊 RUNNING_STATUS.md             # Service status documentation
└── 📝 README.md                     # This file
```

## 🚀 Quick Start

```bash
# Start all services
./start_loan_pipeline.sh start

# Start with dummy request generator
./start_loan_pipeline.sh start --dummy

# Start with drift monitoring
./deploy_drift.sh
```

## 📊 Services & Ports

| Service | URL | Description |
|---------|-----|-------------|
| **ML Pipeline** | Batch Service | Model training & MLflow experiment tracking |
| **MLflow UI** | http://localhost:5001 | ML experiment tracking & model registry |
| **Prediction API** | http://localhost:8000 | Loan approval prediction API |
| **Professional UI** | http://localhost:8000/app | Modern business-grade loan application interface |
| **API Documentation** | http://localhost:8000/docs | Interactive API documentation |
| **Monitoring Dashboard** | http://localhost:8501 | Real-time monitoring with drift detection |
| **Grafana Dashboard** | http://localhost:3001 | Advanced metrics visualization |
| **Prometheus** | http://localhost:9090 | Metrics collection & querying |

## 🔧 API Endpoints

### Core Prediction
- `POST /predict` - Make loan predictions
- `POST /predict/explain` - Get predictions with SHAP explanations
- `GET /health` - Service health check

### Drift Detection
- `POST /drift/collect` - Collect data for drift analysis
- `GET /drift/metrics` - Get current drift metrics
- `GET /drift/summary` - Get drift data collection summary

### Monitoring
- `GET /metrics` - Prometheus metrics
- `GET /prometheus` - Prometheus endpoint

## 🎯 Key Features

### 🤖 ML Pipeline
- **Automated Training**: End-to-end model training pipeline
- **Experiment Tracking**: MLflow integration for experiment management
- **Model Registry**: Version control and model lifecycle management
- **Data Validation**: Automated data quality checks
- **Batch Processing**: Runs as scheduled batch jobs, not long-running service
- **Model Deployment**: Trains and registers champion models for production

### 🔮 Prediction API
- **Real-time Predictions**: FastAPI-based prediction service
- **Model Explanations**: SHAP integration for interpretable AI
- **Data Drift Detection**: Statistical monitoring of data distribution changes
- **Health Monitoring**: Comprehensive health checks and metrics
- **Professional UI**: Modern business-grade interface with custom data input
- **Resizable Interface**: Adjustable sidebar with collapsible AI decision sections

### 📊 Monitoring & Observability
- **Real-time Dashboard**: Streamlit-based monitoring interface
- **Drift Detection**: Automated detection of data and concept drift
- **Metrics Collection**: Prometheus-based metrics gathering
- **Visualization**: Grafana dashboards for advanced analytics

### 🔍 Data Drift Detection
- **Statistical Tests**: Kolmogorov-Smirnov and Chi-square tests
- **Feature-level Monitoring**: Individual feature drift detection
- **Reference Data**: Baseline comparison with historical data
- **Real-time Alerts**: Automated drift notifications

## 🛠️ Development

Each service is completely self-sufficient:

```bash
# Work on ML Pipeline
cd ml-pipeline
docker build -t ml-pipeline .
python -m pytest tests/

# Work on Prediction API
cd prediction-api
docker build -t prediction-api .
python -m pytest tests/

# Work on Monitoring
cd monitoring
docker build -t monitoring .
python -m pytest tests/
```

## 📝 Service Independence

Each service contains:
- ✅ **Source code** (`src/`)
- ✅ **Tests** (`tests/`)
- ✅ **Configuration** (`config/`)
- ✅ **Documentation** (`README.md`, `docs/`)
- ✅ **Scripts** (`scripts/`)
- ✅ **Dependencies** (`pyproject.toml`)
- ✅ **Containerization** (`Dockerfile`)

## 🧹 Clean Root Directory

The root directory is kept clean with only essential files:
- `start_loan_pipeline.sh` - Main orchestration script
- `deploy_drift.sh` - Deploy drift monitoring
- `rollback_drift.sh` - Rollback drift monitoring
- `README.md` - This file
- `RUNNING_STATUS.md` - Service status documentation

## 🔧 Advanced Features

### Data Drift Monitoring
```bash
# Deploy drift monitoring
./deploy_drift.sh

# Rollback drift monitoring
./rollback_drift.sh
```

### Professional UI Features
- **Modern Design**: Clean, professional interface suitable for business environments
- **Custom Data Input**: Add new customers through intuitive forms with validation
- **Resizable Sidebar**: Adjustable width for optimal workspace management
- **Collapsible Sections**: AI decision analysis sections that can be expanded/collapsed
- **Real-time Predictions**: Instant loan approval decisions with SHAP explanations
- **Professional Color Scheme**: Business-appropriate grays and neutrals

### Service Management
```bash
# Check service status
./start_loan_pipeline.sh status

# Stop all services
./start_loan_pipeline.sh stop

# View logs
./start_loan_pipeline.sh logs
```

## 📈 Monitoring Capabilities

### Real-time Metrics
- **Request Rate**: API requests per second
- **Response Time**: Average response latency
- **Error Rate**: Failed request percentage
- **Model Performance**: Prediction accuracy metrics

### Drift Detection
- **Data Drift**: Statistical changes in input data
- **Concept Drift**: Changes in model performance
- **Feature Drift**: Individual feature distribution changes
- **Alert System**: Automated drift notifications

### Visualization
- **Interactive Dashboards**: Real-time data visualization
- **Historical Trends**: Long-term performance tracking
- **Feature Analysis**: Detailed feature drift analysis
- **Model Insights**: SHAP explanation visualizations

## 🚀 Getting Started

1. **Clone the repository**
2. **Run the orchestration script**: `./start_loan_pipeline.sh start --dummy`
3. **Access the professional UI**: http://localhost:8000/app
4. **Access the monitoring dashboard**: http://localhost:8501
5. **Explore the API documentation**: http://localhost:8000/docs
6. **Monitor MLflow experiments**: http://localhost:5001

## 📚 Documentation

- **Service Status**: `RUNNING_STATUS.md`
- **Professional UI**: http://localhost:8000/app
- **API Documentation**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5001

---

**Total Files**: 48 files across 7 main directories
**Architecture**: Service-oriented with complete independence
**Monitoring**: Real-time dashboards with drift detection
**Deployment**: Docker-based containerization