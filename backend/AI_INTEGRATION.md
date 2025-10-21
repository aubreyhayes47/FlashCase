# AI Legal Assistant Integration (Grok + CourtListener)

This document describes the integration of xAI's Grok model with CourtListener's legal database to provide AI-powered legal assistance for law students.

## Overview

The AI Legal Assistant provides three main features:
1. **Chat**: Conversational AI assistance for legal questions
2. **Card Rewriting**: AI-powered flashcard improvement suggestions
3. **Card Autocomplete**: Intelligent completion suggestions while creating flashcards

All features are grounded in verifiable legal sources through CourtListener integration, providing citations and case law references when appropriate.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  (Sends requests via SSE/HTTP to AI endpoints)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Rate Limiting Middleware                      │  │
│  │  (slowapi - per-IP rate limits)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         AI Router (app/routers/ai.py)                │  │
│  │  • POST /ai/chat                                     │  │
│  │  • POST /ai/rewrite-card                             │  │
│  │  • POST /ai/autocomplete-card                        │  │
│  │  • GET  /ai/health                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Grok Service (app/services/grok_service.py)     │  │
│  │  • chat_completion()                                 │  │
│  │  • rewrite_card()                                    │  │
│  │  • autocomplete_card()                               │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                                    │               │
└─────────┼────────────────────────────────────┼───────────────┘
          │                                    │
          ▼                                    ▼
┌──────────────────────┐          ┌─────────────────────────┐
│   xAI Grok API       │          │  CourtListener API      │
│   (LLM inference)    │◄────────►│  (Legal case search)    │
└──────────────────────┘          └─────────────────────────┘
        Tool calling for legal grounding
```

### Data Flow

1. **User Request**: Frontend sends request to AI endpoint
2. **Rate Limiting**: Request checked against rate limits (10/min, 100/hour by default)
3. **API Validation**: Request validated for required fields and API keys
4. **Grok Processing**: Request sent to Grok API with tool definitions
5. **Tool Execution**: If Grok requests legal sources, CourtListener API is called
6. **Response Streaming**: Response streamed back to client via Server-Sent Events (SSE)

## API Endpoints

### 1. Chat Endpoint

```http
POST /api/v1/ai/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Explain Miranda rights"}
  ],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response (SSE stream):**
```
data: {"content": "Miranda"}
data: {"content": " rights"}
data: {"content": " are..."}
data: [DONE]
```

**Use Cases:**
- General legal questions
- Case law lookup
- Legal concept explanations
- Study assistance

### 2. Card Rewrite Endpoint

```http
POST /api/v1/ai/rewrite-card
Content-Type: application/json

{
  "front": "What is jurisdiction?",
  "back": "Power of court",
  "instruction": "Make more detailed and add citations"
}
```

**Response (SSE stream):**
```json
{
  "front": "What is jurisdiction and what are its types?",
  "back": "Jurisdiction is the legal authority of a court to hear and decide cases. Types include: (1) Subject matter jurisdiction - power over the type of case; (2) Personal jurisdiction - power over the parties. See International Shoe Co. v. Washington, 326 U.S. 310 (1945).",
  "explanation": "Added more detail and relevant Supreme Court citation",
  "sources": ["International Shoe Co. v. Washington, 326 U.S. 310 (1945)"]
}
```

**Use Cases:**
- Improving flashcard clarity
- Adding legal citations
- Enhancing answer completeness

### 3. Card Autocomplete Endpoint

```http
POST /api/v1/ai/autocomplete-card
Content-Type: application/json

{
  "partial_text": "What is the Fourth Amendment",
  "card_type": "front"
}
```

**Response (SSE stream):**
```json
{
  "suggestions": [
    "What is the Fourth Amendment's protection against unreasonable searches?",
    "What is the Fourth Amendment warrant requirement?",
    "What is the Fourth Amendment exclusionary rule?"
  ]
}
```

**Use Cases:**
- Faster card creation
- Suggestion of complete questions
- Content generation assistance

### 4. Health Check Endpoint

```http
GET /api/v1/ai/health
```

**Response:**
```json
{
  "status": "healthy",
  "grok_configured": true,
  "courtlistener_configured": true,
  "model": "grok-beta",
  "rate_limiting_enabled": true
}
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Grok API Configuration
GROK_API_KEY=your_xai_api_key_here
GROK_API_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-beta

# CourtListener API Configuration
COURTLISTENER_API_BASE_URL=https://www.courtlistener.com/api/rest/v3
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
```

### Getting API Keys

1. **xAI Grok API Key**: 
   - Sign up at https://x.ai/
   - Create an API key in your dashboard
   - Note: This is a paid service with per-token pricing

2. **CourtListener API Key**:
   - Sign up at https://www.courtlistener.com/sign-in/register/
   - Generate API key in your account settings
   - Free tier available with rate limits

## Rate Limiting

Rate limiting is implemented to control costs and prevent abuse:

- **Per-minute limit**: 10 requests (configurable via `RATE_LIMIT_PER_MINUTE`)
- **Per-hour limit**: 100 requests (configurable via `RATE_LIMIT_PER_HOUR`)
- **Identifier**: Currently uses IP address; will use user ID after authentication

### Rate Limit Response

When rate limit is exceeded:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890

{
  "error": "Rate limit exceeded"
}
```

## Tool Calling (CourtListener Integration)

The Grok service defines tools that the AI can call to search legal databases:

### search_courtlistener Tool

**Purpose**: Search CourtListener API for relevant legal cases and precedents

**Parameters**:
- `query` (required): Search query for legal cases
- `court` (optional): Court identifier (e.g., "scotus" for Supreme Court)
- `jurisdiction` (optional): Jurisdiction filter
- `max_results` (optional): Maximum results (default: 5, max: 20)

**Example Tool Call Flow**:
1. User asks: "What cases define Miranda rights?"
2. Grok decides to call `search_courtlistener`
3. Service executes: `search_courtlistener("Miranda rights", court="scotus")`
4. Results returned to Grok
5. Grok synthesizes response with citations

## Security

### Implemented Security Measures

1. **No Stack Trace Exposure**: All exception handling sanitized to prevent internal error details from reaching users
2. **API Key Protection**: Keys stored in environment variables, never exposed in responses
3. **Input Validation**: All requests validated using Pydantic models
4. **Rate Limiting**: Prevents abuse and controls costs
5. **Secure Logging**: Internal errors logged for debugging without exposing to users

### CodeQL Analysis

The implementation has been analyzed with CodeQL. All initial vulnerabilities related to stack trace exposure have been addressed:

- ✅ Exception messages sanitized
- ✅ Generic error messages returned to users
- ✅ Detailed errors logged internally only
- ✅ No sensitive information in responses

## Testing

### Unit Tests

Run the test suite:
```bash
cd backend
pytest tests/test_ai.py -v
```

**Test Coverage**:
- ✅ Health check endpoint
- ✅ Chat endpoint (with/without API key)
- ✅ Card rewrite endpoint
- ✅ Card autocomplete endpoint
- ✅ CourtListener search functionality
- ✅ Rate limiting configuration
- ✅ Error handling

### Manual Testing

Run the manual test script:
```bash
cd backend
python3 test_ai_manual.py
```

This script tests all endpoints with sample data and demonstrates streaming responses.

### Testing with API Keys

To fully test the integration:

1. Add valid API keys to `.env`
2. Start the server: `uvicorn app.main:app --reload`
3. Use the interactive API docs at http://localhost:8000/docs
4. Or use the manual test script: `python3 test_ai_manual.py`

## Cost Estimation

### Grok API Costs

Pricing varies based on model and usage. Typical costs:
- Grok-beta: ~$5 per million tokens
- Average chat: 500-1000 tokens (~$0.005 per chat)
- With rate limits: Max $5-10 per user per month (100 requests/hour × 720 hours = 72,000 requests)

### Optimization Strategies

1. **Temperature Control**: Lower temperature (0.3-0.5) for card generation = more deterministic, fewer tokens
2. **Max Tokens Limit**: Set appropriate limits (500-2000) based on use case
3. **Caching**: Consider caching common legal queries
4. **Rate Limiting**: Prevent runaway costs from abuse

## Deployment

### Production Checklist

- [ ] Set production API keys in environment
- [ ] Enable rate limiting: `RATE_LIMIT_ENABLED=true`
- [ ] Configure appropriate rate limits based on budget
- [ ] Set up monitoring for API usage and costs
- [ ] Configure logging with appropriate log levels
- [ ] Test rate limiting behavior under load
- [ ] Set up alerting for rate limit violations
- [ ] Document API key rotation procedure

### Monitoring

Key metrics to monitor:
1. **API Request Volume**: Track requests per endpoint
2. **Token Usage**: Monitor Grok API token consumption
3. **Rate Limit Hits**: Track when users hit limits
4. **Error Rates**: Monitor 4xx/5xx responses
5. **Response Times**: Track API latency
6. **CourtListener Usage**: Monitor legal search volume

## Future Enhancements

### Short Term
- [ ] User-based rate limiting (after authentication implemented)
- [ ] Response caching for common queries
- [ ] More legal database integrations (Google Scholar, Justia)
- [ ] Custom prompts per card type

### Long Term
- [ ] Fine-tuned model on legal flashcard data
- [ ] Batch card generation from case briefs
- [ ] Citation validation and formatting
- [ ] Multi-jurisdictional legal analysis
- [ ] Integration with study analytics

## Troubleshooting

### Common Issues

**Issue**: "AI service not configured" error
- **Solution**: Add `GROK_API_KEY` to `.env` file

**Issue**: Rate limit errors in testing
- **Solution**: Temporarily disable rate limiting: `RATE_LIMIT_ENABLED=false`

**Issue**: CourtListener returning no results
- **Solution**: Check API key is valid and query is well-formed

**Issue**: Streaming not working
- **Solution**: Ensure client accepts `text/event-stream` content type

## Support

For issues or questions:
1. Check this documentation
2. Review test files in `tests/test_ai.py`
3. Check server logs for detailed error messages
4. Open an issue on GitHub with error details

## References

- [xAI Grok API Documentation](https://docs.x.ai/)
- [CourtListener API Documentation](https://www.courtlistener.com/api/rest-info/)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SlowAPI Rate Limiting](https://github.com/laurents/slowapi)

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
