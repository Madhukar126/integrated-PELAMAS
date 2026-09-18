"""phase 1 schema

Revision ID: 20260918_phase1
Revises: 
Create Date: 2026-09-18 00:00:00.000000

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260918_phase1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "transports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="ON_SCHEDULE"),
        sa.Column("origin_station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("destination_station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("planned_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eta_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delay_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "cargo_shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("transport_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transports.id"), nullable=False),
        sa.Column("origin_station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("destination_station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("item_code", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("volume_m3", sa.Float(), nullable=False, server_default="0"),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="HIGH"),
        sa.Column("criticality", sa.String(length=32), nullable=False, server_default="CRITICAL"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="IN_TRANSIT"),
        sa.Column("planned_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eta_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("current_quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("minimum_stock", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reorder_threshold", sa.Float(), nullable=False, server_default="0"),
        sa.Column("daily_usage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=32), nullable=False, server_default="unit"),
        sa.Column("last_updated", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("asset_type", sa.String(length=64), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="OPERATING"),
        sa.Column("condition_score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("operating_hours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("maintenance_due_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("last_maintenance", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_maintenance", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "missions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="ACTIVE"),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="HIGH"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "risk_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("risk_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("affected_entities", sa.JSON(), nullable=False),
        sa.Column("dependency_chain", sa.JSON(), nullable=False),
        sa.Column("contributing_factors", sa.JSON(), nullable=False),
        sa.Column("transport_code", sa.String(length=64), nullable=True),
        sa.Column("cargo_code", sa.String(length=64), nullable=True),
        sa.Column("inventory_code", sa.String(length=64), nullable=True),
        sa.Column("asset_code", sa.String(length=64), nullable=True),
        sa.Column("mission_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id"), nullable=False),
        sa.Column("user_name", sa.String(length=128), nullable=False, server_default="expedition_manager"),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.utcnow),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("recommendations")
    op.drop_table("risk_events")
    op.drop_table("missions")
    op.drop_table("assets")
    op.drop_table("inventory_items")
    op.drop_table("cargo_shipments")
    op.drop_table("transports")
    op.drop_table("stations")
