"""
=====================================================
Settings Service
=====================================================

Global platform settings persisted in the Setting table.
Provides defaults, merged reads, save, and runtime application
of the ReID similarity threshold / identity timeout to the
shared global registry.
"""

from backend.database import repository
from ai_engine.reid.global_identity import global_registry


DEFAULTS = {
    # default AI models for new cameras
    "default_models": {
        "detection": True, "tracking": True, "reid": True,
        "demographics": True, "heatmap": True, "zones": True,
    },
    # ReID
    "reid_threshold": 0.65,
    "reid_timeout": 300,
    # camera defaults
    "snapshot_frequency": 2,      # seconds
    "retention_days": 30,
    # database (informational — actual switch via DATABASE_URL + restart)
    "db_backend": "sqlite",
    # alerts
    "alerts_enabled": True,
    "alert_occupancy": 20,
    "alert_queue_length": 8,
}


def get_all():
    stored = {s["key"]: s["value"]
              for s in repository.all_settings() if s["scope"] == "global"}
    return {**DEFAULTS, **stored}


def get(key, default=None):
    return get_all().get(key, default if default is not None else DEFAULTS.get(key))


def save(data):
    for k, v in data.items():
        if k in DEFAULTS:
            repository.set_setting(k, v)
    apply_runtime()
    return get_all()


def apply_runtime():
    """Push live-tunable settings into the running engine."""
    cfg = get_all()
    try:
        global_registry.threshold = float(cfg["reid_threshold"])
        global_registry.timeout = int(cfg["reid_timeout"])
    except Exception as exc:
        print(f"[SETTINGS apply error] {exc}")
