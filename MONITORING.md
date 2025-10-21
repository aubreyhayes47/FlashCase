# FlashCase Monitoring & Observability Guide

## Overview

This document describes the monitoring, logging, and observability setup for FlashCase, including AI token usage tracking and cost monitoring.

## Table of Contents

1. [Logging Setup](#logging-setup)
2. [AI Token Usage Monitoring](#ai-token-usage-monitoring)
3. [Health Checks](#health-checks)
4. [Metrics & Dashboards](#metrics--dashboards)
5. [Alerts & Notifications](#alerts--notifications)
6. [Production Monitoring Setup](#production-monitoring-setup)

---

## Logging Setup

### Backend Logging

FlashCase uses structured logging with JSON format for production environments and human-readable colored logs for development.

#### Configuration

Logging is automatically configured based on the environment:

```python
# In app/main.py or startup
from app.core.logging_config import setup_logging

# Development
setup_logging(environment="development", log_level="INFO")

# Production
setup_logging(environment="production", log_level="INFO")
```

#### Log Format

**Development** (Colored, human-readable):
```
[INFO] 2025-10-21 15:42:22 - app.routers.ai - AI chat request completed
[ERROR] 2025-10-21 15:42:23 - app.services.grok - API request failed
```

**Production** (JSON, structured):
```json
{
  "timestamp": "2025-10-21T15:42:22.392Z",
  "level": "INFO",
  "logger": "app.routers.ai",
  "message": "AI chat request completed",
  "module": "ai",
  "function": "chat",
  "line": 123,
  "user_id": "user_123",
  "endpoint": "/api/v1/ai/chat",
  "method": "POST",
  "status_code": 200,
  "duration_ms": 1250.5,
  "tokens_used": 450,
  "model": "grok-4-fast",
  "cost_estimate": 0.0005
}
```

#### Using Loggers

```python
from app.core.logging_config import get_logger, AILogger, RequestLogger

# Standard logging
logger = get_logger(__name__)
logger.info("Operation completed")
logger.error("An error occurred", exc_info=True)

# Request logging
request_logger = RequestLogger(logger)
request_logger.log_request(
    method="POST",
    endpoint="/api/v1/decks",
    status_code=201,
    duration_ms=45.2,
    user_id="user_123"
)

# AI operation logging
ai_logger = AILogger(logger)
ai_logger.log_ai_request(
    operation="chat",
    model="grok-4-fast",
    tokens_used=450,
    cost_estimate=0.0005,
    duration_ms=1250.5,
    user_id="user_123"
)
```

---

## AI Token Usage Monitoring

### Real-time Token Tracking

FlashCase tracks all AI API calls in real-time, monitoring:
- Total prompt tokens (input)
- Total completion tokens (output)
- Total tokens consumed
- Number of requests
- Estimated costs

### Usage Endpoint

**GET** `/api/v1/ai/usage`

Returns current token usage statistics:

```json
{
  "usage": {
    "total_prompt_tokens": 15420,
    "total_completion_tokens": 8932,
    "total_tokens": 24352,
    "total_requests": 156
  },
  "alert_threshold": 100000,
  "alert_triggered": false,
  "cost_control": {
    "model": "grok-4-fast",
    "default_temperature": 0.7,
    "max_tokens": {
      "chat": 2000,
      "rewrite": 1000,
      "autocomplete": 500
    }
  },
  "rate_limits": {
    "ai_per_minute": 5,
    "ai_per_hour": 50,
    "general_per_minute": 10,
    "general_per_hour": 100
  }
}
```

### Cost Estimation

Based on xAI's Grok pricing (example rates):

| Operation | Avg Tokens | Est. Cost per Request |
|-----------|------------|----------------------|
| Chat | ~1500 | $0.0015 |
| Rewrite | ~800 | $0.0008 |
| Autocomplete | ~300 | $0.0003 |

**Monthly Cost Estimate** (per active user):
- With 50 req/hour limit: ~36,000 requests/month max
- At 75% utilization: ~27,000 requests/month
- **Estimated: $5-10 per user per month**

### Monitoring Script

Create a simple monitoring script to track usage:

```bash
#!/bin/bash
# monitor-ai-usage.sh

API_URL="http://localhost:8000/api/v1/ai/usage"

while true; do
  response=$(curl -s $API_URL)
  echo "$(date): $response"
  
  # Check if alert threshold exceeded
  alert=$(echo $response | jq -r '.alert_triggered')
  if [ "$alert" = "true" ]; then
    echo "⚠️  ALERT: Token usage threshold exceeded!"
    # Add notification logic here (email, Slack, etc.)
  fi
  
  sleep 60  # Check every minute
done
```

### Dashboard Visualization

For visual monitoring, you can use tools like:

1. **Grafana + Prometheus**
   - Scrape the `/api/v1/ai/usage` endpoint
   - Create dashboards for token usage over time
   - Set up alerts for threshold violations

2. **Custom Dashboard**
   - Build a simple web dashboard that polls `/api/v1/ai/usage`
   - Display real-time token consumption
   - Show cost estimates and trends

3. **Cloud Provider Dashboards**
   - CloudWatch (AWS)
   - Cloud Monitoring (GCP)
   - Azure Monitor (Azure)

---

## Health Checks

### Backend Health Endpoint

**GET** `/api/v1/health`

Returns system health status:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T15:42:22.392Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### AI Health Endpoint

**GET** `/api/v1/ai/health`

Returns AI service health:

```json
{
  "status": "healthy",
  "grok_configured": true,
  "courtlistener_configured": true,
  "rate_limiting": {
    "enabled": true,
    "ai_per_minute": 5,
    "ai_per_hour": 50
  },
  "cost_control": {
    "model": "grok-4-fast",
    "token_tracking_enabled": true,
    "alert_threshold": 100000
  }
}
```

### Docker Health Checks

Configured in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## Metrics & Dashboards

### Key Metrics to Monitor

#### Application Metrics
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx responses)
- Active users (concurrent connections)

#### AI Metrics
- Token consumption rate (tokens/hour)
- AI request rate (requests/hour)
- AI response time (ms)
- AI error rate
- Estimated hourly/daily costs

#### System Metrics
- CPU usage
- Memory usage
- Database connections
- Disk I/O
- Network I/O

### Recommended Monitoring Stack

#### Option 1: Prometheus + Grafana (Self-hosted)

1. **Add Prometheus client to backend:**
   ```bash
   pip install prometheus-fastapi-instrumentator
   ```

2. **Configure in main.py:**
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator
   
   instrumentator = Instrumentator()
   instrumentator.instrument(app).expose(app)
   ```

3. **Deploy Prometheus:**
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'flashcase-backend'
       static_configs:
         - targets: ['backend:8000']
   ```

4. **Create Grafana dashboards:**
   - Import FastAPI metrics dashboard
   - Create custom AI token usage dashboard
   - Set up alerts for anomalies

#### Option 2: Cloud Provider Monitoring

**AWS CloudWatch:**
- Enable Container Insights for ECS
- Create custom metrics for AI usage
- Set up CloudWatch alarms

**GCP Cloud Monitoring:**
- Enable Cloud Monitoring for Cloud Run
- Create custom metrics via API
- Set up alerting policies

**Azure Monitor:**
- Enable Application Insights
- Configure custom telemetry
- Create metric alerts

#### Option 3: Third-party Services

- **Datadog**: Full-stack monitoring
- **New Relic**: Application performance monitoring
- **Sentry**: Error tracking and monitoring
- **LogRocket**: Session replay and monitoring

---

## Alerts & Notifications

### Critical Alerts

1. **High Token Usage**
   - Trigger: Token usage exceeds 100,000/hour
   - Action: Alert admins, consider rate limit adjustment

2. **High Error Rate**
   - Trigger: Error rate > 5% over 5 minutes
   - Action: Page on-call engineer

3. **Service Down**
   - Trigger: Health check fails 3 times in a row
   - Action: Immediate notification to ops team

4. **High Response Time**
   - Trigger: P95 response time > 5 seconds
   - Action: Investigate performance issues

### Warning Alerts

1. **Elevated Token Usage**
   - Trigger: Token usage exceeds 50,000/hour
   - Action: Notify team for awareness

2. **Increased Error Rate**
   - Trigger: Error rate > 2% over 5 minutes
   - Action: Monitor and investigate

3. **High Memory Usage**
   - Trigger: Memory usage > 80%
   - Action: Consider scaling up

### Setting Up Alerts

#### Email Notifications

```python
# Example alert handler
import smtplib
from email.mime.text import MIMEText

def send_alert_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'alerts@flashcase.com'
    msg['To'] = 'ops@flashcase.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
```

#### Slack Notifications

```python
import httpx

async def send_slack_alert(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    payload = {
        'text': f'⚠️ FlashCase Alert: {message}'
    }
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)
```

---

## Production Monitoring Setup

### Step-by-Step Guide

#### 1. Environment Variables

Set these in your production environment:

```bash
# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production

# Monitoring
TOKEN_USAGE_ALERT_THRESHOLD=100000
TOKEN_USAGE_TRACKING_ENABLED=true

# Alerts
ALERT_EMAIL=ops@flashcase.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### 2. Log Aggregation

**Using CloudWatch (AWS):**
```bash
# Install awslogs driver
docker run --log-driver=awslogs \
  --log-opt awslogs-group=/flashcase/backend \
  --log-opt awslogs-stream=backend-prod \
  flashcase-backend
```

**Using Stackdriver (GCP):**
```bash
# Logs are automatically collected from Cloud Run
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

#### 3. Create Monitoring Dashboard

Set up a dashboard displaying:
- Token usage over time (line chart)
- Cost estimate (gauge)
- Request rate (line chart)
- Error rate (line chart)
- Response time distribution (histogram)

#### 4. Configure Alerts

Create alert rules for:
- Token threshold exceeded
- High error rate
- Service downtime
- Performance degradation

#### 5. Set Up Runbook

Document response procedures:
- How to investigate high token usage
- Steps to scale up/down
- Emergency contact information
- Incident response procedures

---

## Best Practices

1. **Log Retention**: Keep logs for at least 30 days, compliance data for 1+ year
2. **Sampling**: In high-traffic scenarios, sample detailed logs (e.g., 10%)
3. **PII Protection**: Never log sensitive user data (passwords, payment info)
4. **Cost Monitoring**: Review token usage daily, adjust limits as needed
5. **Regular Reviews**: Weekly review of metrics and alerts
6. **Documentation**: Keep monitoring setup documented and up-to-date

---

## Troubleshooting

### High Token Usage

1. Check `/api/v1/ai/usage` for current stats
2. Review logs for unusual patterns
3. Check rate limiting configuration
4. Consider reducing max_tokens limits

### Missing Logs

1. Verify logging is enabled: `TOKEN_USAGE_TRACKING_ENABLED=true`
2. Check log level: `LOG_LEVEL=INFO`
3. Ensure logs are being shipped to aggregator
4. Check disk space on servers

### Alert Fatigue

1. Review alert thresholds
2. Add hysteresis to prevent flapping
3. Group related alerts
4. Use severity levels appropriately

---

## Resources

- [FastAPI Logging](https://fastapi.tiangolo.com/tutorial/logging/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [The Twelve-Factor App - Logs](https://12factor.net/logs)
- [AWS CloudWatch Documentation](https://aws.amazon.com/cloudwatch/)
- [GCP Cloud Monitoring](https://cloud.google.com/monitoring)

---

---

**Last Updated**: October 21, 2025  
**Version**: 1.0
