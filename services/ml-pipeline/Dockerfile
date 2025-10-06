FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly
RUN pip install mlflow scikit-learn pandas numpy pyyaml numexpr

# Copy source code
COPY src ./src
COPY config ./config

# Set Python path
ENV PYTHONPATH=/app/src

CMD ["python", "-m", "training.train"]
