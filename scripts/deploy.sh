#!/bin/bash

# Auto-deployment script for MLOps pipeline
# This script should be called by GitHub Actions or webhook

set -e  # Exit on any error

echo "🚀 Starting deployment..."

# Configuration
PROJECT_DIR="/home/rohan/Desktop/MLOps/ml-orchestration"
BACKUP_DIR="/home/rohan/Desktop/MLOps/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup current deployment
echo "📦 Creating backup..."
if [ -d "$PROJECT_DIR" ]; then
    tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$(dirname $PROJECT_DIR)" "$(basename $PROJECT_DIR)"
    echo "✅ Backup created: backup_$DATE.tar.gz"
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main || {
    echo "❌ Failed to pull latest code"
    exit 1
}

# Stop existing services gracefully
echo "🛑 Stopping existing services..."
docker-compose -f infrastructure/docker-compose.yml down || true

# Build and start new services
echo "🔨 Building and starting services..."
docker-compose -f infrastructure/docker-compose.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 30

# Health check
echo "🔍 Running health checks..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
        break
    else
        echo "⏳ Waiting for API... (attempt $i/5)"
        sleep 10
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ API health check failed after 5 attempts"
        echo "🔄 Rolling back to previous version..."
        docker-compose -f infrastructure/docker-compose.yml down
        tar -xzf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$(dirname $PROJECT_DIR)"
        cd "$PROJECT_DIR"
        docker-compose -f infrastructure/docker-compose.yml up -d
        exit 1
    fi
done

# Test prediction endpoint
echo "🧪 Testing prediction endpoint..."
python scripts/test_api.py || {
    echo "❌ Prediction test failed"
    echo "🔄 Rolling back..."
    docker-compose -f infrastructure/docker-compose.yml down
    tar -xzf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$(dirname $PROJECT_DIR)"
    cd "$PROJECT_DIR"
    docker-compose -f infrastructure/docker-compose.yml up -d
    exit 1
}

echo "🎉 Deployment successful!"
echo "📊 Service endpoints:"
echo "  • API: http://localhost:8000"
echo "  • Health: http://localhost:8000/health"
echo "  • Frontend: http://localhost:8000/app/"
echo "  • MLflow: http://localhost:5000"
echo "  • Grafana: http://localhost:3001"







