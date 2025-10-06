# Prediction API Service

FastAPI-based prediction service for serving ML models.

## Structure
- `src/api/` - FastAPI application
- `src/models/` - Model loading and management
- `src/middleware/` - API middleware
- `src/serving/` - Model serving logic

## Usage
```bash
# Build and run
docker build -t prediction-api .
docker run -p 8000:8000 prediction-api

# Run tests
python -m pytest tests/
```
