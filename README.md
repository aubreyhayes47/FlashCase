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
- Modern web framework (React/Vue/Svelte)
- Progressive Web App (PWA) capabilities
- Responsive design for all devices

### Backend
- RESTful API architecture
- Authentication and authorization
- Database for user data and flashcards
- Caching for performance

### AI/ML
- Large Language Model integration for content generation
- Natural language processing for text extraction
- Machine learning for personalized SRS algorithm

### Infrastructure
- Cloud hosting for scalability
- CDN for fast global access
- Automated testing and deployment

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

- `GET /api/v1/health` - Health check
- `GET /api/v1/decks` - List all decks
- `POST /api/v1/decks` - Create a new deck
- `GET /api/v1/cards` - List cards
- `POST /api/v1/cards` - Create a new card

## Features

### Current (MVP - Phase 1)

- ✅ Frontend and backend repository separation
- ✅ Next.js SPA with core pages (dashboard, discover, study, create)
- ✅ FastAPI backend with main routers
- ✅ SQLite database with SQLModel
- ✅ Dependency injection for database sessions
- ✅ Docker containers for both services
- ✅ docker-compose for local development
- ✅ JWT authentication with bcrypt password hashing
- ✅ Automated content moderation (profanity filtering)
- ✅ User reporting system for inappropriate content
- ✅ Admin review and moderation tools
- ✅ Legal and AI disclaimers on all relevant pages

### Planned

- 🔄 Spaced repetition algorithm (SRS) - In Progress
- 🔄 Community deck sharing
- 🔄 AI-powered card generation (Phase 3)
- 🔄 Mobile apps (Phase 4)

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

For production deployment, configure:

```bash
# Required
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=<your-database-url>
GROK_API_KEY=<your-xai-api-key>
CORS_ORIGINS=["https://your-frontend-url.com"]

# Recommended
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
TOKEN_USAGE_TRACKING_ENABLED=true
```

## Monitoring & Observability

### AI Token Usage Monitoring

FlashCase includes real-time AI token usage tracking:

```bash
# View current usage
curl http://localhost:8000/api/v1/ai/usage

# Monitor continuously
cd backend
python monitor_token_usage.py
```

### Structured Logging

Production-ready JSON logging is configured automatically:

- Development: Colored, human-readable logs
- Production: JSON-formatted structured logs
- Includes request tracking, AI metrics, and performance data

See [MONITORING.md](MONITORING.md) for complete monitoring setup.

### Health Checks

- Backend: `GET /api/v1/health`
- AI Service: `GET /api/v1/ai/health`
- Token Usage: `GET /api/v1/ai/usage`

## Contributing

We welcome contributions from the community! Whether you're a developer, designer, law student, or educator, there are many ways to help make FlashCase better.

*Contribution guidelines coming soon*

## License

FlashCase is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [Link to docs]
- **Issues**: Report bugs and request features via GitHub Issues
- **Community**: Join our Discord/Slack for discussions
- **Contact**: [Contact information]

---

**Note**: FlashCase is currently in early development. This README represents our product vision and planned features. We're actively seeking feedback from law students and legal educators to ensure we're building the right solution. If you're interested in beta testing or providing input, please reach out!

*Last updated: October 2025*
