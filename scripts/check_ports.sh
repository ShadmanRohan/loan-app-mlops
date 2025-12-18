#!/bin/bash

echo "🔍 Checking port usage and services..."
echo "=================================="

echo "📊 Checking Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running or no containers"

echo ""
echo "🌐 Testing API endpoints:"
echo "Port 8000 (Prediction API):"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/health 2>/dev/null || echo "❌ Port 8000 not accessible"

echo "Port 8501 (Monitoring):"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8501 2>/dev/null || echo "❌ Port 8501 not accessible"

echo "Port 9090 (Prometheus):"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:9090 2>/dev/null || echo "❌ Port 9090 not accessible"

echo "Port 3001 (Grafana):"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:3001 2>/dev/null || echo "❌ Port 3001 not accessible"

echo ""
echo "🔧 Checking what's using port 8000:"
netstat -tlnp 2>/dev/null | grep :8000 || echo "Port 8000 appears free"
lsof -i :8000 2>/dev/null || echo "No process found using port 8000"

echo ""
echo "💡 To start services:"
echo "docker-compose -f infrastructure/docker-compose.yml up -d"


