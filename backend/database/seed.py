"""
=====================================================
Database seeding (idempotent)
=====================================================

Seeds:
- a default Store (id=1)
- the three legacy sources (mall / webcam / rtsp) as Camera rows
- default zones for the mall camera (migrating the old hardcoded
  rectangles into the DB so Zone Analytics has data to start from)

Safe to call on every startup — only inserts what is missing.
"""

from backend.database.db import session_scope
from backend.database.models import Store, Camera, Zone


# legacy hardcoded sources (from ai_engine/stream/camera_manager.py)
DEFAULT_CAMERAS = [
    {
        "name": "Mall Video",
        "source_type": "video",
        "uri": "data/videos/mall.mp4",
        "location": "Main Hall",
        "fps_target": 10,
    },
    {
        "name": "Local Webcam",
        "source_type": "webcam",
        "uri": "0",
        "location": "Test Bench",
        "fps_target": 12,
    },
    {
        "name": "RTSP Camera",
        "source_type": "rtsp",
        "uri": "",
        "location": "—",
        "fps_target": 8,
    },
]

# legacy hardcoded rectangles (from ai_engine/analytics/zone_analytics.py)
DEFAULT_ZONES = [
    {"name": "Zone A", "kind": "entrance",
     "points": [[0, 0], [400, 0], [400, 350], [0, 350]]},
    {"name": "Zone B", "kind": "generic",
     "points": [[400, 0], [800, 0], [800, 350], [400, 350]]},
    {"name": "Zone C", "kind": "generic",
     "points": [[800, 0], [1280, 0], [1280, 350], [800, 350]]},
    {"name": "Zone D", "kind": "checkout",
     "points": [[0, 350], [1280, 350], [1280, 720], [0, 720]]},
]


def seed_defaults():
    with session_scope() as db:

        # ---- default store ----
        store = db.query(Store).filter_by(id=1).first()
        if not store:
            store = Store(id=1, name="Default Store", location="Demo Mall")
            db.add(store)
            db.flush()
            print("[SEED] Created default store")

        # ---- cameras ----
        existing = {c.name for c in db.query(Camera).all()}
        created_cams = {}
        for spec in DEFAULT_CAMERAS:
            if spec["name"] not in existing:
                cam = Camera(store_id=1, status="stopped", **spec)
                db.add(cam)
                db.flush()
                created_cams[spec["name"]] = cam.id
                print(f"[SEED] Created camera: {spec['name']} (id={cam.id})")

        # ---- default zones for the mall camera ----
        mall = db.query(Camera).filter_by(name="Mall Video").first()
        if mall:
            has_zones = db.query(Zone).filter_by(camera_id=mall.id).count()
            if not has_zones:
                for z in DEFAULT_ZONES:
                    db.add(Zone(
                        camera_id=mall.id,
                        name=z["name"],
                        shape="polygon",
                        points=z["points"],
                        kind=z["kind"],
                    ))
                print(f"[SEED] Created {len(DEFAULT_ZONES)} default zones for Mall Video")


if __name__ == "__main__":
    seed_defaults()
    print("[SEED] Done")
