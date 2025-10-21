# FlashCase 📚⚖️

> A modern web flashcard app tailored for law students that combines spaced repetition, community decks, and AI-assisted content creation.

## Product Vision

FlashCase empowers law students to master complex legal concepts through intelligent, personalized study tools. By combining proven spaced repetition techniques with collaborative learning and AI-powered content generation, FlashCase transforms how law students prepare for exams and build long-term legal knowledge.

### Our Mission

To make legal education more accessible, efficient, and effective by providing law students with cutting-edge study tools that adapt to their learning pace and help them retain critical legal knowledge throughout their careers.

## Why FlashCase?

Law school demands memorization of vast amounts of complex information—from case law and statutes to legal principles and procedures. Traditional study methods are time-consuming and often ineffective. FlashCase addresses this by:

- **Spaced Repetition Algorithm**: Optimize study time by focusing on cards you're about to forget
- **Community-Driven Content**: Access and contribute to professionally curated decks for every course
- **AI-Assisted Creation**: Generate flashcards from case briefs, outlines, and textbooks using AI
- **Law School Specific**: Built with legal terminology, citation formats, and bar exam prep in mind
- **Cross-Platform**: Study anywhere—web, mobile, or desktop

## Key Features

### 🧠 Smart Learning
- Evidence-based spaced repetition system (SRS)
- Personalized study schedules based on your retention patterns
- Performance analytics and progress tracking

### 👥 Community Decks
- Browse verified decks for popular law school courses
- Share and collaborate on deck creation
- Upvote and rate community contributions
- Subject-specific collections (Constitutional Law, Torts, Contracts, etc.)

### 🤖 AI-Powered Content
- Convert case briefs to flashcards automatically
- Extract key concepts from legal outlines
- Generate practice questions from study materials
- Smart suggestions for card improvements

### 📊 Progress Tracking
- Visualize learning curves and retention rates
- Track study streaks and time invested
- Compare progress across different subjects
- Bar exam readiness indicators

## Technology Stack

### Frontend
- **Next.js 15** with App Router
- **React 19** for UI components
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- Responsive design for all devices

### Backend
- **FastAPI** (Python) for REST API
- **SQLModel** ORM with SQLite database
- **JWT** authentication with bcrypt
- **Pydantic** for data validation
- Rate limiting and request throttling

### AI/ML
- **Grok AI** (xAI) integration via API
- **CourtListener API** for legal case law
- Automated content moderation (profanity filtering)
- SM-2 spaced repetition algorithm

### Infrastructure
- **Docker** containers for both services
- **Docker Compose** for local development
- GitHub Actions for CI/CD
- SQLite for development, PostgreSQL ready for production

## Architecture

FlashCase follows a modern separation of concerns with:

- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11
- **Database**: SQLite with SQLModel ORM
- **Deployment**: Docker and docker-compose for local parity

### Repository Structure

```
FlashCase/
├── frontend/           # Next.js frontend application
│   ├── app/           # App router pages
│   ├── public/        # Static assets
│   └── Dockerfile     # Frontend container
├── backend/           # FastAPI backend application
│   ├── app/          # Application code
│   │   ├── core/     # Config and database
│   │   ├── models/   # SQLModel models
│   │   └── routers/  # API endpoints
│   └── Dockerfile    # Backend container
├── docker-compose.yml # Orchestration for local development
└── docs/             # Additional documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Node.js 20+ and Python 3.11+ for local development

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/aubreyhayes47/FlashCase.git
cd FlashCase
```

2. Start both services:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

The frontend will be available at http://localhost:3000

## API Documentation

The FastAPI backend provides automatic interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

**Decks & Cards:**
- `GET /api/v1/decks/` - List all decks
- `POST /api/v1/decks/` - Create a new deck
- `GET /api/v1/cards/` - List cards
- `POST /api/v1/cards/` - Create a new card

**Study System:**
- `GET /api/v1/study/session/{deck_id}` - Get cards due for review
- `POST /api/v1/study/review/{card_id}` - Submit review and update progress

**AI Features:**
- `POST /api/v1/ai/chat` - Chat with AI assistant
- `POST /api/v1/ai/rewrite-card` - Improve flashcard quality
- `POST /api/v1/ai/autocomplete-card` - Get AI suggestions

**Moderation:**
- `POST /api/v1/reports/` - Report inappropriate content
- `GET /api/v1/reports/my-reports` - View your reports

## Features

### ✅ Implemented Features

**Core Functionality:**
- Next.js 15 frontend with TypeScript and Tailwind CSS
- FastAPI backend with automatic OpenAPI documentation
- SQLite database with SQLModel ORM
- Docker containers and docker-compose orchestration

**Authentication & Security:**
- JWT-based authentication with secure password hashing
- Protected API endpoints with user authorization
- Automated content moderation (profanity filtering)
- User reporting system for inappropriate content
- Rate limiting on all API endpoints

**Study System:**
- SM-2 spaced repetition algorithm
- Study sessions with due date tracking
- Card review with quality ratings (0-5)
- Progress tracking and statistics

**AI-Powered Features:**
- AI chat assistant with legal context
- CourtListener case law integration
- Flashcard rewriting and improvement
- Autocomplete suggestions for card creation
- Token usage tracking and cost controls

**Content Management:**
- Create, read, update, delete decks and cards
- Public and private deck visibility
- Card organization by deck
- User-specific content ownership

### 🔄 Planned Features

- Enhanced admin moderation dashboard
- Community deck discovery and sharing
- Study statistics and analytics dashboard
- Mobile-responsive UI improvements
- Export/import deck functionality
- Collaborative deck editing

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Smoke Tests

After deployment, run smoke tests to verify functionality:

```bash
./smoke_tests.sh
# Or specify custom URLs:
BACKEND_URL=https://api.flashcase.com FRONTEND_URL=https://flashcase.com ./smoke_tests.sh
```

## CI/CD Pipeline

FlashCase includes automated CI/CD workflows using GitHub Actions:

- **Backend CI**: Runs tests on every push to backend code
- **Frontend CI**: Builds and type-checks frontend on every push
- **Docker Build**: Tests Docker builds and docker-compose setup
- **Deploy**: Template for deployment to various platforms

Workflows automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

See `.github/workflows/` for workflow configurations.

## Deployment

FlashCase supports deployment to multiple platforms. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

### Quick Deploy Options

**Render (Easiest, Free Tier Available)**
- Connect GitHub repository
- Auto-deploy on push
- Managed PostgreSQL included
- Free SSL certificates

**Heroku (Simple PaaS)**
- Git-based deployment
- Rich addon ecosystem
- Easy scaling

**AWS (Production Scale)**
- ECS with Fargate
- Full control and scaling
- Integrates with AWS ecosystem

**GCP Cloud Run (Cost-Effective)**
- Serverless containers
- Auto-scaling (to zero)
- Pay-per-use pricing

### Deployment Documentation

- 📘 [Full Deployment Guide](DEPLOYMENT.md) - Platform-specific instructions
- 📊 [Monitoring Guide](MONITORING.md) - Set up monitoring and logging
- 💰 [Cost Control](backend/COST_CONTROL.md) - AI token usage and cost tracking

### Key Environment Variables

**Backend** (see `backend/.env.example` for full list):

```bash
# Authentication (Required)
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./flashcase.db  # Use PostgreSQL for production

# AI Configuration (Optional - for AI features)
GROK_API_KEY=<your-xai-api-key>
GROK_MODEL=grok-4-fast
COURTLISTENER_API_KEY=<your-courtlistener-key>

# Security & Rate Limiting
CORS_ORIGINS=["http://localhost:3000"]  # Update for production
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10

# Monitoring
ENVIRONMENT=production
LOG_LEVEL=INFO
TOKEN_USAGE_TRACKING_ENABLED=true
```

**Frontend**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Monitoring & Observability

### Health Checks

Monitor system health with these endpoints:

```bash
# Backend API health
curl http://localhost:8000/api/v1/health

# AI service health (checks Grok API availability)
curl http://localhost:8000/api/v1/ai/health

# AI token usage statistics
curl http://localhost:8000/api/v1/ai/usage
```

### Logging

Environment-aware logging is configured automatically:
- **Development**: Colored, human-readable console logs
- **Production**: JSON-formatted structured logs for parsing
- Includes request IDs, user context, and performance metrics

### AI Cost Monitoring

Track AI API usage to control costs:
- Real-time token usage tracking
- Configurable alert thresholds
- Per-endpoint token limits
- Usage statistics via `/api/v1/ai/usage` endpoint

For detailed monitoring setup, see [MONITORING.md](MONITORING.md).

## Contributing

We welcome contributions from the community! Whether you're a developer, designer, law student, or educator, there are many ways to help make FlashCase better.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct and community guidelines
- How to report bugs and suggest features
- Development workflow and pull request process
- Ways to contribute without coding (feedback, testing, content creation)

## License

FlashCase is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guides
- **[MONITORING.md](MONITORING.md)** - Monitoring and observability
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[API Documentation](backend/API_DOCUMENTATION.md)** - Complete API reference
- **[Product Vision](PRODUCT_VISION.md)** - Product strategy and roadmap

## Support

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/aubreyhayes47/FlashCase/issues)
- **Documentation**: See the `/docs` directory and individual documentation files
- **API Docs**: Interactive documentation at http://localhost:8000/docs

---

**Status**: Active development - FlashCase is functional with core features implemented. We welcome contributions and feedback from the law student community!

*Last updated: October 21, 2025*
