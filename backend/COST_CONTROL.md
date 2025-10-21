# AI Cost Control Documentation

## Overview

This document describes the cost control mechanisms implemented for the FlashCase AI features using xAI's grok-4-fast model. These controls help manage costs while providing a free service to users.

## Model Selection: grok-4-fast

**Model**: `grok-4-fast`

**Why grok-4-fast?**
- Optimized for speed and cost efficiency
- Lower cost per token compared to standard models
- Still maintains high quality for legal education use cases
- Faster response times improve user experience

## Cost-Controlled Default Parameters

### Temperature Settings
- **Default**: 0.7 (balanced creativity and consistency)
- **Chat**: 0.7 (conversational, helpful responses)
- **Rewrite**: 0.5 (more deterministic, consistent improvements)
- **Autocomplete**: 0.3 (very deterministic, focused completions)

### Token Limits by Endpoint

| Endpoint | Max Tokens | Rationale |
|----------|------------|-----------|
| **Chat** | 2000 | Full conversational responses with citations |
| **Rewrite** | 1000 | Focused improvements to existing content |
| **Autocomplete** | 500 | Quick, minimal suggestions |

These limits are **enforced by default** unless explicitly overridden in requests.

## Rate Limiting

### Per-User Rate Limits

**AI Endpoints** (more restrictive):
- 5 requests per minute
- 50 requests per hour

**General Endpoints**:
- 10 requests per minute
- 100 requests per hour

Rate limits are applied **per IP address** (will be per authenticated user once auth is fully implemented).

### Which Endpoints Have AI Rate Limits?

- `POST /api/v1/ai/chat`
- `POST /api/v1/ai/rewrite-card`
- `POST /api/v1/ai/autocomplete-card`

### Testing Rate Limits

To test rate limiting in development:

```bash
# Set more lenient limits for testing
export AI_RATE_LIMIT_PER_MINUTE=100
export AI_RATE_LIMIT_PER_HOUR=1000

# Or disable rate limiting entirely
export RATE_LIMIT_ENABLED=false
```

## Token Usage Monitoring

### Tracking

The system automatically tracks:
- Total prompt tokens (input)
- Total completion tokens (output)
- Total tokens consumed
- Total number of requests

### Monitoring Endpoint

**GET** `/api/v1/ai/usage`

Returns current usage statistics:

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
  }
}
```

### Alerting

**Alert Threshold**: 100,000 tokens per hour (configurable)

When token usage exceeds the threshold, `alert_triggered` becomes `true`. This can be used to:
- Send notifications to administrators
- Temporarily restrict service
- Scale rate limits more aggressively
- Switch to a more economical model

## Configuration

All cost control settings can be configured via environment variables:

### Model Configuration

```bash
# AI Model Selection
GROK_MODEL=grok-4-fast

# Cost-controlled defaults
GROK_DEFAULT_TEMPERATURE=0.7
GROK_DEFAULT_MAX_TOKENS=1500
GROK_CHAT_MAX_TOKENS=2000
GROK_REWRITE_MAX_TOKENS=1000
GROK_AUTOCOMPLETE_MAX_TOKENS=500
```

### Rate Limiting

```bash
# General rate limits
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# AI-specific rate limits (more restrictive)
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=50
```

### Token Usage Monitoring

```bash
# Token tracking
TOKEN_USAGE_TRACKING_ENABLED=true
TOKEN_USAGE_ALERT_THRESHOLD=100000
```

## Cost Estimation

### Per Request Costs (Approximate)

Based on typical usage patterns:

| Endpoint | Avg Tokens | Estimated Cost* |
|----------|------------|-----------------|
| Chat | ~1500 | $0.0015 |
| Rewrite | ~800 | $0.0008 |
| Autocomplete | ~300 | $0.0003 |

*Actual costs depend on xAI's pricing for grok-4-fast

### Per User Costs (Monthly)

With default rate limits:
- Max requests per month: 50 requests/hr × 24 hr × 30 days = 36,000 requests
- At 75% utilization: 27,000 requests
- Estimated cost: **$5-10 per active user per month**

### Scaling Considerations

For 100 active users:
- Monthly cost: $500-1,000
- Per user per month: $5-10
- This is **sustainable for a free service** with the implemented controls

## Best Practices

### For Development

1. **Use `.env` for local testing**:
   ```bash
   cp .env.example .env
   # Edit .env with your test API keys
   ```

2. **Disable rate limiting during development**:
   ```bash
   RATE_LIMIT_ENABLED=false
   ```

3. **Monitor token usage**:
   ```bash
   curl http://localhost:8000/api/v1/ai/usage
   ```

### For Production

1. **Enable all protections**:
   ```bash
   RATE_LIMIT_ENABLED=true
   TOKEN_USAGE_TRACKING_ENABLED=true
   ```

2. **Set up monitoring alerts**:
   - Poll `/api/v1/ai/usage` every minute
   - Alert when `alert_triggered` is true
   - Track daily/weekly token consumption trends

3. **Review and adjust limits**:
   - Start conservative (5/min, 50/hr)
   - Monitor user complaints and usage patterns
   - Gradually increase if budget allows

4. **Implement authentication**:
   - Move from IP-based to user-based rate limiting
   - Track usage per authenticated user
   - Allow premium users higher limits

## Testing

### Running Tests

```bash
# All AI tests
pytest tests/test_ai.py tests/test_ai_cost_control.py -v

# Just cost control tests
pytest tests/test_ai_cost_control.py -v
```

### Test Coverage

- ✅ Model configuration (grok-4-fast)
- ✅ Cost-controlled defaults
- ✅ AI-specific rate limits
- ✅ Token usage tracking
- ✅ Usage monitoring endpoint
- ✅ Alert threshold triggering
- ✅ Configuration validation

## Troubleshooting

### Issue: Rate limit errors in testing

**Solution**: Temporarily disable rate limiting:
```bash
export RATE_LIMIT_ENABLED=false
```

### Issue: Token usage not tracking

**Solution**: Ensure tracking is enabled:
```bash
export TOKEN_USAGE_TRACKING_ENABLED=true
```

### Issue: High token usage

**Solutions**:
1. Reduce max_tokens limits
2. Increase temperature (for shorter responses)
3. Add more aggressive rate limiting
4. Review prompts for unnecessary verbosity

## Future Enhancements

### Planned Improvements

1. **Per-User Budget Tracking**
   - Track tokens per authenticated user
   - Implement daily/monthly user budgets
   - Gracefully degrade service when budget exceeded

2. **Dynamic Rate Limiting**
   - Adjust limits based on current usage
   - Implement backoff during high load
   - Priority queuing for premium users

3. **Cost Dashboard**
   - Real-time cost visualization
   - Historical usage trends
   - User-level cost breakdown
   - Budget forecasting

4. **Model Selection API**
   - Allow clients to choose models
   - Enforce cost-based restrictions
   - Fallback to cheaper models when possible

5. **Caching**
   - Cache common queries
   - Reduce redundant API calls
   - Significant cost savings on repeated questions

## References

- [xAI API Documentation](https://docs.x.ai/)
- [SlowAPI Rate Limiting](https://github.com/laurents/slowapi)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Cost Control Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

## Support

For questions or issues:
1. Check this documentation
2. Review test files for examples
3. Check server logs for detailed errors
4. Open an issue on GitHub with error details

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
