# Core SRS Engine - Quick Start Guide

## Overview
This implementation provides a complete Spaced Repetition System (SRS) based on the SM-2 algorithm for the FlashCase application.

## Quick Test

Start the server:
```bash
cd backend
uvicorn app.main:app --reload
```

Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Get Study Session
Get cards due for review:

```bash
GET /api/v1/study/session/{deck_id}?user_id={user_id}&limit=20
```

Example:
```bash
curl "http://localhost:8000/api/v1/study/session/1?user_id=1"
```

Response:
```json
[
    {
        "id": 1,
        "deck_id": 1,
        "front": "What is mens rea?",
        "back": "The mental element of a crime",
        "ease_factor": 2.5,
        "interval": 0,
        "repetitions": 0,
        "due_date": "2025-10-21T03:52:06.452495"
    }
]
```

### Submit Review
Review a card with quality rating (0-5):

```bash
POST /api/v1/study/review/{card_id}
```

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/study/review/1" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "quality": 5}'
```

Response:
```json
{
    "card_id": 1,
    "quality": 5,
    "new_ease_factor": 2.6,
    "new_interval": 1,
    "new_repetitions": 1,
    "next_due_date": "2025-10-22T03:52:06.515586"
}
```

## Quality Ratings

| Rating | Meaning | Action |
|--------|---------|--------|
| 5 | Perfect response | Increase interval significantly |
| 4 | Correct after hesitation | Increase interval moderately |
| 3 | Correct with difficulty | Increase interval slightly |
| 2 | Incorrect, but answer familiar | Reset to beginning |
| 1 | Incorrect, correct answer seemed easy | Reset to beginning |
| 0 | Complete blackout | Reset to beginning |

## SM-2 Algorithm Details

### Intervals
- **First correct review**: 1 day
- **Second correct review**: 6 days  
- **Subsequent reviews**: interval × ease_factor

### Ease Factor
- Initial value: 2.5
- Floor: 1.3 (prevents "ease hell")
- Adjusted based on quality rating

### Incorrect Responses
- Quality < 3 resets:
  - Repetitions to 0
  - Interval to 1 day
  - Ease factor decreases but respects floor

## Testing

Run unit tests:
```bash
cd backend
pytest tests/test_srs.py -v
```

Expected output:
```
15 passed, 3 warnings in 0.02s
```

## Database Schema

The StudyLog model includes:
- `user_id`: Foreign key to user
- `card_id`: Foreign key to card
- `ease_factor`: Current ease factor (≥ 1.3)
- `interval`: Days until next review
- `repetitions`: Consecutive correct reviews
- `last_rating`: Most recent quality (0-5)
- `due_date`: When card is next due
- `reviewed_at`: Timestamp of last review

## Example Workflow

1. **Get due cards**:
   ```bash
   curl "http://localhost:8000/api/v1/study/session/1?user_id=1"
   ```

2. **Review first card** (perfect recall):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/study/review/1" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "quality": 5}'
   ```
   Result: Card due in 1 day

3. **Review again** (next day):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/study/review/1" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "quality": 5}'
   ```
   Result: Card due in 6 days

4. **Review third time** (6 days later):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/study/review/1" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "quality": 5}'
   ```
   Result: Card due in ~16 days (6 × 2.7)

## Documentation

- **IMPLEMENTATION_SUMMARY.md**: Complete implementation details
- **STUDY_API_TESTING.md**: Testing results and examples
- **DATABASE_SCHEMA.md**: Database design and relationships

## Files

```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   └── srs.py              # SM-2 algorithm
│   ├── routers/
│   │   └── study.py            # Study endpoints
│   └── models/
│       └── study_log.py        # Updated model
├── tests/
│   └── test_srs.py             # Unit tests
├── IMPLEMENTATION_SUMMARY.md   # Complete details
└── STUDY_API_TESTING.md        # Test results
```

## Next Steps

To integrate with frontend:
1. Add authentication to endpoints
2. Create study session UI
3. Implement card review interface
4. Add progress tracking dashboard

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review test cases: `backend/tests/test_srs.py`
- Read implementation notes: `IMPLEMENTATION_SUMMARY.md`
