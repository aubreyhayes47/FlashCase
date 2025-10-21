# AI Legal Assistant - Quick Start Guide

## Overview

The AI Legal Assistant uses xAI's **grok-4-fast** model with CourtListener legal database integration to provide AI-powered features for law students. The system includes comprehensive cost control mechanisms to keep the service free and sustainable.

## Features

- **💬 Chat**: Ask legal questions with grounded answers
- **✏️ Card Rewriting**: AI-powered flashcard improvement
- **⚡ Autocomplete**: Smart suggestions while creating cards
- **📊 Cost Control**: Built-in rate limiting, token tracking, and usage monitoring

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or update `.env` file:

```bash
# Required: xAI Grok API Key
GROK_API_KEY=your_xai_api_key_here

# Optional: CourtListener API Key (for better legal grounding)
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# Model Configuration (grok-4-fast optimized for cost)
GROK_MODEL=grok-4-fast

# Rate Limiting (optional, defaults shown)
RATE_LIMIT_ENABLED=true
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=50

# Token Usage Monitoring
TOKEN_USAGE_TRACKING_ENABLED=true
TOKEN_USAGE_ALERT_THRESHOLD=100000
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

### 4. Test the API

Visit http://localhost:8000/docs for interactive API documentation.

Or run the test suite:
```bash
pytest tests/test_ai.py -v
```

## API Endpoints

All endpoints are prefixed with `/api/v1/ai/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check AI service status and configuration |
| `/usage` | GET | Monitor token usage and costs |
| `/chat` | POST | Conversational AI assistance |
| `/rewrite-card` | POST | Improve flashcard content |
| `/autocomplete-card` | POST | Get completion suggestions |

## Example Usage

### Chat Request

```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain Miranda rights briefly"}
    ],
    "stream": false
  }'
```

### Rewrite Card Request

```bash
curl -X POST http://localhost:8000/api/v1/ai/rewrite-card \
  -H "Content-Type: application/json" \
  -d '{
    "front": "What is jurisdiction?",
    "back": "Power of court",
    "instruction": "Add more detail and citations"
  }'
```

## Rate Limits

AI endpoints have stricter limits for cost control:
- **AI endpoints**: 5 requests/minute, 50 requests/hour
- **Other endpoints**: 10 requests/minute, 100 requests/hour

## Cost Control & Monitoring

Monitor token usage and costs:
```bash
curl http://localhost:8000/api/v1/ai/usage
```

For detailed cost control information, see [COST_CONTROL.md](./COST_CONTROL.md)

## Documentation

- [COST_CONTROL.md](./COST_CONTROL.md) - Cost control and monitoring
- [AI_INTEGRATION.md](./AI_INTEGRATION.md) - Comprehensive technical documentation

## Testing

```bash
# Run all AI tests
pytest tests/test_ai.py tests/test_ai_cost_control.py -v

# Run only cost control tests
pytest tests/test_ai_cost_control.py -v
```

## Troubleshooting

**Service not configured error?**
- Add `GROK_API_KEY` to your `.env` file

**Rate limit errors?**
- Temporarily disable: `RATE_LIMIT_ENABLED=false` in `.env`

**No streaming?**
- Ensure `stream: true` in request
- Client must accept `text/event-stream`

## Security

✅ No stack trace exposure  
✅ API keys protected  
✅ Rate limiting enabled  
✅ Input validation  
✅ Secure error logging  

## Cost Estimation

With default rate limits (50 req/hour for AI):
- **Model**: grok-4-fast (optimized for cost)
- **Token limits**: 500-2000 per request (endpoint-specific)
- **Estimated cost**: ~$5-10 per active user per month
- **Monitoring**: Real-time token tracking via `/api/v1/ai/usage`

See [COST_CONTROL.md](./COST_CONTROL.md) for detailed cost analysis.

---

**Need Help?** Check [AI_INTEGRATION.md](./AI_INTEGRATION.md) for detailed documentation.
