from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Create the engine
engine_options = {}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_options)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def migrate_database():
    """Add fields introduced after the first version of the SQLite database."""
    if engine.url.get_backend_name() != "sqlite":
        return
    with engine.begin() as connection:
        columns = {row[1] for row in connection.execute(text("PRAGMA table_info(tasks)"))}
        migrations = {
            "category": "ALTER TABLE tasks ADD COLUMN category VARCHAR(50) DEFAULT 'General'",
            "priority": "ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'",
            "due_date": "ALTER TABLE tasks ADD COLUMN due_date DATETIME",
            "created_at": "ALTER TABLE tasks ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
        }
        for name, statement in migrations.items():
            if name not in columns:
                try:
                    connection.execute(text(statement))
                except Exception:
                    pass  # Column might already exist

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
