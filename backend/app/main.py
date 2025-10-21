from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.routers import decks, cards, health, ai, study, auth, reports
from app.middleware import setup_rate_limiting

app = FastAPI(title=settings.project_name)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup rate limiting
limiter = setup_rate_limiting(app)

# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(decks.router, prefix=settings.api_v1_prefix)
app.include_router(cards.router, prefix=settings.api_v1_prefix)
app.include_router(study.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
app.include_router(reports.router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    create_db_and_tables()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FlashCase API",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
        "ai_health": f"{settings.api_v1_prefix}/ai/health"
    }
