# FlashCase Backend

FastAPI backend for FlashCase flashcard application.

## Features

- FastAPI with automatic OpenAPI documentation
- SQLite database with SQLModel ORM
- Dependency injection for database sessions
- CORS configuration for frontend integration
- RESTful API endpoints for decks and cards

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

### Health Check
- `GET /api/v1/health` - Check API health

### Decks
- `GET /api/v1/decks` - List all decks
- `GET /api/v1/decks/{id}` - Get specific deck
- `POST /api/v1/decks` - Create new deck
- `DELETE /api/v1/decks/{id}` - Delete deck

### Cards
- `GET /api/v1/cards` - List cards (optional: ?deck_id=X)
- `GET /api/v1/cards/{id}` - Get specific card
- `POST /api/v1/cards` - Create new card
- `DELETE /api/v1/cards/{id}` - Delete card

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and database
│   ├── models/         # SQLModel database models
│   ├── routers/        # API route handlers
│   └── main.py         # FastAPI application
├── tests/              # Test files
├── Dockerfile          # Docker configuration
└── requirements.txt    # Python dependencies
```
