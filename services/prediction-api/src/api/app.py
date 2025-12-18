import os
import yaml
import joblib
import mlflow
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response, JSONResponse

# Import schemas
from .schemas import (
    LoanApplication, 
    LoanPrediction, 
    HealthResponse
)

# Import SHAP explainer
try:
    from explainability.shap_explainer import LoanSHAPExplainer
    SHAP_AVAILABLE = True
except ImportError as e:
    print(f"SHAP not available: {e}")
    LoanSHAPExplainer = None
    SHAP_AVAILABLE = False

# Try to import drift collector, but don't fail if it's not available
try:
    from drift.drift_collector import DriftDataCollector
    DRIFT_AVAILABLE = True
except ImportError as e:
    print(f"Drift monitoring not available: {e}")
    DriftDataCollector = None
    DRIFT_AVAILABLE = False

# Try to import demo request generator
try:
    from demo.dummy_requests import start_demo_generator
    DEMO_AVAILABLE = True
except ImportError as e:
    print(f"Demo request generator not available: {e}")
    start_demo_generator = None
    DEMO_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent.parent.parent / "config" / "api_config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Global variables for model and encoders
model = None
label_encoders = None
drift_collector = None
shap_explainer = None

# Feature names in order
FEATURE_NAMES = [
    'age', 'annual_income', 'credit_score', 'experience', 
    'loan_amount', 'loan_duration', 'number_of_dependents',
    'monthly_debt_payments', 'credit_card_utilization_rate',
    'number_of_open_credit_lines', 'number_of_credit_inquiries',
    'debt_to_income_ratio', 'bankruptcy_history', 
    'previous_loan_defaults', 'payment_history',
    'length_of_credit_history', 'savings_account_balance',
    'checking_account_balance', 'total_assets', 'total_liabilities',
    'monthly_income', 'job_tenure', 'net_worth',
    'employment_status', 'education_level', 'marital_status',
    'home_ownership_status', 'loan_purpose'
]

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'loan_api_requests_total', 'Total number of requests',
    ['endpoint', 'method']
)
REQUEST_DURATION = Histogram(
    'loan_api_request_duration_seconds', 'Request duration in seconds',
    ['endpoint', 'method']
)
LOAN_APPROVAL_COUNT = Counter(
    'loan_api_approvals_total', 'Total number of loan approvals',
    ['approved']
)
AVG_RISK_SCORE = Gauge(
    'loan_api_avg_risk_score', 'Average risk score of approved loans'
)
ACTIVE_REQUESTS = Gauge(
    'loan_api_active_requests', 'Number of active requests'
)

# Schemas are now imported from schemas.py

# Simple metrics tracking for backward compatibility
class SimpleMetrics:
    def __init__(self):
        self.requests = 0
        self.approvals = 0
        self.total_risk_score = 0
    
    def record_prediction(self, approved: bool, risk_score: float):
        self.requests += 1
        if approved:
            self.approvals += 1
        self.total_risk_score += risk_score
    
    def get_stats(self):
        return {
            "total_requests": self.requests,
            "approvals": self.approvals,
            "approval_rate": self.approvals / self.requests if self.requests > 0 else 0,
            "avg_risk_score": self.total_risk_score / self.requests if self.requests > 0 else 0
        }

metrics = SimpleMetrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MLflow and load the production model."""
    global model, label_encoders, drift_collector, shap_explainer
    try:
        mlflow.set_tracking_uri("http://localhost:5000")
        logger.info("MLflow tracking URI set successfully")
        
        # Try to load model from environment-aware paths
        def _first_existing(*paths):
            for p in paths:
                if p and Path(p).exists():
                    return p
            return None

        model_path = _first_existing(
            os.getenv("MODEL_PATH"),
            config["model"]["model_path"],  # legacy config path
            "models/champion/model.joblib",   # legacy in prediction-api/
            "../models/model.joblib"          # legacy at repo root (if used)
        )

        encoders_path = _first_existing(
            os.getenv("LABEL_ENCODERS_PATH"),
            Path(config["model"]["model_path"]).parent / "label_encoders.joblib",  # legacy config path
            "models/champion/label_encoders.joblib",
            "../models/label_encoders.joblib"
        )
        
        if model_path and encoders_path and Path(model_path).exists() and Path(encoders_path).exists():
            model = joblib.load(model_path)
            label_encoders = joblib.load(encoders_path)
            logger.info(f"Model and encoders loaded from {model_path}")
        else:
            # Create a dummy model if no fallback to MLflow
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            logger.warning(f"No model found at paths: model={model_path}, encoders={encoders_path}, using dummy model for predictions.")
        
        # Initialize SHAP explainer
        if SHAP_AVAILABLE and model is not None:
            try:
                shap_explainer = LoanSHAPExplainer(model, FEATURE_NAMES)
                logger.info("SHAP explainer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize SHAP explainer: {e}")
                shap_explainer = None
        
        # Initialize drift collector if available
        if DRIFT_AVAILABLE:
            try:
                drift_collector = DriftDataCollector()
                # Prefer training-produced reference, else fallback path
                reference_candidates = [
                    "/opt/data/reference/drift_reference.csv",
                    "/app/data/raw/Loan.csv",
                ]
                loaded = False
                for reference_data_path in reference_candidates:
                    if drift_collector.load_reference_data(reference_data_path):
                        logger.info(f"Drift collector initialized with reference data: {reference_data_path}")
                        loaded = True
                        break
                if not loaded:
                    logger.warning("Drift collector initialized but reference data not loaded")
                logger.info("Drift collector initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize drift collector: {e}")
                drift_collector = None
        else:
            logger.info("Drift monitoring not available")
        
        # Start demo request generator if available and enabled
        if DEMO_AVAILABLE and start_demo_generator:
            try:
                demo_thread = start_demo_generator()
                if demo_thread:
                    logger.info("Demo request generator started successfully")
            except Exception as e:
                logger.warning(f"Failed to start demo request generator: {e}")
        else:
            logger.info("Demo request generator not available or disabled")
        
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        pass

# Create FastAPI app
app = FastAPI(
    title="Loan Approval API",
    description="API for predicting loan approval based on applicant features",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount minimal static UI to avoid Node/React bloat
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

    @app.get("/", include_in_schema=False)
    async def root_index():
        """Serve minimal UI index for convenience at root."""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse({"message": "Loan Approval API. Visit /docs or /ui/"})

# Optionally serve a designed UI build (mounted into container)
frontend_dir_env = os.getenv("FRONTEND_DIR", "/app/frontend")
frontend_dir = Path(frontend_dir_env)
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="app")

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Middleware to track Prometheus metrics."""
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    try:
        response = await call_next(request)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        return response
    finally:
        REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(time.time() - start_time)
        ACTIVE_REQUESTS.dec()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        shap_available=shap_explainer is not None
    )

@app.get("/metrics")
async def get_metrics():
    """Get simple metrics for backward compatibility."""
    REQUEST_COUNT.labels(endpoint="/metrics", method="GET").inc()
    
    # Use the SimpleMetrics object instead of global variables
    # This ensures metrics persist during container lifetime
    stats = metrics.get_stats()
    
    return {
        "total_requests": stats["total_requests"],
        "approvals": stats["approvals"],
        "approval_rate": stats["approval_rate"],
        "avg_risk_score": stats["avg_risk_score"]
    }

@app.get("/prometheus")
async def prometheus_metrics():
    """Expose Prometheus metrics."""
    REQUEST_COUNT.labels(endpoint="/prometheus", method="GET").inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=LoanPrediction)
async def predict_loan_approval(application: LoanApplication):
    """Predict loan approval based on applicant features."""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Convert application to DataFrame
        app_data = application.dict()
        
        # Map column names to encoder keys
        column_mapping = {
            'employment_status': 'EmploymentStatus',
            'education_level': 'EducationLevel', 
            'marital_status': 'MaritalStatus',
            'home_ownership_status': 'HomeOwnershipStatus',
            'loan_purpose': 'LoanPurpose'
        }
        
        # Encode categorical variables with safe fallback for unseen labels
        if label_encoders:
            for col, encoder_key in column_mapping.items():
                if col in app_data and encoder_key in label_encoders:
                    try:
                        app_data[col] = label_encoders[encoder_key].transform([app_data[col]])[0]
                    except Exception:
                        # Fallback to the first known class if unseen label is provided
                        known = list(getattr(label_encoders[encoder_key], 'classes_', []))
                        fallback = known[0] if known else app_data[col]
                        app_data[col] = label_encoders[encoder_key].transform([fallback])[0]
        
        # Create feature vector
        features = np.array([[
            app_data['age'], app_data['annual_income'], app_data['credit_score'],
            app_data['experience'], app_data['loan_amount'], app_data['loan_duration'],
            app_data['number_of_dependents'], app_data['monthly_debt_payments'],
            app_data['credit_card_utilization_rate'], app_data['number_of_open_credit_lines'],
            app_data['number_of_credit_inquiries'], app_data['debt_to_income_ratio'],
            app_data['bankruptcy_history'], app_data['previous_loan_defaults'],
            app_data['payment_history'], app_data['length_of_credit_history'],
            app_data['savings_account_balance'], app_data['checking_account_balance'],
            app_data['total_assets'], app_data['total_liabilities'],
            app_data['monthly_income'], app_data['job_tenure'], app_data['net_worth'],
            app_data.get('employment_status', 0), app_data.get('education_level', 0),
            app_data.get('marital_status', 0), app_data.get('home_ownership_status', 0),
            app_data.get('loan_purpose', 0)
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] if hasattr(model, 'predict_proba') else 0.5
        
        # Calculate risk score (inverse of probability)
        risk_score = (1 - probability) * 100
        
        # Determine confidence
        if probability > 0.8 or probability < 0.2:
            confidence = "High"
        elif probability > 0.6 or probability < 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Update metrics using SimpleMetrics object
        prediction_approved = bool(prediction)
        metrics.record_prediction(prediction_approved, risk_score)
        
        # Update Prometheus metrics
        LOAN_APPROVAL_COUNT.labels(approved=str(prediction_approved).lower()).inc()
        if prediction_approved:
            AVG_RISK_SCORE.set(risk_score)
        
        # Collect data for drift analysis if available
        if drift_collector:
            try:
                drift_data = app_data.copy()
                drift_data['approved'] = prediction_approved
                drift_data['risk_score'] = risk_score
                drift_collector.collect_request_data(drift_data)
            except Exception as e:
                logger.warning(f"Failed to collect drift data: {e}")
        
        return LoanPrediction(
            approved=prediction_approved,
            probability=float(probability),
            risk_score=float(risk_score),
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/drift/collect")
async def collect_drift_data(application: LoanApplication):
    """Manually collect data for drift analysis."""
    if not DRIFT_AVAILABLE or drift_collector is None:
        raise HTTPException(status_code=503, detail="Drift collector not available")
    
    try:
        drift_data = application.dict()
        drift_collector.collect_request_data(drift_data)
        return {"status": "collected"}
    except Exception as e:
        logger.error(f"Failed to collect drift data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect drift data: {str(e)}")

@app.get("/drift/metrics")
async def get_drift_metrics():
    """Get current drift metrics."""
    if not DRIFT_AVAILABLE or drift_collector is None:
        raise HTTPException(status_code=503, detail="Drift collector not available")
    
    try:
        return drift_collector.calculate_drift()
    except Exception as e:
        logger.error(f"Failed to get drift metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get drift metrics: {str(e)}")

@app.get("/drift/summary")
async def get_drift_summary():
    """Get drift data collection summary."""
    if not DRIFT_AVAILABLE or drift_collector is None:
        raise HTTPException(status_code=503, detail="Drift collector not available")
    
    try:
        return drift_collector.get_summary()
    except Exception as e:
        logger.error(f"Failed to get drift summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get drift summary: {str(e)}")

@app.post("/predict/explain")
async def predict_with_explanation(application: LoanApplication):
    """Predict loan approval WITH SHAP explanation for React UI."""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        app_data = application.dict()
        
        # Map column names to encoder keys (same as /predict endpoint)
        column_mapping = {
            'employment_status': 'EmploymentStatus',
            'education_level': 'EducationLevel',
            'marital_status': 'MaritalStatus',
            'home_ownership_status': 'HomeOwnershipStatus',
            'loan_purpose': 'LoanPurpose'
        }
        
        # Encode categorical variables with safe fallback for unseen labels
        if label_encoders:
            for col, encoder_key in column_mapping.items():
                if col in app_data and encoder_key in label_encoders:
                    try:
                        app_data[col] = label_encoders[encoder_key].transform([app_data[col]])[0]
                    except Exception:
                        known = list(getattr(label_encoders[encoder_key], 'classes_', []))
                        fallback = known[0] if known else app_data[col]
                        app_data[col] = label_encoders[encoder_key].transform([fallback])[0]
        
        # Create feature vector
        features = np.array([[
            app_data['age'], app_data['annual_income'], app_data['credit_score'],
            app_data['experience'], app_data['loan_amount'], app_data['loan_duration'],
            app_data['number_of_dependents'], app_data['monthly_debt_payments'],
            app_data['credit_card_utilization_rate'], app_data['number_of_open_credit_lines'],
            app_data['number_of_credit_inquiries'], app_data['debt_to_income_ratio'],
            app_data['bankruptcy_history'], app_data['previous_loan_defaults'],
            app_data['payment_history'], app_data['length_of_credit_history'],
            app_data['savings_account_balance'], app_data['checking_account_balance'],
            app_data['total_assets'], app_data['total_liabilities'],
            app_data['monthly_income'], app_data['job_tenure'], app_data['net_worth'],
            app_data.get('employment_status', 0), app_data.get('education_level', 0),
            app_data.get('marital_status', 0), app_data.get('home_ownership_status', 0),
            app_data.get('loan_purpose', 0)
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] if hasattr(model, 'predict_proba') else 0.5
        risk_score = (1 - probability) * 100
        
        # Determine confidence
        if probability > 0.8 or probability < 0.2:
            confidence = "High"
        elif probability > 0.6 or probability < 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Update metrics
        prediction_approved = bool(prediction)
        metrics.record_prediction(prediction_approved, risk_score)
        
        LOAN_APPROVAL_COUNT.labels(approved=str(prediction_approved).lower()).inc()
        if prediction_approved:
            AVG_RISK_SCORE.set(risk_score)
        
        # Collect drift data
        if drift_collector:
            try:
                drift_data = application.dict()  # Use original data, not encoded
                drift_data['approved'] = prediction_approved
                drift_data['risk_score'] = risk_score
                
                # Apply drift trigger if active
                if drift_trigger:
                    drift_data = drift_trigger.apply_drift_to_data(drift_data)
                
                drift_collector.collect_request_data(drift_data)
            except Exception as e:
                logger.warning(f"Failed to collect drift data: {e}")
        
        # Get SHAP explanation
        shap_explanation = {}
        if shap_explainer:
            try:
                shap_explanation = shap_explainer.explain_prediction(
                    features,
                    application.dict()  # Pass original dict for display purposes
                )
            except Exception as e:
                logger.error(f"SHAP explanation failed: {e}", exc_info=True)
                shap_explanation = {
                    "error": True,
                    "message": f"SHAP explanation failed: {str(e)}",
                    "available": False
                }
        else:
            shap_explanation = {
                "message": "SHAP explainer not available",
                "available": False
            }
        
        response_dict = {
            "prediction": {
                "approved": prediction_approved,
                "probability": float(probability),
                "risk_score": float(risk_score),
                "confidence": confidence
            },
            "shap_explanation": shap_explanation
        }
        
        return response_dict
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Drift trigger endpoints
try:
    from ..drift.drift_trigger import DriftTrigger
    drift_trigger = DriftTrigger()
    
    @app.post("/drift/trigger")
    async def start_drift_trigger(drift_type: str, intensity: float = 0.5, duration: Optional[int] = None):
        """Start drift injection for testing drift detection."""
        result = drift_trigger.start_drift(drift_type, intensity, duration)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result

    @app.delete("/drift/trigger")
    async def stop_drift_trigger():
        """Stop drift injection and return to normal data generation."""
        return drift_trigger.stop_drift()

    @app.get("/drift/trigger/status")
    async def get_drift_trigger_status():
        """Get current drift trigger status."""
        return drift_trigger.get_status()
        
except ImportError as e:
    logger.warning(f"Drift trigger not available: {e}")
    drift_trigger = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
