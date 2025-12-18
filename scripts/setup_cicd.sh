#!/bin/bash

# Setup script for CI/CD pipeline
# Run this script to configure automatic deployment from GitHub

set -e

echo "🚀 Setting up CI/CD pipeline..."

# Make scripts executable
chmod +x scripts/deploy.sh
chmod +x scripts/webhook_server.py

# Create systemd service for webhook server
echo "📝 Creating webhook service..."
sudo tee /etc/systemd/system/mlops-webhook.service > /dev/null <<EOF
[Unit]
Description=MLOps GitHub Webhook Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/rohan/Desktop/MLOps/ml-orchestration
ExecStart=/usr/bin/python3 scripts/webhook_server.py
Restart=always
RestartSec=10
Environment=WEBHOOK_SECRET=your-webhook-secret-change-this

[Install]
WantedBy=multi-user.target
EOF

# Create backup directory
mkdir -p /home/rohan/Desktop/MLOps/backups

echo "✅ CI/CD setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the webhook secret in /etc/systemd/system/mlops-webhook.service"
echo "2. Start the webhook service: sudo systemctl start mlops-webhook"
echo "3. Enable auto-start: sudo systemctl enable mlops-webhook"
echo "4. Configure GitHub webhook:"
echo "   - Go to your GitHub repo → Settings → Webhooks"
echo "   - Add webhook: http://your-server:8080/github-webhook"
echo "   - Set content type: application/json"
echo "   - Set secret: (same as in service file)"
echo "   - Select events: Just the push event"
echo ""
echo "🧪 Test the setup:"
echo "   - Make a commit and push to main branch"
echo "   - Check logs: sudo journalctl -u mlops-webhook -f"
echo "   - Check deployment: tail -f scripts/deploy.log"







