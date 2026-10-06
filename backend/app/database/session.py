"""
Database session/engine setup.

Works out of the box with SQLite for local dev (DATABASE_URL default),
and is Postgres/Supabase-ready: just point DATABASE_URL at a Postgres
connection string, e.g.:

    postgresql+psycopg://user:password@host:5432/dbname

For an MVP hackathon build we use SQLAlchemy's `create_all` on startup
instead of a migrations framework (Alembic) — see the "Known limitations"
section of the README for the tradeoff. Swapping in Alembic later does
not require changing any model or route code.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a request-scoped DB session, always closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables that don't exist yet. Safe to call repeatedly."""
    # Import models here (not at module top) so they register on Base's
    # metadata before create_all runs, without creating a circular import.
    from app.models import profile, saved_roadmap, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
