from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import (
    Asset,
    AssetMaintenance,
    AuditLog,
    CargoShipment,
    Expedition,
    ExpeditionStation,
    InventoryItem,
    InventoryTransaction,
    Mission,
    MissionDependency,
    Personnel,
    Recommendation,
    RiskEvent,
    Station,
    Transport,
)
from app.schemas import (
    AssetRead,
    AuditDecision,
    CargoRead,
    DashboardState,
    ExpeditionCreate,
    ExpeditionRead,
    InventoryRead,
    InventoryTransactionCreate,
    PersonnelCreate,
    PersonnelRead,
    Phase2Dashboard,
    SimulateDelayResponse,
)
from app.services.polaris_engine import create_risk_event_and_recommendations
from app.services.seed_demo import seed_demo_data_if_needed

try:
    from backend.polaris.forecasting.demand_forecasting import DemandForecastingEngine
    from backend.polaris.inventory.shortage_predictor import ShortagePredictor
    from backend.polaris.optimization.cargo_optimizer import CargoOptimizer
    from backend.polaris.risk.dependency_analyzer import DependencyAnalyzer
    from backend.polaris.risk.risk_fusion import RiskFusionEngine
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.forecasting.demand_forecasting import DemandForecastingEngine
    from polaris.inventory.shortage_predictor import ShortagePredictor
    from polaris.optimization.cargo_optimizer import CargoOptimizer
    from polaris.risk.dependency_analyzer import DependencyAnalyzer
    from polaris.risk.risk_fusion import RiskFusionEngine

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "POLARIS Phase 2"}


@router.get("/polaris/inventory/forecast/{station_code}/{item_code}")
def get_inventory_forecast(station_code: str, item_code: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    seed_demo_data_if_needed(db)
    station = db.query(Station).filter(Station.code == station_code.upper()).first()
    item = db.query(InventoryItem).filter(InventoryItem.code == item_code.upper()).first()
    if station is None or item is None:
        raise HTTPException(status_code=404, detail="Inventory forecast target not found.")

    history = [
        max(0.0, float(item.current_quantity + offset))
        for offset in [15, 12, 9, 7, 4, 2, 0, -2]
    ]
    forecast = DemandForecastingEngine(history=history, horizon_days=30, station=station.code, item_code=item.code).forecast()
    return {
        "station": station.code,
        "item_code": item.code,
        "item_name": item.item_name,
        "forecast_horizon_days": forecast["forecast_horizon_days"],
        "predicted_consumption": forecast["predicted_consumption"],
        "model_used": forecast["model_used"],
        "evaluation_metric": forecast["evaluation_metric"],
        "metric_value": forecast["metric_value"],
        "confidence_score": forecast["confidence_score"],
        "explanation": forecast["explanation"],
    }


@router.get("/polaris/inventory/shortages")
def get_inventory_shortages(
    db: Session = Depends(get_db),
    station: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    horizon: int = Query(default=30),
) -> list[dict[str, Any]]:
    seed_demo_data_if_needed(db)
    query = db.query(InventoryItem)
    if station:
        query = query.join(Station).filter(Station.code == station.upper())

    rows = query.order_by(InventoryItem.current_quantity.asc()).all()
    results: list[dict[str, Any]] = []
    for item in rows:
        forecast = DemandForecastingEngine(
            history=[
                max(0.0, float(item.current_quantity + offset)) for offset in [18, 16, 14, 11, 9, 7, 5, 3]
            ],
            horizon_days=horizon,
            station=item.station.code if item.station else "UNKNOWN",
            item_code=item.code,
        ).forecast()
        shortage = ShortagePredictor(
            available_inventory=item.available_quantity,
            reserved_inventory=item.reserved_quantity,
            predicted_daily_consumption=forecast["predicted_consumption"],
            next_resupply_days=max(7.0, float(horizon) * 0.9),
            minimum_reserve=item.minimum_stock,
        ).evaluate()
        if severity and shortage["severity"] != severity.upper():
            continue
        results.append({
            "station": item.station.code if item.station else "UNKNOWN",
            "item_code": item.code,
            "item_name": item.item_name,
            "current_quantity": item.current_quantity,
            "minimum_stock": item.minimum_stock,
            "estimated_days_of_supply": shortage["estimated_days_of_supply"],
            "gap_days": shortage["gap_days"],
            "severity": shortage["severity"],
            "forecast": forecast,
            "explanation": shortage["explanation"],
        })
    return results


@router.get("/polaris/dependency/graph")
def get_dependency_graph() -> dict[str, Any]:
    analyzer = DependencyAnalyzer()
    return analyzer.analyze_transport_chain(
        transport_code="T04",
        cargo_code="C018",
        inventory_code="GF14",
        asset_code="G07",
        mission_code="M12",
    )


@router.get("/polaris/risk/fusion")
def get_risk_fusion() -> dict[str, Any]:
    fusion = RiskFusionEngine()
    return fusion.calculate(
        inventory_risk=72,
        transport_risk=82,
        asset_risk=60,
        mission_risk=55,
        environment_risk=40,
    )


@router.get("/polaris/assistant")
def polaris_assistant(q: str = Query(default="", alias="q", description="Operational question for the safe POLARIS explanation layer"), db: Session = Depends(get_db)) -> dict[str, Any]:
    normalized_question = (q or "").strip()
    if not normalized_question:
        raise HTTPException(status_code=400, detail="A question is required to use the POLARIS assistant.")

    seed_demo_data_if_needed(db)
    transport = db.query(Transport).filter(Transport.code == "T04").first()
    cargo = db.query(CargoShipment).filter(CargoShipment.code == "C018").first()
    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    asset = db.query(Asset).filter(Asset.code == "G07").first()
    mission = db.query(Mission).filter(Mission.code == "M12").first()
    risk_event = db.query(RiskEvent).order_by(RiskEvent.created_at.desc()).first()

    answer_parts = [
        "Based on the current database state, the primary operational risk is the T04 delay affecting the Bharati mission chain.",
        "Transport T04 is delayed, Cargo C018 is impacted, Inventory GF14 is near or below its reserve threshold, Generator G07 is elevated, and Mission M12 remains at risk.",
    ]
    if risk_event is not None:
        answer_parts.append(f"The latest risk event is {risk_event.title} with a severity of {risk_event.severity} and score {risk_event.score}.")
    if inventory is not None:
        answer_parts.append(f"Inventory GF14 currently stands at {inventory.current_quantity} units against a minimum stock of {inventory.minimum_stock}.")
    if asset is not None:
        answer_parts.append(f"Generator G07 remains in a degraded operating condition with condition score {asset.condition_score}.")
    answer = " ".join(answer_parts)

    return {
        "question": normalized_question,
        "answer": answer,
        "entities": [
            {"type": "transport", "code": "T04", "status": transport.status if transport else "UNKNOWN"},
            {"type": "cargo", "code": "C018", "status": cargo.status if cargo else "UNKNOWN"},
            {"type": "inventory", "code": "GF14", "status": inventory.status if inventory and hasattr(inventory, "status") else "CRITICAL"},
            {"type": "asset", "code": "G07", "status": asset.status if asset else "UNKNOWN"},
            {"type": "mission", "code": "M12", "status": mission.status if mission else "UNKNOWN"},
        ],
        "data_mode": "SYNTHETIC DEMONSTRATION DATA",
        "source": "POLARIS risk + inventory + asset + mission state",
    }


@router.get("/polaris/cargo/optimize")
def optimize_cargo(db: Session = Depends(get_db)) -> dict[str, Any]:
    seed_demo_data_if_needed(db)
    cargo_rows = db.query(CargoShipment).order_by(CargoShipment.created_at.asc()).all()
    cargo_payload = [
        {
            "id": str(row.id),
            "weight_kg": float(row.weight_kg),
            "volume_m3": float(row.volume_m3),
            "criticality": float(row.criticality_score) if hasattr(row, "criticality_score") else 1.0,
            "shortage_risk": 0.8 if row.status in {"DELAYED", "HIGH_RISK"} else 0.2,
            "mission_impact": 1.0 if row.criticality in {"CRITICAL", "URGENT"} else 0.5,
            "required_by_days": max(1, int(row.eta_days or 7)),
        }
        for row in cargo_rows
    ]
    optimizer = CargoOptimizer(weight_capacity=1200.0, volume_capacity=28.0, cargo=cargo_payload)
    return optimizer.optimize()


@router.get("/phase4/overview")
def get_phase4_overview(db: Session = Depends(get_db)) -> dict[str, Any]:
    seed_demo_data_if_needed(db)
    transport = db.query(Transport).filter(Transport.code == "T04").first()
    cargo = db.query(CargoShipment).filter(CargoShipment.code == "C018").first()
    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    asset = db.query(Asset).filter(Asset.code == "G07").first()
    mission = db.query(Mission).filter(Mission.code == "M12").first()
    risk_event = db.query(RiskEvent).order_by(RiskEvent.created_at.desc()).first()

    return {
        "expedition": "SIH26062",
        "status": "ACTIVE",
        "overall_risk": risk_event.severity if risk_event else "NORMAL",
        "risk_score": risk_event.score if risk_event else 0,
        "last_analysis": "2 minutes ago",
        "open_critical_alerts": 2 if risk_event else 0,
        "data_mode": "SYNTHETIC DEMO",
        "personnel_deployed": 30,
        "cargo_in_transit": 18,
        "delayed_cargo": transport.delay_days if transport else 0,
        "critical_inventory": inventory.current_quantity if inventory else 0,
        "active_asset_risks": 2 if asset else 0,
        "open_incidents": 3 if risk_event else 0,
        "transport": {
            "code": transport.code,
            "status": transport.status,
            "eta_days": transport.eta_days,
            "delay_days": transport.delay_days,
        } if transport else None,
        "cargo": {
            "code": cargo.code,
            "item_name": cargo.item_name,
            "criticality": cargo.criticality,
            "status": cargo.status,
        } if cargo else None,
        "inventory": {
            "code": inventory.code,
            "item_name": inventory.item_name,
            "available_quantity": inventory.available_quantity,
            "minimum_stock": inventory.minimum_stock,
        } if inventory else None,
        "asset": {
            "code": asset.code,
            "condition_score": asset.condition_score,
            "status": asset.status,
        } if asset else None,
        "mission": {
            "code": mission.code,
            "name": mission.name,
            "status": mission.status,
        } if mission else None,
    }


@router.get("/phase4/map")
def get_phase4_map() -> dict[str, Any]:
    return {
        "stations": [
            {"id": "GOA", "name": "NCPOR Goa", "x": 12, "y": 28, "status": "ACTIVE", "type": "STATION"},
            {"id": "CAPE_TOWN", "name": "Cape Town Logistics Hub", "x": 32, "y": 28, "status": "ACTIVE", "type": "STATION"},
            {"id": "MAITRI", "name": "Maitri", "x": 68, "y": 58, "status": "ACTIVE", "type": "STATION"},
            {"id": "BHARATI", "name": "Bharati", "x": 82, "y": 46, "status": "HIGH_RISK", "type": "STATION"},
        ],
        "routes": [
            {"from": "GOA", "to": "CAPE_TOWN", "type": "LOGISTICS", "status": "ACTIVE"},
            {"from": "CAPE_TOWN", "to": "BHARATI", "type": "TRANSPORT", "status": "DELAYED"},
            {"from": "CAPE_TOWN", "to": "MAITRI", "type": "TRANSPORT", "status": "ACTIVE"},
            {"from": "MAITRI", "to": "BHARATI", "type": "LOGISTICS", "status": "ACTIVE"},
        ],
        "markers": [
            {"id": "T04", "name": "Transport T04", "type": "SHIP", "x": 56, "y": 35, "status": "DELAYED"},
            {"id": "C018", "name": "Cargo C018", "type": "CARGO", "x": 72, "y": 40, "status": "AFFECTED"},
            {"id": "G07", "name": "Generator G07", "type": "ASSET", "x": 84, "y": 53, "status": "ELEVATED"},
            {"id": "M12", "name": "Mission M12", "type": "MISSION", "x": 86, "y": 36, "status": "AT_RISK"},
        ],
        "layers": ["Stations", "Transport", "Cargo", "Personnel", "Risks", "Incidents"],
    }


@router.get("/phase4/notifications")
def get_phase4_notifications() -> list[dict[str, Any]]:
    return [
        {
            "id": "n-001",
            "category": "CRITICAL",
            "title": "GF14 shortage risk detected at Bharati",
            "message": "Current reserve margin remains below the mission threshold.",
            "severity": "CRITICAL",
            "target_type": "inventory",
            "target_id": "GF14",
            "acknowledged": False,
        },
        {
            "id": "n-002",
            "category": "WARNING",
            "title": "Transport T04 delayed by 8 days",
            "message": "ETA has shifted and cargo criticality has increased.",
            "severity": "HIGH",
            "target_type": "transport",
            "target_id": "T04",
            "acknowledged": False,
        },
        {
            "id": "n-003",
            "category": "INFO",
            "title": "Cargo optimization plan generated",
            "message": "Mission-critical load selection has been computed for the next cycle.",
            "severity": "INFO",
            "target_type": "cargo",
            "target_id": "C018",
            "acknowledged": True,
        },
    ]


@router.get("/phase4/impact-path")
def get_phase4_impact_path() -> dict[str, Any]:
    graph = get_dependency_graph()
    return {
        "title": "Transport Delay Impact Path",
        "steps": [
            {"label": "Transport Delay", "value": "T04"},
            {"label": "Cargo Delay", "value": "C018"},
            {"label": "Inventory Reserve Breach", "value": "GF14"},
            {"label": "Asset Availability Risk", "value": "G07"},
            {"label": "Mission Impact", "value": "M12"},
        ],
        "graph": graph,
    }


@router.post("/phase4/demo/reset")
def reset_phase4_demo(db: Session = Depends(get_db)) -> dict[str, Any]:
    db.query(AuditLog).delete()
    db.query(Recommendation).delete()
    db.query(RiskEvent).delete()
    seed_demo_data_if_needed(db)
    db.commit()
    return {
        "status": "reset",
        "message": "Synthetic demo data restored to the deterministic Phase 1–4 baseline.",
        "data_mode": "SYNTHETIC DEMO",
    }


@router.get("/phase1/dashboard", response_model=DashboardState)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardState:
    seed_demo_data_if_needed(db)
    transport = db.query(Transport).filter(Transport.code == "T04").first()
    cargo = db.query(CargoShipment).filter(CargoShipment.code == "C018").first()
    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    asset = db.query(Asset).filter(Asset.code == "G07").first()
    mission = db.query(Mission).filter(Mission.code == "M12").first()
    risk_event = db.query(RiskEvent).order_by(RiskEvent.created_at.desc()).first()

    recommendations = []
    if risk_event is not None:
        recommendations = db.query(Recommendation).filter(Recommendation.risk_event_id == risk_event.id).order_by(Recommendation.created_at.asc()).all()

    return DashboardState(
        transport={
            "id": str(transport.id),
            "code": transport.code,
            "status": transport.status,
            "eta_days": transport.eta_days,
            "delay_days": transport.delay_days,
            "planned_departure": transport.planned_departure,
            "actual_departure": transport.actual_departure,
            "planned_arrival": transport.planned_arrival,
            "estimated_arrival": transport.estimated_arrival,
            "actual_arrival": transport.actual_arrival,
        } if transport else None,
        cargo={
            "id": str(cargo.id),
            "code": cargo.code,
            "item_code": cargo.item_code,
            "item_name": cargo.item_name,
            "status": cargo.status,
            "criticality": cargo.criticality,
            "weight_kg": cargo.weight_kg,
            "volume_m3": cargo.volume_m3,
            "eta_days": cargo.eta_days,
            "planned_arrival": cargo.planned_arrival,
            "estimated_arrival": cargo.estimated_arrival,
            "actual_arrival": cargo.actual_arrival,
        } if cargo else None,
        inventory={
            "id": str(inventory.id),
            "code": inventory.code,
            "item_name": inventory.item_name,
            "category": inventory.category,
            "current_quantity": inventory.current_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "minimum_stock": inventory.minimum_stock,
            "reorder_threshold": inventory.reorder_threshold,
            "daily_usage": inventory.daily_usage,
            "unit": inventory.unit,
            "station_name": inventory.station.name if inventory.station else None,
            "available_quantity": inventory.available_quantity,
        } if inventory else None,
        asset={
            "id": str(asset.id),
            "code": asset.code,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "condition_score": asset.condition_score,
            "operating_hours": asset.operating_hours,
            "maintenance_due_days": asset.maintenance_due_days,
            "station_name": asset.station.name if asset.station else None,
        } if asset else None,
        mission={
            "id": str(mission.id),
            "code": mission.code,
            "name": mission.name,
            "status": mission.status,
            "priority": mission.priority,
            "station_name": mission.station.name if mission.station else None,
        } if mission else None,
        risk_event={
            "id": str(risk_event.id),
            "event_type": risk_event.event_type,
            "risk_type": risk_event.risk_type,
            "severity": risk_event.severity,
            "score": risk_event.score,
            "title": risk_event.title,
            "description": risk_event.description,
            "explanation": risk_event.explanation,
            "affected_entities": risk_event.affected_entities,
            "dependency_chain": risk_event.dependency_chain,
            "contributing_factors": risk_event.contributing_factors,
            "transport_code": risk_event.transport_code,
            "cargo_code": risk_event.cargo_code,
            "inventory_code": risk_event.inventory_code,
            "asset_code": risk_event.asset_code,
            "mission_code": risk_event.mission_code,
            "created_at": risk_event.created_at,
        } if risk_event else None,
        recommendations=[
            {
                "id": str(item.id),
                "title": item.title,
                "action": item.action,
                "rationale": item.rationale,
                "status": item.status,
                "created_at": item.created_at,
            }
            for item in recommendations
        ],
        normal_state=risk_event is None,
    )


@router.post("/phase1/simulate-delay", response_model=SimulateDelayResponse)
def simulate_delay(db: Session = Depends(get_db)) -> SimulateDelayResponse:
    seed_demo_data_if_needed(db)

    transport = db.query(Transport).filter(Transport.code == "T04").first()
    cargo = db.query(CargoShipment).filter(CargoShipment.code == "C018").first()
    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    asset = db.query(Asset).filter(Asset.code == "G07").first()
    mission = db.query(Mission).filter(Mission.code == "M12").first()

    if not all([transport, cargo, inventory, asset, mission]):
        raise HTTPException(status_code=500, detail="Required Phase 1 entities are missing.")

    transport.status = "DELAYED"
    transport.delay_days = 8
    transport.eta_days = max(0, transport.eta_days + 8)
    if transport.estimated_arrival:
        transport.estimated_arrival = transport.estimated_arrival + timedelta(days=8)
    if transport.planned_arrival:
        transport.planned_arrival = transport.planned_arrival + timedelta(days=8)

    cargo.status = "DELAYED"
    cargo.eta_days = max(0, cargo.eta_days + 8)
    if cargo.estimated_arrival:
        cargo.estimated_arrival = cargo.estimated_arrival + timedelta(days=8)
    if cargo.planned_arrival:
        cargo.planned_arrival = cargo.planned_arrival + timedelta(days=8)

    db.commit()

    risk_output = create_risk_event_and_recommendations(db, "T04")
    risk_event = risk_output["risk_event"]
    recommendations = risk_output["recommendations"]

    risk_payload = {
        "id": str(risk_event.id),
        "event_type": risk_event.event_type,
        "risk_type": risk_event.risk_type,
        "severity": risk_event.severity,
        "score": risk_event.score,
        "title": risk_event.title,
        "description": risk_event.description,
        "explanation": risk_event.explanation,
        "affected_entities": risk_event.affected_entities,
        "dependency_chain": risk_event.dependency_chain,
        "contributing_factors": risk_event.contributing_factors,
        "transport_code": risk_event.transport_code,
        "cargo_code": risk_event.cargo_code,
        "inventory_code": risk_event.inventory_code,
        "asset_code": risk_event.asset_code,
        "mission_code": risk_event.mission_code,
        "created_at": risk_event.created_at,
    }

    rec_payload = [
        {
            "id": str(item.id),
            "title": item.title,
            "action": item.action,
            "rationale": item.rationale,
            "status": item.status,
            "created_at": item.created_at,
        }
        for item in recommendations
    ]

    return SimulateDelayResponse(
        ok=True,
        message="Risk detected and recommendations generated for the transport delay scenario.",
        transport={
            "id": str(transport.id),
            "code": transport.code,
            "status": transport.status,
            "eta_days": transport.eta_days,
            "delay_days": transport.delay_days,
            "planned_departure": transport.planned_departure,
            "actual_departure": transport.actual_departure,
            "planned_arrival": transport.planned_arrival,
            "estimated_arrival": transport.estimated_arrival,
            "actual_arrival": transport.actual_arrival,
        },
        cargo={
            "id": str(cargo.id),
            "code": cargo.code,
            "item_code": cargo.item_code,
            "item_name": cargo.item_name,
            "status": cargo.status,
            "criticality": cargo.criticality,
            "weight_kg": cargo.weight_kg,
            "volume_m3": cargo.volume_m3,
            "eta_days": cargo.eta_days,
            "planned_arrival": cargo.planned_arrival,
            "estimated_arrival": cargo.estimated_arrival,
            "actual_arrival": cargo.actual_arrival,
        },
        inventory={
            "id": str(inventory.id),
            "code": inventory.code,
            "item_name": inventory.item_name,
            "category": inventory.category,
            "current_quantity": inventory.current_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "minimum_stock": inventory.minimum_stock,
            "reorder_threshold": inventory.reorder_threshold,
            "daily_usage": inventory.daily_usage,
            "unit": inventory.unit,
            "station_name": inventory.station.name if inventory.station else None,
            "available_quantity": inventory.available_quantity,
        },
        asset={
            "id": str(asset.id),
            "code": asset.code,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "condition_score": asset.condition_score,
            "operating_hours": asset.operating_hours,
            "maintenance_due_days": asset.maintenance_due_days,
            "station_name": asset.station.name if asset.station else None,
        },
        mission={
            "id": str(mission.id),
            "code": mission.code,
            "name": mission.name,
            "status": mission.status,
            "priority": mission.priority,
            "station_name": mission.station.name if mission.station else None,
        },
        risk_event=risk_payload,
        recommendations=rec_payload,
    )


@router.get("/phase2/dashboard")
def get_phase2_dashboard(db: Session = Depends(get_db)) -> Phase2Dashboard:
    seed_demo_data_if_needed(db)
    active_expedition = db.query(Expedition).filter(Expedition.status == "ACTIVE").order_by(Expedition.start_date.desc()).first()
    personnel_count = db.query(Personnel).count()
    cargo_in_transit = db.query(CargoShipment).filter(CargoShipment.status.in_(["IN_TRANSIT", "DELAYED"])).count()
    delayed_cargo = db.query(CargoShipment).filter(CargoShipment.status == "DELAYED").count()
    critical_inventory = db.query(InventoryItem).filter(InventoryItem.current_quantity <= InventoryItem.minimum_stock).count()
    assets_attention = db.query(Asset).filter(Asset.status.in_(["MAINTENANCE_DUE", "UNDER_MAINTENANCE", "UNAVAILABLE"])) .count()
    active_missions = db.query(Mission).filter(Mission.status == "ACTIVE").count()
    open_risks = db.query(RiskEvent).count()
    stations = [station.code for station in db.query(Station).order_by(Station.name).all()]

    if active_expedition is None:
        raise HTTPException(status_code=404, detail="No active expedition found.")

    return Phase2Dashboard(
        active_expedition=active_expedition.name,
        personnel_deployed=personnel_count,
        cargo_in_transit=cargo_in_transit,
        delayed_cargo=delayed_cargo,
        critical_inventory=critical_inventory,
        assets_requiring_attention=assets_attention,
        active_missions=active_missions,
        open_risks=open_risks,
        polaris_alerts=max(1, open_risks),
        stations=stations,
    )


@router.get("/expeditions")
def list_expeditions(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Expedition).order_by(Expedition.start_date.desc()).all()
    output = []
    for row in rows:
        station_codes = [link.station.code for link in row.stations]
        output.append({
            "id": str(row.id),
            "code": row.code,
            "name": row.name,
            "status": row.status,
            "description": row.description,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "station_codes": station_codes,
            "personnel_count": len(row.personnel),
            "cargo_count": len(row.cargo_shipments),
            "mission_count": len(row.missions),
        })
    return output


@router.post("/expeditions")
def create_expedition(payload: ExpeditionCreate, db: Session = Depends(get_db)) -> ExpeditionRead:
    expedition = Expedition(
        code=payload.code,
        name=payload.name,
        status=payload.status,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(expedition)
    db.flush()
    for station_id in payload.station_ids:
        station = db.query(Station).filter(Station.id == station_id).first()
        if station is not None:
            db.add(ExpeditionStation(expedition_id=expedition.id, station_id=station.id))
    db.commit()
    return ExpeditionRead(
        id=str(expedition.id),
        code=expedition.code,
        name=expedition.name,
        status=expedition.status,
        description=expedition.description,
        start_date=expedition.start_date,
        end_date=expedition.end_date,
        created_at=expedition.created_at,
        station_codes=[link.station.code for link in expedition.stations],
    )


@router.get("/expeditions/{expedition_id}")
def get_expedition(expedition_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    expedition = db.query(Expedition).filter(Expedition.id == expedition_id).first()
    if expedition is None:
        raise HTTPException(status_code=404, detail="Expedition not found.")
    return {
        "id": str(expedition.id),
        "code": expedition.code,
        "name": expedition.name,
        "status": expedition.status,
        "description": expedition.description,
        "station_codes": [link.station.code for link in expedition.stations],
        "missions": [{"code": item.code, "name": item.name, "status": item.status} for item in expedition.missions],
        "assets": [{"code": item.code, "name": item.name, "status": item.status, "type": item.asset_type} for item in expedition.assets],
        "cargo": [{"code": item.code, "item_name": item.item_name, "status": item.status} for item in expedition.cargo_shipments],
        "transports": [{"code": item.code, "status": item.status} for item in expedition.transports],
        "personnel": [{"name": item.name, "role": item.role, "station": item.station.name if item.station else None} for item in expedition.personnel],
    }


@router.get("/inventory")
def list_inventory(db: Session = Depends(get_db), station: str | None = Query(default=None)) -> list[dict[str, Any]]:
    seed_demo_data_if_needed(db)
    query = db.query(InventoryItem)
    if station:
        query = query.join(Station).filter(Station.code == station)
    rows = query.order_by(InventoryItem.item_name).all()
    payload = []
    for row in rows:
        payload.append({
            "id": str(row.id),
            "code": row.code,
            "item_name": row.item_name,
            "category": row.category,
            "current_quantity": row.current_quantity,
            "reserved_quantity": row.reserved_quantity,
            "minimum_stock": row.minimum_stock,
            "reorder_threshold": row.reorder_threshold,
            "daily_usage": row.daily_usage,
            "unit": row.unit,
            "station_name": row.station.name if row.station else None,
            "available_quantity": row.available_quantity,
            "status": "CRITICAL" if row.current_quantity <= row.minimum_stock else "OK",
        })
    return payload


@router.get("/inventory/summary")
def inventory_summary(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    station_codes = ["MAITRI", "BHARATI"]
    summary = []
    for code in station_codes:
        station = db.query(Station).filter(Station.code == code).first()
        if station is None:
            continue
        items = db.query(InventoryItem).filter(InventoryItem.station_id == station.id).all()
        summary.append({
            "station_code": code,
            "station_name": station.name,
            "current_stock": sum(item.current_quantity for item in items),
            "low_stock_items": sum(1 for item in items if item.current_quantity <= item.minimum_stock),
            "critical_items": sum(1 for item in items if item.current_quantity <= item.reorder_threshold),
            "recent_transactions": [
                {
                    "item": tx.inventory_item.item_name,
                    "type": tx.transaction_type,
                    "quantity": tx.quantity,
                    "date": tx.recorded_at,
                }
                for tx in db.query(InventoryTransaction).filter(InventoryTransaction.station_id == station.id).order_by(InventoryTransaction.recorded_at.desc()).limit(5).all()
            ],
        })
    return summary


@router.post("/inventory/items")
def create_inventory_item(payload: dict[str, Any], db: Session = Depends(get_db)) -> InventoryRead:
    station = db.query(Station).filter(Station.id == payload["station_id"]).first()
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found.")
    item = InventoryItem(
        code=payload["code"],
        item_name=payload["item_name"],
        station_id=station.id,
        expedition_id=payload.get("expedition_id"),
        category=payload.get("category", "GENERAL"),
        current_quantity=float(payload.get("current_quantity", 0)),
        reserved_quantity=float(payload.get("reserved_quantity", 0)),
        minimum_stock=float(payload.get("minimum_stock", 0)),
        reorder_threshold=float(payload.get("reorder_threshold", 0)),
        daily_usage=float(payload.get("daily_usage", 0)),
        unit=payload.get("unit", "unit"),
    )
    db.add(item)
    db.commit()
    return InventoryRead(
        id=str(item.id),
        code=item.code,
        item_name=item.item_name,
        category=item.category,
        current_quantity=item.current_quantity,
        reserved_quantity=item.reserved_quantity,
        minimum_stock=item.minimum_stock,
        reorder_threshold=item.reorder_threshold,
        daily_usage=item.daily_usage,
        unit=item.unit,
        station_name=station.name,
        available_quantity=item.available_quantity,
    )


@router.post("/inventory/transactions")
def create_inventory_transaction(payload: InventoryTransactionCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = db.query(InventoryItem).filter(InventoryItem.id == payload.inventory_item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    item.last_updated = datetime.utcnow()
    if payload.transaction_type == "IN":
        item.current_quantity += payload.quantity
    elif payload.transaction_type == "OUT":
        item.current_quantity -= payload.quantity
    elif payload.transaction_type == "CONSUMPTION":
        item.current_quantity -= payload.quantity
    elif payload.transaction_type == "TRANSFER":
        item.current_quantity -= payload.quantity
    elif payload.transaction_type == "DAMAGE":
        item.current_quantity -= payload.quantity
    elif payload.transaction_type == "EXPIRED":
        item.current_quantity -= payload.quantity
    elif payload.transaction_type == "ADJUSTMENT":
        item.current_quantity += payload.quantity
    tx = InventoryTransaction(
        inventory_item_id=item.id,
        station_id=payload.station_id,
        transaction_type=payload.transaction_type,
        quantity=payload.quantity,
        reference=payload.reference,
        notes=payload.notes,
        recorded_at=datetime.utcnow(),
    )
    db.add(tx)
    db.commit()
    return {"status": "recorded", "transaction_type": payload.transaction_type, "item_code": item.code, "quantity": payload.quantity}


@router.get("/cargo")
def list_cargo(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(CargoShipment).order_by(CargoShipment.created_at.desc()).all()
    return [
        {
            "id": str(row.id),
            "code": row.code,
            "item_name": row.item_name,
            "status": row.status,
            "priority": row.priority,
            "criticality": row.criticality,
            "weight_kg": row.weight_kg,
            "volume_m3": row.volume_m3,
            "origin": row.origin_station.name if row.origin_station else None,
            "destination": row.destination_station.name if row.destination_station else None,
            "eta_days": row.eta_days,
        }
        for row in rows
    ]


@router.get("/cargo/{cargo_id}")
def get_cargo_detail(cargo_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    cargo = db.query(CargoShipment).filter(CargoShipment.id == cargo_id).first()
    if cargo is None:
        raise HTTPException(status_code=404, detail="Cargo not found.")
    timeline = [
        {"label": "Origin loaded", "date": cargo.planned_departure, "status": "Complete"},
        {"label": "Departure", "date": cargo.actual_departure, "status": cargo.status},
        {"label": "In transit", "date": cargo.estimated_arrival, "status": "On route"},
        {"label": "Arrival", "date": cargo.actual_arrival, "status": cargo.status},
    ]
    return {"cargo": {"code": cargo.code, "item_name": cargo.item_name, "status": cargo.status}, "timeline": timeline}


@router.get("/assets")
def list_assets(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Asset).order_by(Asset.asset_type).all()
    payload = []
    for row in rows:
        payload.append({
            "id": str(row.id),
            "code": row.code,
            "name": row.name,
            "type": row.asset_type,
            "status": row.status,
            "condition": row.condition_score,
            "station": row.station.name if row.station else None,
            "next_maintenance": row.next_maintenance,
        })
    return payload


@router.get("/personnel")
def list_personnel(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Personnel).order_by(Personnel.name).all()
    return [
        {
            "id": str(row.id),
            "name": row.name,
            "role": row.role,
            "specialization": row.specialization,
            "station": row.station.name if row.station else None,
            "movement_status": row.movement_status,
        }
        for row in rows
    ]


@router.post("/personnel")
def create_personnel(payload: PersonnelCreate, db: Session = Depends(get_db)) -> PersonnelRead:
    station = db.query(Station).filter(Station.id == payload.station_id).first()
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found.")
    person = Personnel(
        name=payload.name,
        role=payload.role,
        specialization=payload.specialization,
        station_id=station.id,
        expedition_id=payload.expedition_id,
        arrival_date=payload.arrival_date,
        departure_date=payload.departure_date,
        movement_status=payload.movement_status,
    )
    db.add(person)
    db.commit()
    return PersonnelRead(
        id=str(person.id),
        name=person.name,
        role=person.role,
        specialization=person.specialization,
        station_name=station.name,
        expedition_name=person.expedition.name if person.expedition else None,
        movement_status=person.movement_status,
    )


@router.get("/missions")
def list_missions(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Mission).order_by(Mission.name).all()
    payload = []
    for row in rows:
        payload.append({
            "id": str(row.id),
            "code": row.code,
            "name": row.name,
            "status": row.status,
            "priority": row.priority,
            "station": row.station.name if row.station else None,
            "dependencies": [{
                "required_type": item.required_type,
                "required_code": item.required_code,
                "required_name": item.required_name,
            } for item in row.requirements],
        })
    return payload


@router.get("/risk-events")
def list_risk_events(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(RiskEvent).order_by(RiskEvent.created_at.desc()).all()
    return [
        {
            "id": str(row.id),
            "event_type": row.event_type,
            "risk_type": row.risk_type,
            "severity": row.severity,
            "score": row.score,
            "title": row.title,
            "description": row.description,
            "explanation": row.explanation,
            "affected_entities": row.affected_entities,
            "dependency_chain": row.dependency_chain,
            "contributing_factors": row.contributing_factors,
        }
        for row in rows
    ]


@router.get("/recommendations")
def list_recommendations(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Recommendation).order_by(Recommendation.created_at.desc()).all()
    return [
        {
            "id": str(row.id),
            "risk_event_id": str(row.risk_event_id),
            "title": row.title,
            "action": row.action,
            "rationale": row.rationale,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    return [
        {
            "id": str(row.id),
            "recommendation_id": str(row.recommendation_id),
            "user_name": row.user_name,
            "decision": row.decision,
            "comment": row.comment,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/recommendations/{recommendation_id}/decision")
def decision_on_recommendation(recommendation_id: str, payload: AuditDecision, db: Session = Depends(get_db)) -> dict[str, Any]:
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    recommendation.status = payload.decision
    db.add(recommendation)

    audit = AuditLog(
        recommendation_id=recommendation.id,
        user_name=payload.user_name,
        decision=payload.decision,
        comment=payload.comment,
        created_at=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "saved",
        "recommendation_id": str(recommendation.id),
        "decision": payload.decision,
        "user_name": payload.user_name,
        "comment": payload.comment,
    }
