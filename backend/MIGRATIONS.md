# Database Migrations Guide

## Current State: SQLite with SQLModel

FlashCase currently uses SQLite as the database with SQLModel as the ORM. SQLModel provides automatic table creation based on model definitions, which is suitable for development and MVP phases.

### Current Database Configuration

- **Database**: SQLite (`flashcase.db`)
- **ORM**: SQLModel (built on SQLAlchemy and Pydantic)
- **Connection**: Configured with `check_same_thread=False` for FastAPI threading compatibility
- **Schema Management**: Automatic via `SQLModel.metadata.create_all()`

### Current Models

1. **User** - User authentication and management
   - id, email, username, hashed_password, is_active, created_at, updated_at

2. **Deck** - Flashcard deck organization
   - id, name, description, is_public, created_at, updated_at

3. **Card** - Individual flashcards
   - id, deck_id (FK), front, back, created_at, updated_at

4. **DeckMetadata** - Deck statistics and usage tracking
   - id, deck_id (FK), card_count, total_reviews, average_rating, last_studied, created_at, updated_at

5. **StudyLog** - Study session and spaced repetition tracking
   - id, user_id (FK), card_id (FK), reviewed_at, ease_factor, interval, next_review, created_at

6. **UserDeck** - Many-to-many relationship between users and decks
   - id, user_id (FK), deck_id (FK), is_owner, is_favorite, added_at

### Database Session Management

The application provides database sessions through dependency injection:

```python
from app.core.database import get_db, get_session

# Use in route handlers
@app.get("/endpoint")
async def endpoint(session: Session = Depends(get_db)):
    # Use session here
    pass
```

Both `get_db` and `get_session` are available for consistency with different naming conventions.

## Migration Path to PostgreSQL

### Why Migrate to PostgreSQL?

PostgreSQL offers several advantages for production:

1. **Concurrency**: Better multi-user support with MVCC (Multi-Version Concurrency Control)
2. **Performance**: Superior performance with large datasets and complex queries
3. **Features**: Advanced features like JSON support, full-text search, and array types
4. **Scalability**: Horizontal scaling with read replicas and partitioning
5. **Data Integrity**: Robust constraint enforcement and ACID compliance
6. **Extensions**: Rich ecosystem (PostGIS, pg_trgm, etc.)

### Migration Timeline

#### Phase 1: Preparation (Before Migration)
- [ ] Install Alembic for schema migration management
- [ ] Generate initial migration from current SQLModel models
- [ ] Test migrations in staging environment
- [ ] Backup all SQLite data
- [ ] Document current database size and schema

#### Phase 2: Setup PostgreSQL (Week 1)
- [ ] Provision PostgreSQL instance (AWS RDS, Google Cloud SQL, or DigitalOcean)
- [ ] Configure connection pooling (e.g., PgBouncer)
- [ ] Update connection string in environment variables
- [ ] Test connectivity and performance

#### Phase 3: Schema Migration (Week 2)
- [ ] Run Alembic migrations against PostgreSQL
- [ ] Verify all tables, indexes, and constraints created correctly
- [ ] Test application against new database with sample data
- [ ] Performance testing and query optimization

#### Phase 4: Data Migration (Week 3)
- [ ] Export data from SQLite using custom scripts
- [ ] Transform data if needed (e.g., datetime formats)
- [ ] Import data into PostgreSQL
- [ ] Verify data integrity with checksums
- [ ] Test critical user flows with migrated data

#### Phase 5: Cutover (Week 4)
- [ ] Schedule maintenance window
- [ ] Final data sync from SQLite to PostgreSQL
- [ ] Update production configuration
- [ ] Deploy application with PostgreSQL connection
- [ ] Monitor for errors and performance issues
- [ ] Keep SQLite backup for 30 days

### Setting Up Alembic

Install Alembic for database migrations:

```bash
pip install alembic
```

Initialize Alembic:

```bash
cd backend
alembic init alembic
```

Configure `alembic.ini`:

```ini
# For SQLite (current)
sqlalchemy.url = sqlite:///./flashcase.db

# For PostgreSQL (future)
# sqlalchemy.url = postgresql://user:password@localhost/flashcase
```

Configure `alembic/env.py` to use SQLModel metadata:

```python
from app.models import *  # Import all models
from app.core.database import engine

target_metadata = SQLModel.metadata

# ... rest of env.py configuration
```

Generate initial migration:

```bash
alembic revision --autogenerate -m "Initial schema"
```

Apply migrations:

```bash
alembic upgrade head
```

### PostgreSQL Configuration Example

Update `.env` for PostgreSQL:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://username:password@host:5432/flashcase
# Or using async driver
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/flashcase

# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

Update `database.py`:

```python
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

# PostgreSQL-compatible engine configuration
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    echo=settings.debug  # Log SQL in development only
)
```

### Data Migration Script Example

```python
# scripts/migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
from sqlmodel import Session, select
from app.core.database import engine
from app.models import User, Deck, Card, DeckMetadata, StudyLog, UserDeck

def migrate_data():
    # Connect to both databases
    sqlite_conn = sqlite3.connect('flashcase.db')
    
    with Session(engine) as pg_session:
        # Migrate Users
        users = sqlite_conn.execute('SELECT * FROM user').fetchall()
        for user_data in users:
            user = User(**dict(zip([col[0] for col in sqlite_conn.description], user_data)))
            pg_session.add(user)
        
        # Migrate other tables similarly...
        pg_session.commit()

if __name__ == '__main__':
    migrate_data()
```

### Testing After Migration

1. **Data Integrity Tests**:
   ```bash
   pytest tests/test_migration.py -v
   ```

2. **Performance Comparison**:
   - Compare query response times
   - Check connection pool usage
   - Monitor database CPU/memory

3. **Application Tests**:
   ```bash
   pytest tests/ -v
   ```

### Rollback Plan

If issues arise during migration:

1. Immediately switch `DATABASE_URL` back to SQLite
2. Restart application
3. Investigate issues in staging environment
4. Document problems and solutions
5. Schedule new migration window

### PostgreSQL-Specific Optimizations

After migration, consider:

1. **Indexes**: Add indexes for common queries
   ```sql
   CREATE INDEX idx_study_log_user_next_review ON study_log(user_id, next_review);
   CREATE INDEX idx_card_deck_created ON card(deck_id, created_at DESC);
   ```

2. **Constraints**: Add unique constraints
   ```sql
   ALTER TABLE user_deck ADD CONSTRAINT unique_user_deck UNIQUE (user_id, deck_id);
   ```

3. **Partitioning**: For large tables like `study_log`
   ```sql
   -- Partition by review date
   CREATE TABLE study_log_2024 PARTITION OF study_log
       FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
   ```

4. **Full-Text Search**: For deck/card search
   ```sql
   CREATE INDEX idx_deck_name_fts ON deck USING gin(to_tsvector('english', name));
   ```

### Monitoring and Maintenance

Post-migration monitoring:

1. **Query Performance**:
   - Enable slow query logging
   - Use `EXPLAIN ANALYZE` for optimization
   - Monitor with pgBadger or similar tools

2. **Database Health**:
   - Regular VACUUM and ANALYZE
   - Monitor connection pool utilization
   - Track database size growth

3. **Backup Strategy**:
   - Daily automated backups
   - Point-in-time recovery (PITR) enabled
   - Test restore procedures monthly

## Resources

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)

## Support

For questions or issues with database migrations:
- Create an issue in the GitHub repository
- Contact the development team
- Review existing migration examples in `alembic/versions/`
