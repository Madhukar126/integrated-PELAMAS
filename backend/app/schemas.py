from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class StationRead(BaseModel):
    id: str
    code: str
    name: str
    region: str
    created_at: datetime | None = None


class TransportRead(BaseModel):
    id: str
    code: str
    status: str
    eta_days: int
    delay_days: int
    planned_departure: datetime | None = None
    actual_departure: datetime | None = None
    planned_arrival: datetime | None = None
    estimated_arrival: datetime | None = None
    actual_arrival: datetime | None = None


class CargoRead(BaseModel):
    id: str
    code: str
    item_code: str
    item_name: str
    status: str
    criticality: str
    weight_kg: float
    volume_m3: float
    eta_days: int
    planned_arrival: datetime | None = None
    estimated_arrival: datetime | None = None
    actual_arrival: datetime | None = None
    priority: str | None = None
    origin: str | None = None
    destination: str | None = None


class InventoryRead(BaseModel):
    id: str
    code: str
    item_name: str
    category: str
    current_quantity: float
    reserved_quantity: float
    minimum_stock: float
    reorder_threshold: float
    daily_usage: float
    unit: str
    station_name: str | None = None
    available_quantity: float | None = None


class AssetRead(BaseModel):
    id: str
    code: str
    name: str | None = None
    asset_type: str
    status: str
    condition_score: int
    operating_hours: int
    maintenance_due_days: int
    station_name: str | None = None


class MissionRead(BaseModel):
    id: str
    code: str
    name: str
    status: str
    priority: str
    station_name: str | None = None


class RecommendationRead(BaseModel):
    id: str
    title: str
    action: str
    rationale: str
    status: str
    created_at: datetime | None = None


class RiskFactor(BaseModel):
    name: str
    contribution: int
    reason: str


class RiskEventRead(BaseModel):
    id: str
    event_type: str
    risk_type: str
    severity: str
    score: int
    title: str
    description: str
    explanation: str
    affected_entities: list[str]
    dependency_chain: list[str]
    contributing_factors: list[RiskFactor]
    transport_code: str | None = None
    cargo_code: str | None = None
    inventory_code: str | None = None
    asset_code: str | None = None
    mission_code: str | None = None
    created_at: datetime | None = None


class AuditDecision(BaseModel):
    decision: Literal["APPROVE", "MODIFY", "REJECT"]
    comment: str = Field(default="")
    user_name: str = Field(default="expedition_manager")


class ExpeditionCreate(BaseModel):
    code: str
    name: str
    status: str = "ACTIVE"
    description: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    station_ids: list[str] = Field(default_factory=list)


class ExpeditionRead(BaseModel):
    id: str
    code: str
    name: str
    status: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime | None = None
    station_codes: list[str] = Field(default_factory=list)


class InventoryTransactionCreate(BaseModel):
    inventory_item_id: str
    station_id: str
    transaction_type: Literal["IN", "OUT", "CONSUMPTION", "TRANSFER", "DAMAGE", "EXPIRED", "ADJUSTMENT"]
    quantity: float
    reference: str | None = None
    notes: str | None = None


class PersonnelCreate(BaseModel):
    name: str
    role: str
    specialization: str
    station_id: str
    expedition_id: str | None = None
    arrival_date: datetime | None = None
    departure_date: datetime | None = None
    movement_status: str = "ASSIGNED"


class PersonnelRead(BaseModel):
    id: str
    name: str
    role: str
    specialization: str
    station_name: str | None = None
    expedition_name: str | None = None
    movement_status: str = "ASSIGNED"


class DashboardState(BaseModel):
    transport: TransportRead | None
    cargo: CargoRead | None
    inventory: InventoryRead | None
    asset: AssetRead | None
    mission: MissionRead | None
    risk_event: RiskEventRead | None
    recommendations: list[RecommendationRead]
    normal_state: bool


class Phase2Dashboard(BaseModel):
    active_expedition: str
    personnel_deployed: int
    cargo_in_transit: int
    delayed_cargo: int
    critical_inventory: int
    assets_requiring_attention: int
    active_missions: int
    open_risks: int
    polaris_alerts: int
    stations: list[str] = Field(default_factory=list)


class SimulateDelayResponse(BaseModel):
    ok: bool
    message: str
    transport: TransportRead | None = None
    cargo: CargoRead | None = None
    inventory: InventoryRead | None = None
    asset: AssetRead | None = None
    mission: MissionRead | None = None
    risk_event: RiskEventRead | None = None
    recommendations: list[RecommendationRead] = Field(default_factory=list)
