#!/bin/bash
# Quick access to drift integration deployment
echo "🚀 Deploying Drift Integration..."
echo "================================"
echo ""

# Check if drift integration directory exists
if [ ! -d "scripts/drift-integration" ]; then
    echo "❌ Drift integration not found!"
    echo "Please ensure scripts/drift-integration/ directory exists."
    exit 1
fi

# Run the deployment script
cd scripts/drift-integration
./deploy_drift_integration.sh

echo ""
echo "✅ Drift integration deployment completed!"
echo "📋 Next steps:"
echo "1. Start services: ./start_loan_pipeline.sh start --dummy"
echo "2. Test integration: python scripts/drift-integration/test_drift_integration.py"
echo "3. View dashboard: http://localhost:8501"
