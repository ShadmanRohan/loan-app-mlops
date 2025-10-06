FROM python:3.11-slim

WORKDIR /app

# Install dependencies for monitoring dashboard
RUN pip install streamlit plotly pandas numpy requests evidently==0.4.0 "numpy<2.0"

# Copy source code
COPY src ./src

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8501

# Run the monitoring dashboard
CMD ["streamlit", "run", "src/orchestration/start_evidently.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
