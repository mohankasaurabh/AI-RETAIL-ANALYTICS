from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from backend.database.db import Base


class AnalyticsLog(Base):

    __tablename__ = "analytics_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    occupancy = Column(Integer)

    entries = Column(Integer)

    exits = Column(Integer)

    active_customers = Column(Integer)

    zone_occupancy = Column(Integer)

    total_tracks = Column(Integer)

    reid_identities = Column(Integer)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )


class MovementLog(Base):

    __tablename__ = "movement_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    track_id = Column(Integer)

    x = Column(Float)

    y = Column(Float)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )