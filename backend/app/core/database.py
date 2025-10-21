from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings


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
