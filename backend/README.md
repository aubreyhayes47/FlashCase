# FlashCase Backend

FastAPI backend for FlashCase flashcard application.

## Features

- **FastAPI** with automatic OpenAPI documentation
- **SQLModel** ORM with SQLite database (PostgreSQL ready)
- **JWT Authentication** with bcrypt password hashing
- **Spaced Repetition System** (SM-2 algorithm)
- **AI Integration** with Grok and CourtListener APIs
- **Content Moderation** with automated profanity filtering
- **Rate Limiting** on all endpoints
- **Structured Logging** for production monitoring
- RESTful API endpoints for complete CRUD operations

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Docker

Build and run with Docker:
```bash
docker build -t flashcase-backend .
docker run -p 8000:8000 flashcase-backend
```

## API Endpoints

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Create user account
- `POST /api/v1/auth/login` - Login with credentials
- `GET /api/v1/auth/me` - Get current user

**Decks & Cards:**
- `GET /api/v1/decks/` - List all decks
- `POST /api/v1/decks/` - Create new deck
- `GET /api/v1/cards/` - List cards
- `POST /api/v1/cards/` - Create new card

**Study System:**
- `GET /api/v1/study/session/{deck_id}` - Get study session
- `POST /api/v1/study/review/{card_id}` - Review card

**AI Features:**
- `POST /api/v1/ai/chat` - Chat with AI
- `POST /api/v1/ai/rewrite-card` - Rewrite flashcard
- `GET /api/v1/ai/health` - Check AI service health

**Content Moderation:**
- `POST /api/v1/reports/` - Create report
- `GET /api/v1/reports/my-reports` - View my reports

## Project Structure

```
backend/
├── app/
│   ├── core/              # Core configuration and database
│   │   ├── config.py      # Settings and configuration
│   │   ├── database.py    # Database connection
│   │   └── logging_config.py  # Structured logging
│   ├── models/            # SQLModel database models
│   │   ├── user.py        # User model
│   │   ├── deck.py        # Deck model
│   │   ├── card.py        # Card model
│   │   ├── study_log.py   # Study session tracking
│   │   └── report.py      # Content report model
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── decks.py       # Deck CRUD endpoints
│   │   ├── cards.py       # Card CRUD endpoints
│   │   ├── study.py       # Study session endpoints
│   │   ├── ai.py          # AI-powered features
│   │   ├── reports.py     # Content moderation
│   │   └── health.py      # Health check
│   ├── services/          # Business logic
│   │   ├── srs.py         # Spaced repetition algorithm
│   │   └── moderation.py  # Content moderation
│   ├── middleware/        # Custom middleware
│   └── main.py            # FastAPI application
├── tests/                 # Test files (pytest)
├── .env.example           # Environment variable template
├── Dockerfile             # Docker configuration
└── requirements.txt       # Python dependencies
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Authentication
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./flashcase.db

# AI (Optional)
GROK_API_KEY=<your-xai-api-key>
COURTLISTENER_API_KEY=<your-courtlistener-key>

# Security
CORS_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_ENABLED=true
```

See `.env.example` for complete configuration options.

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

**Test Coverage**: 126 passing tests covering authentication, CRUD operations, SRS algorithm, AI features, and content moderation.

## Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database models and relationships
- **[AI_INTEGRATION.md](AI_INTEGRATION.md)** - AI features and integration guide
- **[CONTENT_MODERATION.md](CONTENT_MODERATION.md)** - Moderation system details
- **[COST_CONTROL.md](COST_CONTROL.md)** - AI cost management strategies

## Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

---

**Last Updated**: October 21, 2025
