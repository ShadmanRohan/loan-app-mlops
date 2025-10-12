#!/usr/bin/env bash
set -euo pipefail

# Build the designed React UI using Dockerized Node 20 to avoid local Node toolchain
# Copies only the production dist into local_storage/frontend_dist and serves it at /app via FastAPI

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
DIST_DIR="$ROOT_DIR/local_storage/frontend_dist"
TMP_APP_DIR="/tmp/loan-ui-build"

echo "[INFO] Preparing temp app dir at $TMP_APP_DIR"
rm -rf "$TMP_APP_DIR"
mkdir -p "$TMP_APP_DIR"

cat > "$TMP_APP_DIR/build_in_container.sh" << 'EOF'
set -euo pipefail
echo "[INFO] Using Node version: $(node -v)"
echo "[INFO] Scaffolding Vite React app"
echo "y" | npm create vite@latest app -- --template react
cd app
echo "[INFO] Installing dependencies (lucide-react, papaparse, tailwind)"
npm install
npm install lucide-react papaparse
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo "[INFO] Wiring Tailwind"
cat > tailwind.config.js << TWC
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: { extend: {} },
  plugins: [],
}
TWC

mkdir -p src
cat > src/index.css << CSS
@tailwind base;
@tailwind components;
@tailwind utilities;
CSS

sed -i "s|import React from 'react'|import React from 'react'\nimport './index.css'|" src/main.jsx || true

echo "[INFO] Injecting designed component into App.jsx"
cp /host/frontend/LoanApprovalWithSHAP.jsx src/App.jsx

echo "[INFO] Building production bundle"
npm run build
EOF

echo "[INFO] Running Dockerized build (node:20-alpine)"
docker run --rm -t \
  -v "$TMP_APP_DIR":/work \
  -v "$ROOT_DIR":/host \
  -w /work \
  node:20-alpine sh -lc "apk add --no-cache bash git python3 make g++ >/dev/null && chmod +x /work/build_in_container.sh && /work/build_in_container.sh"

echo "[INFO] Copying dist to $DIST_DIR"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
cp -r "$TMP_APP_DIR"/app/dist/* "$DIST_DIR/"

echo "[SUCCESS] Frontend built. Assets available at $DIST_DIR"
echo "Restart API container and open http://localhost:8000/app/"


