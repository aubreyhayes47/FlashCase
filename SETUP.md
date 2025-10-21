# FlashCase Setup Guide

This guide will help you set up the FlashCase application for local development.

## Prerequisites

- **Option 1 (Recommended)**: Docker and Docker Compose
- **Option 2**: Node.js 20+ and Python 3.11+

## Quick Start with Docker (Recommended)

1. **Clone the repository**:
```bash
git clone https://github.com/aubreyhayes47/FlashCase.git
cd FlashCase
```

2. **Start the services**:
```bash
docker compose up --build
```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env if needed
```

5. **Start the backend server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment**:
```bash
cp .env.local.example .env.local
# Edit .env.local if needed
```

4. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Testing the Setup

### Test Backend API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create a deck
curl -X POST http://localhost:8000/api/v1/decks/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Deck","description":"Testing","is_public":true}'

# List decks
curl http://localhost:8000/api/v1/decks/
```

### Test Frontend

Open your browser and navigate to:
- Home: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- Discover: http://localhost:3000/discover
- Study: http://localhost:3000/study
- Create: http://localhost:3000/create

## Project Structure

```
FlashCase/
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js app router pages
│   │   ├── dashboard/    # Dashboard page
│   │   ├── discover/     # Discover decks page
│   │   ├── study/        # Study session page
│   │   ├── create/       # Card creator page
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Home page
│   ├── public/           # Static assets
│   └── Dockerfile        # Frontend Docker config
│
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── core/        # Configuration & database
│   │   ├── models/      # SQLModel database models
│   │   ├── routers/     # API route handlers
│   │   └── main.py      # FastAPI application
│   └── Dockerfile       # Backend Docker config
│
└── docker-compose.yml   # Multi-service orchestration
```

## API Endpoints

### Health
- `GET /api/v1/health` - API health check

### Decks
- `GET /api/v1/decks/` - List all decks
- `GET /api/v1/decks/{id}` - Get specific deck
- `POST /api/v1/decks/` - Create new deck
- `DELETE /api/v1/decks/{id}` - Delete deck

### Cards
- `GET /api/v1/cards/` - List all cards (optional: ?deck_id=X)
- `GET /api/v1/cards/{id}` - Get specific card
- `POST /api/v1/cards/` - Create new card
- `DELETE /api/v1/cards/{id}` - Delete card

## Database

The application uses SQLite for data persistence. The database file is created automatically on first run at `backend/flashcase.db`.

### Database Models

**Deck**:
- `id`: Integer (Primary Key)
- `name`: String (Indexed)
- `description`: String (Optional)
- `is_public`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

**Card**:
- `id`: Integer (Primary Key)
- `deck_id`: Integer (Foreign Key to Deck)
- `front`: String (Question/Prompt)
- `back`: String (Answer)
- `created_at`: DateTime
- `updated_at`: DateTime

## Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Check that port 8000 is not in use
- Verify all dependencies are installed: `pip list`

### Frontend won't start
- Ensure Node.js 20+ is installed
- Check that port 3000 is not in use
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Database issues
- Delete the database file to reset: `rm backend/flashcase.db`
- The database will be recreated on next backend startup

### Docker issues
- Ensure Docker is running: `docker --version`
- Check logs: `docker compose logs`
- Rebuild images: `docker compose up --build --force-recreate`

## Development Tips

### Backend Development
- API documentation is auto-generated at `/docs`
- Database queries are logged in development mode
- Use `--reload` flag for auto-reload on file changes

### Frontend Development
- Pages auto-reload on file changes
- TypeScript provides type safety
- Tailwind CSS classes are available globally

## Next Steps

1. ✅ Set up authentication and user management
2. ✅ Implement spaced repetition algorithm
3. ✅ Add community deck features
4. ✅ Integrate AI for card generation
5. ✅ Deploy to production

## Support

For issues and questions:
- GitHub Issues: https://github.com/aubreyhayes47/FlashCase/issues
- Documentation: See `/docs` directory
