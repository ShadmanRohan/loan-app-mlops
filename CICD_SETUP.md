# 🚀 CI/CD Pipeline Setup

This document explains how to set up automatic deployment from GitHub to your server.

## 📋 Overview

The CI/CD pipeline automatically:
1. **Listens** for GitHub push events
2. **Tests** the application
3. **Builds** Docker images
4. **Deploys** to your server
5. **Verifies** deployment health

## 🏗️ Architecture

```
GitHub Push → Webhook Server → Deploy Script → Docker Services
     ↓              ↓              ↓              ↓
   Trigger      Verify         Backup        Health Check
```

## 🛠️ Setup Instructions

### 1. Initial Setup

```bash
# Run the setup script
./scripts/setup_cicd.sh

# Update webhook secret (IMPORTANT!)
sudo nano /etc/systemd/system/mlops-webhook.service
# Change: WEBHOOK_SECRET=your-secure-secret-here
```

### 2. Start Webhook Service

```bash
# Start the webhook server
sudo systemctl start mlops-webhook

# Enable auto-start on boot
sudo systemctl enable mlops-webhook

# Check status
sudo systemctl status mlops-webhook
```

### 3. Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: `http://your-server-ip:8080/github-webhook`
   - **Content type**: `application/json`
   - **Secret**: (same as in service file)
   - **Events**: Select "Just the push event"
   - **Active**: ✅ Checked

### 4. Test the Pipeline

```bash
# Make a test commit
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main

# Monitor deployment
sudo journalctl -u mlops-webhook -f
```

## 📁 File Structure

```
scripts/
├── deploy.sh              # Main deployment script
├── webhook_server.py      # GitHub webhook listener
└── setup_cicd.sh         # Setup script

.github/workflows/
└── deploy.yml            # GitHub Actions workflow (alternative)
```

## 🔧 Configuration

### Environment Variables

```bash
# Webhook server
WEBHOOK_SECRET=your-secure-secret

# Deployment paths
PROJECT_DIR=/home/rohan/Desktop/MLOps/ml-orchestration
BACKUP_DIR=/home/rohan/Desktop/MLOps/backups
```

### Service Endpoints

After deployment, these endpoints are available:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:8000/app/
- **MLflow**: http://localhost:5000
- **Grafana**: http://localhost:3001

## 🚨 Troubleshooting

### Webhook Not Triggering

```bash
# Check webhook service
sudo systemctl status mlops-webhook
sudo journalctl -u mlops-webhook -f

# Test webhook manually
curl -X POST http://localhost:8080/github-webhook \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main"}'
```

### Deployment Failing

```bash
# Check deployment logs
tail -f /home/rohan/Desktop/MLOps/backups/deploy.log

# Manual deployment
./scripts/deploy.sh

# Rollback to previous version
cd /home/rohan/Desktop/MLOps/backups
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz -C ../
```

### Docker Issues

```bash
# Check Docker status
docker ps
docker-compose -f infrastructure/docker-compose.yml ps

# Restart services
docker-compose -f infrastructure/docker-compose.yml down
docker-compose -f infrastructure/docker-compose.yml up -d
```

## 🔒 Security Considerations

1. **Webhook Secret**: Use a strong, random secret
2. **Firewall**: Only allow webhook port (8080) from GitHub IPs
3. **SSH Keys**: Use key-based authentication
4. **Backups**: Regular backups before each deployment
5. **Logs**: Monitor deployment logs for issues

## 📊 Monitoring

### Health Checks

The deployment script includes:
- ✅ API health check
- ✅ Prediction endpoint test
- ✅ Automatic rollback on failure

### Logs

```bash
# Webhook server logs
sudo journalctl -u mlops-webhook -f

# Deployment logs
tail -f scripts/deploy.log

# Docker logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

## 🎯 Best Practices

1. **Branch Strategy**: Only deploy from `main` branch
2. **Testing**: Always test locally before pushing
3. **Backups**: Keep multiple backup versions
4. **Monitoring**: Set up alerts for failed deployments
5. **Documentation**: Keep deployment logs updated

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test components individually
4. Consider rolling back to previous version

---

**Note**: This setup provides a robust CI/CD pipeline that's commonly used in production environments. It includes automatic rollback, health checks, and comprehensive logging.







