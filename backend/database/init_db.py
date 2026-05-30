"""
Database initialization — create all tables then seed defaults.
Importing backend.database.models registers every model on Base.
"""

from backend.database.db import engine, Base

# import side-effect: registers all model classes on Base.metadata
import backend.database.models  # noqa: F401

from backend.database.seed import seed_defaults


def init_database():

    Base.metadata.create_all(bind=engine)
    print("[INFO] Database Initialized")

    seed_defaults()


if __name__ == "__main__":
    init_database()
