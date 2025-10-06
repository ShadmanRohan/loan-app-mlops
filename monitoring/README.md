# Monitoring Service

ML monitoring service for drift detection, metrics collection, and observability.

## Structure
- `src/drift/` - Data and model drift detection
- `src/metrics/` - Metrics collection and analysis
- `src/dashboards/` - Dashboard configurations
- `src/orchestration/` - Monitoring orchestration

## Usage
```bash
# Build and run
docker build -t monitoring .
docker run monitoring

# Run tests
python -m pytest tests/
```
