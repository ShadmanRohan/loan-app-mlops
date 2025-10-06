#!/bin/bash
# Quick access to drift integration rollback
echo "🔄 Rolling back Drift Integration..."
echo "=================================="
echo ""

# Check if drift integration directory exists
if [ ! -d "scripts/drift-integration" ]; then
    echo "❌ Drift integration not found!"
    echo "Please ensure scripts/drift-integration/ directory exists."
    exit 1
fi

# Run the rollback script
cd scripts/drift-integration
./rollback_drift_integration.sh

echo ""
echo "✅ Drift integration rollback completed!"
echo "📋 The system is now back to its original state."
