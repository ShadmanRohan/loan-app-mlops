# ML Pipeline Service

End-to-end machine learning pipeline service for data processing, training, and deployment.

## Structure
- `src/orchestration/` - Data processing & evaluation
- `src/training/` - Model training
- `src/preprocessing/` - Data preprocessing
- `src/ingestion/` - Data ingestion
- `src/deployment/` - Model deployment
- `src/serving/` - Model serving

## Usage
```bash
# Build and run
docker build -t ml-pipeline .
docker run ml-pipeline

# Run tests
python -m pytest tests/
```
