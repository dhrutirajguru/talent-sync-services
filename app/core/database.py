"""
Database engine + session management.

Every model in app/models/ inherits from Base, and every route/service gets
its DB session via the get_db() dependency — never by importing SessionLocal
directly, so tests can override the dependency cleanly later.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # avoids stale-connection errors after idle periods
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def get_db() -> Generator:
    """
    FastAPI dependency that yields a DB session and guarantees it's closed
    after the request, even if an exception is raised.

    Usage in a route:
        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
