# FlashCase Database Schema Documentation

This document describes the complete database schema for FlashCase, implemented using SQLModel.

## Overview

FlashCase uses SQLite for development with a path to migrate to PostgreSQL for production. All models are defined using SQLModel, which provides type-safe database models with automatic validation.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    User     │       │   UserDeck   │       │    Deck     │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id          │◄──────│ user_id (FK) │──────►│ id          │
│ email       │       │ deck_id (FK) │       │ name        │
│ username    │       │ is_owner     │       │ description │
│ is_admin    │       │ is_favorite  │       │ is_public   │
│ ...         │       │ added_at     │       │ ...         │
└─────────────┘       └──────────────┘       └─────────────┘
       │              (unique: user_id,               │
       │               deck_id)                       │
       │                                              │
       │              ┌──────────────┐                │
       │              │  StudyLog    │                │
       │              ├──────────────┤                │
       ├─────────────►│ user_id (FK) │                │
       │              │ card_id (FK) │                │
       │              │ reviewed_at  │                │
       │              │ ease_factor  │                │
       │              │ interval     │       ┌─────────────┐
       │              │ next_review  │       │    Card     │
       │              └──────────────┘       ├─────────────┤
       │                       ▲             │ id          │
       │                       └─────────────│ deck_id (FK)│
       │                                     │ front       │
       │              ┌──────────────┐       │ back        │
       │              │   Report     │       └─────────────┘
       │              ├──────────────┤              │
       ├─────────────►│reporter_id(FK)              │
       │              │ reviewed_by(FK)      ┌──────────────┐
       └──────────────┤ report_type  │      │DeckMetadata  │
                      │ content_id   │      ├──────────────┤
                      │ status       │      │ deck_id (FK) │◄──┐
                      │ reason       │      │ card_count   │   │
                      └──────────────┘      │ total_reviews│   │
                                            │ avg_rating   │   │
                                            │ last_studied │   │
                                            └──────────────┘   │
                                                   │           │
                                                   └───────────┘
```

## Models

### User

Stores user authentication and account information.

**Table:** `user`

| Column           | Type     | Constraints                    | Description                      |
|------------------|----------|--------------------------------|----------------------------------|
| id               | INTEGER  | PRIMARY KEY                    | Auto-incrementing user ID        |
| email            | VARCHAR  | NOT NULL, UNIQUE, INDEX        | User's email address             |
| username         | VARCHAR  | NOT NULL, UNIQUE, INDEX        | User's display name              |
| hashed_password  | VARCHAR  | NOT NULL                       | Bcrypt hashed password           |
| is_active        | BOOLEAN  | NOT NULL, DEFAULT TRUE         | Account active status            |
| is_admin         | BOOLEAN  | NOT NULL, DEFAULT FALSE        | Admin user flag                  |
| created_at       | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Account creation timestamp       |
| updated_at       | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Last update timestamp            |

**Relationships:**
- One-to-many with `UserDeck` (user owns/accesses multiple decks)
- One-to-many with `StudyLog` (user has multiple study sessions)

**Indexes:**
- `ix_user_email` (unique)
- `ix_user_username` (unique)

---

### Deck

Represents a collection of flashcards.

**Table:** `deck`

| Column      | Type     | Constraints                    | Description                  |
|-------------|----------|--------------------------------|------------------------------|
| id          | INTEGER  | PRIMARY KEY                    | Auto-incrementing deck ID    |
| name        | VARCHAR  | NOT NULL, INDEX                | Deck name                    |
| description | VARCHAR  | NULL                           | Optional deck description    |
| is_public   | BOOLEAN  | NOT NULL, DEFAULT FALSE        | Public visibility flag       |
| created_at  | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Deck creation timestamp      |
| updated_at  | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Last update timestamp        |

**Relationships:**
- One-to-many with `Card` (deck contains multiple cards)
- One-to-one with `DeckMetadata` (deck has metadata)
- One-to-many with `UserDeck` (deck accessible by multiple users)

**Indexes:**
- `ix_deck_name`

---

### Card

Individual flashcard within a deck.

**Table:** `card`

| Column      | Type     | Constraints                    | Description                  |
|-------------|----------|--------------------------------|------------------------------|
| id          | INTEGER  | PRIMARY KEY                    | Auto-incrementing card ID    |
| deck_id     | INTEGER  | NOT NULL, FK(deck.id), INDEX   | Parent deck reference        |
| front       | VARCHAR  | NOT NULL                       | Question/prompt text         |
| back        | VARCHAR  | NOT NULL                       | Answer/response text         |
| created_at  | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Card creation timestamp      |
| updated_at  | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Last update timestamp        |

**Relationships:**
- Many-to-one with `Deck` (cards belong to one deck)
- One-to-many with `StudyLog` (card has multiple study records)

**Foreign Keys:**
- `deck_id` → `deck.id` (CASCADE on delete recommended for production)

**Indexes:**
- `ix_card_deck_id`

---

### DeckMetadata

Statistics and metadata about a deck.

**Table:** `deck_metadata`

| Column        | Type     | Constraints                          | Description                        |
|---------------|----------|--------------------------------------|------------------------------------|
| id            | INTEGER  | PRIMARY KEY                          | Auto-incrementing metadata ID      |
| deck_id       | INTEGER  | NOT NULL, FK(deck.id), UNIQUE, INDEX | Deck reference                     |
| card_count    | INTEGER  | NOT NULL, DEFAULT 0                  | Number of cards in deck            |
| total_reviews | INTEGER  | NOT NULL, DEFAULT 0                  | Total study sessions count         |
| average_rating| FLOAT    | NULL                                 | Average user rating (future)       |
| last_studied  | DATETIME | NULL                                 | Most recent study session          |
| created_at    | DATETIME | NOT NULL, DEFAULT CURRENT_TIME       | Metadata creation timestamp        |
| updated_at    | DATETIME | NOT NULL, DEFAULT CURRENT_TIME       | Last update timestamp              |

**Relationships:**
- One-to-one with `Deck` (one metadata record per deck)

**Foreign Keys:**
- `deck_id` → `deck.id` (unique constraint ensures one-to-one)

**Indexes:**
- `ix_deck_metadata_deck_id` (unique)

---

### StudyLog

Records of individual study sessions for spaced repetition.

**Table:** `study_log`

| Column      | Type     | Constraints                          | Description                          |
|-------------|----------|--------------------------------------|--------------------------------------|
| id          | INTEGER  | PRIMARY KEY                          | Auto-incrementing log ID             |
| user_id     | INTEGER  | NOT NULL, FK(user.id), INDEX         | User who studied                     |
| card_id     | INTEGER  | NOT NULL, FK(card.id), INDEX         | Card that was studied                |
| reviewed_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIME, INDEX| Study session timestamp              |
| ease_factor | FLOAT    | NOT NULL, DEFAULT 2.5                | Spaced repetition ease factor (SM-2) |
| interval    | INT      | NOT NULL, DEFAULT 0                  | Days until next review               |
| next_review | DATETIME | NOT NULL, DEFAULT CURRENT_TIME       | Scheduled next review date           |
| created_at  | DATETIME | NOT NULL, DEFAULT CURRENT_TIME       | Log creation timestamp               |

**Relationships:**
- Many-to-one with `User` (user has many study sessions)
- Many-to-one with `Card` (card has many study records)

**Foreign Keys:**
- `user_id` → `user.id`
- `card_id` → `card.id`

**Indexes:**
- `ix_study_log_user_id`
- `ix_study_log_card_id`
- `ix_study_log_reviewed_at`

**Spaced Repetition Fields:**
- `ease_factor`: SM-2 algorithm parameter (typically 1.3-2.5)
- `interval`: Days until next review
- `next_review`: Calculated timestamp for next review

---

### UserDeck

Many-to-many relationship between users and decks.

**Table:** `user_deck`

| Column      | Type     | Constraints                                | Description                    |
|-------------|----------|--------------------------------------------|--------------------------------|
| id          | INTEGER  | PRIMARY KEY                                | Auto-incrementing ID           |
| user_id     | INTEGER  | NOT NULL, FK(user.id), INDEX               | User reference                 |
| deck_id     | INTEGER  | NOT NULL, FK(deck.id), INDEX               | Deck reference                 |
| is_owner    | BOOLEAN  | NOT NULL, DEFAULT FALSE                    | User is deck owner             |
| is_favorite | BOOLEAN  | NOT NULL, DEFAULT FALSE                    | User favorited deck            |
| added_at    | DATETIME | NOT NULL, DEFAULT CURRENT_TIME             | When user added deck           |

**Relationships:**
- Many-to-one with `User` (users can access multiple decks)
- Many-to-one with `Deck` (decks can be accessed by multiple users)

**Foreign Keys:**
- `user_id` → `user.id`
- `deck_id` → `deck.id`

**Unique Constraint:**
- `unique_user_deck` on `(user_id, deck_id)` - prevents duplicate associations

**Indexes:**
- `ix_user_deck_user_id`
- `ix_user_deck_deck_id`

**Notes:**
- `is_owner=True` indicates the user created the deck
- Multiple users can own the same deck (collaborative decks)
- `is_favorite` allows users to bookmark decks for quick access

---

### Report

Content moderation reports submitted by users.

**Table:** `report`

| Column       | Type     | Constraints                    | Description                      |
|--------------|----------|--------------------------------|----------------------------------|
| id           | INTEGER  | PRIMARY KEY                    | Auto-incrementing report ID      |
| reporter_id  | INTEGER  | NOT NULL, FK(user.id), INDEX   | User who created the report      |
| report_type  | VARCHAR  | NOT NULL                       | Type: "deck" or "card"           |
| content_id   | INTEGER  | NOT NULL, INDEX                | ID of reported deck or card      |
| reason       | VARCHAR  | NOT NULL                       | Report reason category           |
| description  | VARCHAR  | NULL                           | Optional additional details      |
| status       | VARCHAR  | NOT NULL, DEFAULT "pending"    | Status: pending/reviewed/etc     |
| reviewed_by  | INTEGER  | NULL, FK(user.id)              | Admin who reviewed               |
| admin_notes  | VARCHAR  | NULL                           | Admin review notes               |
| created_at   | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Report creation timestamp        |
| updated_at   | DATETIME | NOT NULL, DEFAULT CURRENT_TIME | Last update timestamp            |

**Relationships:**
- Many-to-one with `User` via `reporter_id` (user creates reports)
- Many-to-one with `User` via `reviewed_by` (admin reviews reports)

**Foreign Keys:**
- `reporter_id` → `user.id`
- `reviewed_by` → `user.id` (nullable)

**Indexes:**
- `ix_report_reporter_id`
- `ix_report_content_id`
- `ix_report_status`

**Valid Values:**
- `report_type`: "deck", "card"
- `reason`: "inappropriate", "spam", "copyright", "misleading", "other"
- `status`: "pending", "reviewed", "resolved", "dismissed"

**Notes:**
- Reports allow users to flag inappropriate content
- Admin users can review and update report status
- `reviewed_by` tracks which admin handled the report
- `content_id` references the deck or card being reported (not a foreign key to allow flexibility)

---

## Database Configuration

### SQLite (Development)

```python
# Connection String
DATABASE_URL = "sqlite:///./flashcase.db"

# Engine Configuration
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Required for FastAPI
    echo=True  # SQL logging in development
)
```

**Key Settings:**
- `check_same_thread=False`: Allows SQLite to work with FastAPI's async/threading
- `echo=True`: Logs all SQL queries for debugging

### PostgreSQL (Production - Future)

See `MIGRATIONS.md` for the complete migration guide.

```python
# Connection String Example
DATABASE_URL = "postgresql://user:password@localhost:5432/flashcase"

# Engine Configuration
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)
```

---

## Database Session Management

### Session Dependency

The application provides database sessions via dependency injection:

```python
from app.core.database import get_db
from sqlmodel import Session

@app.get("/endpoint")
async def endpoint(session: Session = Depends(get_db)):
    # Use session here
    pass
```

### Context Manager Usage

For scripts and background tasks:

```python
from app.core.database import engine
from sqlmodel import Session

with Session(engine) as session:
    # Perform database operations
    session.commit()  # Commit when done
```

---

## Common Queries

### Get User's Decks

```python
statement = select(Deck).join(UserDeck).where(UserDeck.user_id == user_id)
decks = session.exec(statement).all()
```

### Get Cards Due for Review

```python
from datetime import datetime

statement = (
    select(Card, StudyLog)
    .join(StudyLog)
    .where(StudyLog.user_id == user_id)
    .where(StudyLog.next_review <= datetime.utcnow())
)
cards_to_review = session.exec(statement).all()
```

### Get Deck with Statistics

```python
statement = (
    select(Deck, DeckMetadata)
    .join(DeckMetadata)
    .where(Deck.id == deck_id)
)
deck, metadata = session.exec(statement).first()
```

### Update Deck Card Count

```python
# After adding/removing cards
metadata = session.get(DeckMetadata, metadata_id)
metadata.card_count = session.exec(
    select(func.count()).where(Card.deck_id == deck_id)
).one()
metadata.updated_at = datetime.utcnow()
session.add(metadata)
session.commit()
```

---

## Data Integrity

### Foreign Key Constraints

All foreign keys are enforced at the database level. Operations that would violate referential integrity will raise an error.

**SQLite:** Requires `PRAGMA foreign_keys = ON` (enabled in engine config)

### Unique Constraints

- `user.email` - Prevents duplicate email addresses
- `user.username` - Prevents duplicate usernames
- `deck_metadata.deck_id` - One metadata record per deck
- `user_deck.(user_id, deck_id)` - Prevents duplicate deck associations

### Cascade Behavior

Current implementation does not specify CASCADE delete behavior. For production, consider:

```python
# Example: Cascade delete cards when deck is deleted
deck_id: int = Field(foreign_key="deck.id", ondelete="CASCADE")
```

---

## Testing

### Test Script

Run the database verification script:

```bash
cd backend
python test_db_models.py
```

This script:
1. Creates all tables
2. Inserts sample data for each model
3. Verifies relationships and constraints
4. Tests foreign key enforcement

### Sample Data

```python
from app.models import User, Deck, Card, DeckMetadata, StudyLog, UserDeck

# Create user
user = User(
    email="student@law.edu",
    username="lawstudent",
    hashed_password="$2b$12$...",
    is_active=True
)

# Create deck
deck = Deck(
    name="Constitutional Law",
    description="Core constitutional concepts",
    is_public=True
)

# Create card
card = Card(
    deck_id=deck.id,
    front="What is judicial review?",
    back="Power of courts to review constitutionality of laws"
)
```

---

## Performance Considerations

### Indexes

All foreign keys are automatically indexed for join performance.

### Additional Indexes (Recommended for Production)

```sql
-- Composite index for study log queries
CREATE INDEX idx_study_user_next ON study_log(user_id, next_review);

-- Full-text search on deck names (PostgreSQL)
CREATE INDEX idx_deck_name_fts ON deck USING gin(to_tsvector('english', name));

-- Card search within deck
CREATE INDEX idx_card_deck_created ON card(deck_id, created_at DESC);
```

### Query Optimization

- Use `select()` statements for type-safe queries
- Leverage `join()` for relationship queries
- Use `limit()` and `offset()` for pagination
- Consider `select_in_loading` for large result sets

---

## Schema Evolution

### Adding New Fields

1. Update SQLModel class
2. Generate migration (with Alembic)
3. Apply migration
4. Update API models if needed

### Example: Adding a Field

```python
class Deck(SQLModel, table=True):
    # ... existing fields ...
    tags: Optional[str] = Field(default=None)  # New field
```

Then generate and apply migration:

```bash
alembic revision --autogenerate -m "Add tags to deck"
alembic upgrade head
```

---

## Security Considerations

1. **Password Storage**: Use bcrypt or argon2 for hashing passwords
2. **SQL Injection**: SQLModel/SQLAlchemy provides protection via parameterized queries
3. **Session Management**: Use secure session tokens, not stored in database
4. **User Input**: Validate all inputs with Pydantic models
5. **Foreign Keys**: Enable enforcement to maintain referential integrity

---

## Backup and Recovery

### SQLite Backup

```bash
# Create backup
cp flashcase.db flashcase.db.backup

# Or use SQLite backup command
sqlite3 flashcase.db ".backup flashcase.db.backup"
```

### PostgreSQL Backup

```bash
# Dump database
pg_dump flashcase > backup.sql

# Restore database
psql flashcase < backup.sql
```

---

## Monitoring

### Database Size

```sql
-- SQLite
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- PostgreSQL
SELECT pg_size_pretty(pg_database_size('flashcase'));
```

### Table Row Counts

```sql
SELECT COUNT(*) FROM user;
SELECT COUNT(*) FROM deck;
SELECT COUNT(*) FROM card;
SELECT COUNT(*) FROM study_log;
```

### Performance Monitoring

- Monitor query execution times in logs (when `echo=True`)
- Use database-specific tools (SQLite Analyzer, pgAdmin)
- Track connection pool usage in production

---

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Database Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SM-2 Spaced Repetition Algorithm](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [MIGRATIONS.md](./MIGRATIONS.md) - PostgreSQL migration guide
