from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes import router
from app.config import settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401
from app.db.database import SessionLocal
from app.services.seed_demo import seed_demo_data_if_needed

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="POLARIS expedition intelligence platform for polar logistics, forecasting, shortage prediction, and mission-risk decision support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowlist,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


def ensure_phase2_schema() -> None:
    inspector = inspect(engine)
    required_columns = {
        "transports": ["expedition_id"],
        "cargo_shipments": ["expedition_id", "required_by_date"],
        "inventory_items": ["expedition_id"],
        "assets": ["name", "expedition_id"],
        "missions": ["expedition_id", "description", "start_date", "end_date"],
    }

    with engine.begin() as conn:
        for table_name, columns in required_columns.items():
            if not inspector.has_table(table_name):
                continue
            current_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name in columns:
                if column_name in current_columns:
                    continue
                column_type = "UUID"
                if column_name in {"required_by_date", "start_date", "end_date", "last_maintenance", "next_maintenance", "last_updated", "created_at"}:
                    column_type = "TIMESTAMPTZ"
                elif column_name == "description":
                    column_type = "TEXT"
                elif column_name == "name":
                    column_type = "VARCHAR(255)"
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_phase2_schema()
    db = SessionLocal()
    try:
        seed_demo_data_if_needed(db)
    finally:
        db.close()
