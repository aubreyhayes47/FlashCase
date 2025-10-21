from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings
# Import models to ensure they are registered with SQLModel
from app.models.user import User
from app.models.deck import Deck
from app.models.card import Card
from app.models.report import Report
from app.models.study_log import StudyLog
from app.models.user_deck import UserDeck


# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Log SQL queries in development
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for database session."""
    with Session(engine) as session:
        yield session


# Alias for consistency with common naming conventions
get_db = get_session
