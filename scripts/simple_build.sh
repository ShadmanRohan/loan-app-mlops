#!/usr/bin/env bash
set -euo pipefail

# Simple approach: create a minimal React app without complex build tools
# Just copy the designed component and serve it directly

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
DIST_DIR="$ROOT_DIR/local_storage/frontend_dist"

echo "[INFO] Creating minimal React app structure"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Create a simple HTML file that loads React from CDN
cat > "$DIST_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loan Approval - Designed UI</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/lucide-react@latest/dist/umd/lucide-react.js"></script>
    <script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="app.js"></script>
</body>
</html>
EOF

# Copy the designed component as app.js
cp "$ROOT_DIR/frontend/LoanApprovalWithSHAP.jsx" "$DIST_DIR/app.js"

echo "[SUCCESS] Minimal React app created at $DIST_DIR"
echo "Open http://localhost:8000/app/ after restarting the API container."
