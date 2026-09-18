import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Expedition(Base):
    __tablename__ = "expeditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(64), nullable=False, default="PLANNED")
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    stations = relationship("ExpeditionStation", back_populates="expedition", cascade="all, delete-orphan")
    transports = relationship("Transport", back_populates="expedition", cascade="all, delete-orphan")
    cargo_shipments = relationship("CargoShipment", back_populates="expedition", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="expedition", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="expedition", cascade="all, delete-orphan")
    personnel = relationship("Personnel", back_populates="expedition", cascade="all, delete-orphan")


class ExpeditionStation(Base):
    __tablename__ = "expedition_stations"

    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), primary_key=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), primary_key=True)

    expedition = relationship("Expedition", back_populates="stations")
    station = relationship("Station", back_populates="expeditions")


class Station(Base):
    __tablename__ = "stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    inventory_items = relationship("InventoryItem", back_populates="station")
    assets = relationship("Asset", back_populates="station")
    missions = relationship("Mission", back_populates="station")
    personnel = relationship("Personnel", back_populates="station")
    expeditions = relationship("ExpeditionStation", back_populates="station")
    inventory_transactions = relationship("InventoryTransaction", back_populates="station")


class Transport(Base):
    __tablename__ = "transports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    status = Column(String(64), nullable=False, default="ON_SCHEDULE")
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    origin_station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    planned_departure = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    planned_arrival = Column(DateTime(timezone=True), nullable=True)
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    eta_days = Column(Integer, nullable=False, default=0)
    delay_days = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition", back_populates="transports")
    origin_station = relationship("Station", foreign_keys=[origin_station_id], overlaps="destination_station")
    destination_station = relationship("Station", foreign_keys=[destination_station_id], overlaps="origin_station")
    cargo_shipments = relationship("CargoShipment", back_populates="transport")


class CargoShipment(Base):
    __tablename__ = "cargo_shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    transport_id = Column(UUID(as_uuid=True), ForeignKey("transports.id"), nullable=False)
    origin_station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    item_code = Column(String(64), nullable=False)
    item_name = Column(String(255), nullable=False)
    weight_kg = Column(Float, nullable=False, default=0.0)
    volume_m3 = Column(Float, nullable=False, default=0.0)
    priority = Column(String(32), nullable=False, default="HIGH")
    criticality = Column(String(32), nullable=False, default="CRITICAL")
    status = Column(String(64), nullable=False, default="IN_TRANSIT")
    required_by_date = Column(DateTime(timezone=True), nullable=True)
    planned_departure = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    planned_arrival = Column(DateTime(timezone=True), nullable=True)
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    eta_days = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition", back_populates="cargo_shipments")
    transport = relationship("Transport", back_populates="cargo_shipments")
    origin_station = relationship("Station", foreign_keys=[origin_station_id], overlaps="destination_station")
    destination_station = relationship("Station", foreign_keys=[destination_station_id], overlaps="origin_station")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    item_name = Column(String(255), nullable=False)
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    category = Column(String(64), nullable=False)
    current_quantity = Column(Float, nullable=False, default=0.0)
    reserved_quantity = Column(Float, nullable=False, default=0.0)
    minimum_stock = Column(Float, nullable=False, default=0.0)
    reorder_threshold = Column(Float, nullable=False, default=0.0)
    daily_usage = Column(Float, nullable=False, default=0.0)
    unit = Column(String(32), nullable=False, default="unit")
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition")
    station = relationship("Station", back_populates="inventory_items")
    transactions = relationship("InventoryTransaction", back_populates="inventory_item")

    @property
    def available_quantity(self) -> float:
        return max(0.0, self.current_quantity - self.reserved_quantity)


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    transaction_type = Column(String(32), nullable=False)
    quantity = Column(Float, nullable=False)
    reference = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    inventory_item = relationship("InventoryItem", back_populates="transactions")
    station = relationship("Station", back_populates="inventory_transactions")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    asset_type = Column(String(64), nullable=False)
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    status = Column(String(64), nullable=False, default="OPERATING")
    condition_score = Column(Integer, nullable=False, default=100)
    operating_hours = Column(Integer, nullable=False, default=0)
    maintenance_due_days = Column(Integer, nullable=False, default=30)
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    next_maintenance = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition", back_populates="assets")
    station = relationship("Station", back_populates="assets")
    maintenance_history = relationship("AssetMaintenance", back_populates="asset", cascade="all, delete-orphan")


class AssetMaintenance(Base):
    __tablename__ = "asset_maintenance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    maintenance_type = Column(String(64), nullable=False, default="ROUTINE")
    status = Column(String(64), nullable=False, default="COMPLETED")
    performed_at = Column(DateTime(timezone=True), nullable=True)
    next_due_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    asset = relationship("Asset", back_populates="maintenance_history")


class Mission(Base):
    __tablename__ = "missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    status = Column(String(64), nullable=False, default="ACTIVE")
    priority = Column(String(32), nullable=False, default="HIGH")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition", back_populates="missions")
    station = relationship("Station", back_populates="missions")
    requirements = relationship("MissionDependency", back_populates="mission", cascade="all, delete-orphan")


class MissionDependency(Base):
    __tablename__ = "mission_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    required_type = Column(String(32), nullable=False)
    required_entity_id = Column(UUID(as_uuid=True), nullable=False)
    required_code = Column(String(64), nullable=False)
    required_name = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    mission = relationship("Mission", back_populates="requirements")


class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(128), nullable=False)
    specialization = Column(String(128), nullable=False)
    expedition_id = Column(UUID(as_uuid=True), ForeignKey("expeditions.id"), nullable=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    arrival_date = Column(DateTime(timezone=True), nullable=True)
    departure_date = Column(DateTime(timezone=True), nullable=True)
    movement_status = Column(String(64), nullable=False, default="ASSIGNED")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    expedition = relationship("Expedition", back_populates="personnel")
    station = relationship("Station", back_populates="personnel")
    movement_history = relationship("PersonnelMovement", back_populates="personnel", cascade="all, delete-orphan")


class PersonnelMovement(Base):
    __tablename__ = "personnel_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personnel_id = Column(UUID(as_uuid=True), ForeignKey("personnel.id"), nullable=False)
    from_location = Column(String(128), nullable=True)
    to_location = Column(String(128), nullable=False)
    movement_type = Column(String(32), nullable=False, default="TRANSFER")
    movement_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    personnel = relationship("Personnel", back_populates="movement_history")


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(64), nullable=False)
    risk_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    score = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    affected_entities = Column(JSON, nullable=False, default=list)
    dependency_chain = Column(JSON, nullable=False, default=list)
    contributing_factors = Column(JSON, nullable=False, default=list)
    transport_code = Column(String(64), nullable=True)
    cargo_code = Column(String(64), nullable=True)
    inventory_code = Column(String(64), nullable=True)
    asset_code = Column(String(64), nullable=True)
    mission_code = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    recommendations = relationship("Recommendation", back_populates="risk_event")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_event_id = Column(UUID(as_uuid=True), ForeignKey("risk_events.id"), nullable=False)
    title = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="OPEN")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    risk_event = relationship("RiskEvent", back_populates="recommendations")
    audit_logs = relationship("AuditLog", back_populates="recommendation")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=False)
    user_name = Column(String(128), nullable=False, default="expedition_manager")
    decision = Column(String(32), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="audit_logs")
