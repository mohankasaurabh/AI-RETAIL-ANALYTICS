"""
=====================================================
Database engine & session management
=====================================================

Supports SQLite (default), PostgreSQL and MySQL via the
DATABASE_URL environment variable. Provides:

- engine / Base               : SQLAlchemy core
- SessionLocal                : legacy factory (kept for back-compat)
- ScopedSession               : thread-safe scoped session (multi-camera workers)
- session_scope()             : context manager that commits/rolls back/closes

The platform runs concurrent per-camera worker threads, so new
code MUST use ScopedSession / session_scope() instead of sharing a
single Session across threads.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager


# =====================================
# CONNECTION URL
# =====================================
# e.g.
#   sqlite:///retail_analytics.db          (default)
#   postgresql+psycopg2://user:pw@host/db
#   mysql+pymysql://user:pw@host/db

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///retail_analytics.db"
)

# SQLite needs check_same_thread=False to be shared across threads
_connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=_connect_args,
)

# =====================================
# SESSION FACTORIES
# =====================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# thread-safe scoped session for concurrent workers
ScopedSession = scoped_session(SessionLocal)

Base = declarative_base()


# =====================================
# SESSION CONTEXT MANAGER
# =====================================

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        ScopedSession.remove()
