from backend.database.db import (
    engine
)

from backend.database.models import Base


def init_database():

    Base.metadata.create_all(
        bind=engine
    )

    print("[INFO] Database Initialized")


if __name__ == "__main__":

    init_database()