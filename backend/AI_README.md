# AI Legal Assistant - Quick Start Guide

## Overview

The AI Legal Assistant uses xAI's Grok model with CourtListener legal database integration to provide AI-powered features for law students.

## Features

- **💬 Chat**: Ask legal questions with grounded answers
- **✏️ Card Rewriting**: AI-powered flashcard improvement
- **⚡ Autocomplete**: Smart suggestions while creating cards

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

# Rate Limiting (optional, defaults shown)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
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
| `/health` | GET | Check AI service status |
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

Default limits (configurable):
- 10 requests per minute
- 100 requests per hour

## Documentation

For comprehensive documentation, see [AI_INTEGRATION.md](./AI_INTEGRATION.md)

## Testing

```bash
# Run unit tests
pytest tests/test_ai.py -v

# Run manual tests (requires running server)
python3 test_ai_manual.py
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

With default rate limits (100 req/hour):
- ~$5-10 per active user per month
- Adjust rate limits based on budget

---

**Need Help?** Check [AI_INTEGRATION.md](./AI_INTEGRATION.md) for detailed documentation.
