# FlashCase Deployment Guide

## Overview

This guide covers deployment options, configurations, and best practices for deploying FlashCase to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Platform-Specific Guides](#platform-specific-guides)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- Docker and Docker Compose (for containerized deployments)
- Git repository access
- Domain name (optional, but recommended)
- SSL certificate (Let's Encrypt recommended)

### Environment Secrets

Prepare these secrets before deployment:

```bash
# Required
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=<your-database-url>
GROK_API_KEY=<your-xai-api-key>

# Optional but recommended
COURTLISTENER_API_KEY=<your-courtlistener-key>
SLACK_WEBHOOK_URL=<for-alerts>
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Deployment Options

FlashCase supports multiple deployment platforms. Choose based on your needs:

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Render** | Easy setup, free tier, managed databases | Limited free tier resources | MVP, small projects |
| **Heroku** | Simple deployment, addons ecosystem | Higher cost, no free tier | Quick prototypes |
| **AWS (ECS/Fargate)** | Scalable, full control, AWS ecosystem | Complex setup, management overhead | Production at scale |
| **GCP (Cloud Run)** | Auto-scaling, pay-per-use, simple | Less control than VMs | Production, cost-conscious |
| **Railway** | Modern UI, simple deploy, databases included | Newer platform | MVP, small teams |
| **DigitalOcean App Platform** | Simple, affordable, managed | Limited features vs AWS/GCP | Small to medium apps |

### Recommendation Matrix

**For MVP / Learning / Small Projects:**
→ **Render** (Free tier) or **Railway** ($5/month)

**For Production / Startup:**
→ **GCP Cloud Run** or **AWS ECS** (scalable, cost-effective)

**For Enterprise:**
→ **AWS ECS** or **Kubernetes** (full control, compliance)

---

## Platform-Specific Guides

### Option 1: Render (Recommended for MVP)

**Pros:**
- Free tier available
- Managed database included
- Automatic SSL
- Easy GitHub integration

**Steps:**

1. **Create Render Account**: Sign up at [render.com](https://render.com)

2. **Create PostgreSQL Database** (recommended over SQLite for production):
   - Go to "New" → "PostgreSQL"
   - Choose free tier
   - Copy connection string

3. **Deploy Backend**:
   - Go to "New" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     ```
     Name: flashcase-backend
     Environment: Docker
     Dockerfile Path: backend/Dockerfile
     Branch: main
     ```
   - Add environment variables:
     ```
     DATABASE_URL=<your-postgres-url>
     SECRET_KEY=<your-secret-key>
     GROK_API_KEY=<your-grok-key>
     CORS_ORIGINS=["https://flashcase-frontend.onrender.com"]
     ```
   - Deploy!

4. **Deploy Frontend**:
   - Go to "New" → "Static Site"
   - Connect repository
   - Settings:
     ```
     Name: flashcase-frontend
     Build Command: cd frontend && npm install && npm run build
     Publish Directory: frontend/out
     ```
   - Add environment variable:
     ```
     NEXT_PUBLIC_API_URL=https://flashcase-backend.onrender.com/api/v1
     ```

5. **Configure Custom Domain** (optional):
   - Add your domain in Render dashboard
   - Update DNS records
   - SSL is automatic

**Cost Estimate:**
- Free tier: $0/month (limited resources, spins down after inactivity)
- Paid tier: ~$7-15/month (always-on, better resources)

---

### Option 2: Heroku

**Pros:**
- Well-documented
- Large addon marketplace
- Easy rollbacks

**Steps:**

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   heroku login
   ```

2. **Create Apps**:
   ```bash
   heroku create flashcase-backend
   heroku create flashcase-frontend
   ```

3. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini -a flashcase-backend
   ```

4. **Configure Backend**:
   ```bash
   cd backend
   heroku git:remote -a flashcase-backend
   
   # Set environment variables
   heroku config:set SECRET_KEY=<your-secret-key>
   heroku config:set GROK_API_KEY=<your-grok-key>
   heroku config:set CORS_ORIGINS='["https://flashcase-frontend.herokuapp.com"]'
   
   # Deploy
   git subtree push --prefix backend heroku main
   ```

5. **Configure Frontend**:
   ```bash
   cd frontend
   heroku git:remote -a flashcase-frontend
   
   # Set environment variables
   heroku config:set NEXT_PUBLIC_API_URL=https://flashcase-backend.herokuapp.com/api/v1
   
   # Deploy
   git subtree push --prefix frontend heroku main
   ```

**Cost Estimate:**
- Basic tier: ~$7-16/month per app
- Database: ~$9/month (mini)
- **Total: ~$23-41/month**

---

### Option 3: AWS (ECS with Fargate)

**Pros:**
- Highly scalable
- Full AWS ecosystem
- Production-grade

**Prerequisites:**
- AWS account
- AWS CLI installed
- ECR repositories created

**Steps:**

1. **Build and Push Images**:
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push backend
   cd backend
   docker build -t flashcase-backend .
   docker tag flashcase-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/flashcase-backend:latest
   docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/flashcase-backend:latest
   
   # Build and push frontend
   cd ../frontend
   docker build -t flashcase-frontend .
   docker tag flashcase-frontend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/flashcase-frontend:latest
   docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/flashcase-frontend:latest
   ```

2. **Create ECS Cluster**:
   ```bash
   aws ecs create-cluster --cluster-name flashcase
   ```

3. **Create Task Definitions**:
   - Use AWS Console or CLI
   - Configure container settings
   - Set environment variables
   - Configure resource limits (CPU/Memory)

4. **Create Services**:
   ```bash
   aws ecs create-service \
     --cluster flashcase \
     --service-name backend \
     --task-definition flashcase-backend:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

5. **Configure Load Balancer**:
   - Create Application Load Balancer
   - Configure target groups
   - Set up health checks
   - Configure SSL certificate

6. **Setup RDS Database**:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier flashcase-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password <password> \
     --allocated-storage 20
   ```

**Cost Estimate:**
- Fargate: ~$30-50/month (2 tasks, small)
- RDS: ~$15-20/month (db.t3.micro)
- Load Balancer: ~$16/month
- **Total: ~$61-86/month**

---

### Option 4: GCP (Cloud Run)

**Pros:**
- Auto-scaling (including to zero)
- Pay only for requests
- Simple deployment

**Steps:**

1. **Install gcloud CLI**:
   ```bash
   curl https://sdk.cloud.google.com | bash
   gcloud init
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Deploy Backend**:
   ```bash
   cd backend
   
   # Build and deploy
   gcloud run deploy flashcase-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=<url>,SECRET_KEY=<key>,GROK_API_KEY=<key>
   ```

4. **Deploy Frontend**:
   ```bash
   cd frontend
   
   # Build and deploy
   gcloud run deploy flashcase-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NEXT_PUBLIC_API_URL=<backend-url>/api/v1
   ```

5. **Setup Cloud SQL** (optional, for managed database):
   ```bash
   gcloud sql instances create flashcase-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

**Cost Estimate:**
- Cloud Run: ~$5-15/month (pay per use)
- Cloud SQL: ~$10-25/month (db-f1-micro)
- **Total: ~$15-40/month**

---

## Environment Configuration

### Production Environment Variables

**Backend (.env or platform config):**
```bash
# Core Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-key-here>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/flashcase

# CORS (set to your frontend URLs)
CORS_ORIGINS=["https://app.flashcase.com", "https://flashcase.com"]

# AI Configuration
GROK_API_KEY=<your-xai-api-key>
GROK_API_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-4-fast

# Cost Control
GROK_DEFAULT_TEMPERATURE=0.7
GROK_DEFAULT_MAX_TOKENS=1500
GROK_CHAT_MAX_TOKENS=2000
GROK_REWRITE_MAX_TOKENS=1000
GROK_AUTOCOMPLETE_MAX_TOKENS=500

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=50

# Token Usage Monitoring
TOKEN_USAGE_ALERT_THRESHOLD=100000
TOKEN_USAGE_TRACKING_ENABLED=true

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Optional: CourtListener
COURTLISTENER_API_KEY=<your-key>
COURTLISTENER_API_BASE_URL=https://www.courtlistener.com/api/rest/v3

# Logging
LOG_LEVEL=INFO

# Alerts (optional)
ALERT_EMAIL=ops@flashcase.com
SLACK_WEBHOOK_URL=<your-slack-webhook>
```

**Frontend (.env.production):**
```bash
NEXT_PUBLIC_API_URL=https://api.flashcase.com/api/v1
NODE_ENV=production
```

---

## Database Setup

### SQLite (Development Only)

SQLite is included in the repository for local development but **NOT recommended for production**.

### PostgreSQL (Production Recommended)

1. **Create Database**:
   ```sql
   CREATE DATABASE flashcase;
   CREATE USER flashcase_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE flashcase TO flashcase_user;
   ```

2. **Run Migrations** (if applicable):
   ```bash
   # From backend directory
   alembic upgrade head
   ```

3. **Connection String Format**:
   ```
   postgresql://username:password@hostname:5432/database_name
   ```

### Database Backups

**Automated Backups (PostgreSQL):**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
# Upload to S3, Google Cloud Storage, etc.
```

---

## CI/CD Pipeline

FlashCase includes GitHub Actions workflows for continuous integration and deployment.

### Workflows Included

1. **backend-ci.yml**: Run tests on backend changes
2. **frontend-ci.yml**: Build and test frontend
3. **docker-build.yml**: Build and test Docker images
4. **deploy.yml**: Deploy to production (template)

### Setup GitHub Secrets

Add these secrets to your GitHub repository:

**For All Platforms:**
- `SECRET_KEY`
- `GROK_API_KEY`
- `DATABASE_URL`

**Platform-Specific:**

**Render:**
- `RENDER_SERVICE_ID`
- `RENDER_API_KEY`

**Heroku:**
- `HEROKU_API_KEY`
- `HEROKU_EMAIL`

**AWS:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**GCP:**
- `GCP_CREDENTIALS` (service account JSON)
- `GCP_PROJECT_ID`

### Enabling Automatic Deployment

1. Edit `.github/workflows/deploy.yml`
2. Uncomment the section for your chosen platform
3. Add required secrets to GitHub
4. Push to `main` branch to trigger deployment

---

## Post-Deployment

### Verification Checklist

- [ ] Health check endpoints responding: `/api/v1/health`, `/api/v1/ai/health`
- [ ] Frontend loads correctly
- [ ] Database connection working
- [ ] Authentication flow works
- [ ] AI features functional (if API key configured)
- [ ] CORS configured correctly
- [ ] SSL certificate valid
- [ ] Monitoring and logging operational
- [ ] Backup strategy in place

### Smoke Tests

Run these tests after deployment:

```bash
# Backend health
curl https://api.flashcase.com/api/v1/health

# AI health
curl https://api.flashcase.com/api/v1/ai/health

# Token usage monitoring
curl https://api.flashcase.com/api/v1/ai/usage

# Frontend
curl https://flashcase.com
```

### Performance Testing

```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Test backend performance
hey -n 1000 -c 10 https://api.flashcase.com/api/v1/health

# Expected: <100ms p95, <1% errors
```

---

## Troubleshooting

### Common Issues

**Issue: "Database connection failed"**
- Check `DATABASE_URL` format
- Verify database is accessible from deployment
- Check firewall rules
- Ensure database is running

**Issue: "CORS errors in browser"**
- Verify `CORS_ORIGINS` includes your frontend URL
- Check URL format (no trailing slash)
- Clear browser cache

**Issue: "AI features not working"**
- Verify `GROK_API_KEY` is set correctly
- Check API key is valid on xAI platform
- Review logs for specific error messages
- Check rate limits aren't exceeded

**Issue: "Container crashes on startup"**
- Check logs: `docker logs <container-id>`
- Verify all required env vars are set
- Check resource limits (memory/CPU)
- Review startup health check settings

**Issue: "Slow response times"**
- Check database connection pool settings
- Review AI token limits (reduce if needed)
- Check server resources (CPU/Memory)
- Consider scaling up or out

### Getting Help

1. Check application logs first
2. Review monitoring dashboards
3. Consult this documentation
4. Search GitHub issues
5. Contact support team

---

## Security Considerations

1. **Never commit secrets** - Use environment variables
2. **Enable HTTPS** - Use SSL certificates
3. **Secure database** - Restrict access, use strong passwords
4. **Rate limiting** - Prevent abuse
5. **Regular updates** - Keep dependencies updated
6. **Backup data** - Regular automated backups
7. **Monitor logs** - Watch for suspicious activity

---

## Maintenance

### Regular Tasks

**Daily:**
- Check error logs
- Monitor token usage
- Review alerts

**Weekly:**
- Review performance metrics
- Check backup integrity
- Update dependencies (if needed)

**Monthly:**
- Review and optimize costs
- Security audit
- Update documentation
- Review and adjust rate limits

---

## Cost Optimization

### Tips to Reduce Costs

1. **Use serverless** - Pay only for what you use (Cloud Run, Lambda)
2. **Right-size resources** - Don't over-provision
3. **Enable autoscaling** - Scale down during low traffic
4. **Optimize AI usage** - Strict rate limits, token controls
5. **Use caching** - Reduce database and AI calls
6. **Regular reviews** - Monthly cost analysis

### Cost Tracking

Monitor these metrics:
- Compute costs (CPU/Memory)
- Database costs
- AI API costs (track via `/api/v1/ai/usage`)
- Network egress
- Storage costs

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)
- [GCP Cloud Run](https://cloud.google.com/run/docs)
- [Render Docs](https://render.com/docs)
- [Heroku Dev Center](https://devcenter.heroku.com/)

---

---

## Additional Documentation

- [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) - Complete implementation details
- [SECURITY.md](docs/SECURITY.md) - Security features and best practices
- [MONITORING.md](MONITORING.md) - Monitoring and observability setup
- [API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) - API reference

**Last Updated**: October 21, 2025  
**Version**: 1.0
