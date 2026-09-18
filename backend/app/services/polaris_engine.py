from __future__ import annotations

from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.db.models import Asset, CargoShipment, InventoryItem, Mission, Recommendation, RiskEvent, Transport


def _severity_from_score(score: int) -> str:
    if score >= 90:
        return "CRITICAL"
    if score >= 75:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"


def evaluate_transport_delay(db: Session, transport_code: str = "T04") -> dict:
    transport = db.query(Transport).filter(Transport.code == transport_code).first()
    if transport is None:
        raise ValueError(f"Transport {transport_code} was not found.")

    cargo = db.query(CargoShipment).filter(CargoShipment.transport_id == transport.id).first()
    if cargo is None:
        raise ValueError(f"Cargo for transport {transport_code} was not found.")

    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    asset = db.query(Asset).filter(Asset.code == "G07").first()
    mission = db.query(Mission).filter(Mission.code == "M12").first()

    if inventory is None or asset is None or mission is None:
        raise ValueError("Phase 1 dependency data is incomplete.")

    days_of_supply = inventory.current_quantity / inventory.daily_usage if inventory.daily_usage > 0 else 0
    reserve_gap = max(0.0, inventory.minimum_stock - inventory.current_quantity)
    transport_component = min(30, max(0, transport.delay_days * 2))
    inventory_component = min(30, max(0, int((inventory.minimum_stock - days_of_supply) * 4)))
    asset_component = 15 if asset.condition_score < 75 or asset.maintenance_due_days <= 7 else 8
    mission_component = 18 if mission.status == "ACTIVE" else 8
    score = min(100, int(transport_component + inventory_component + asset_component + mission_component + 12))
    severity = _severity_from_score(score)

    contributing_factors = [
        {"name": "Transport Delay", "contribution": int(transport_component), "reason": f"Transport {transport_code} was delayed by {transport.delay_days} days and pushed cargo delivery beyond the maintenance window."},
        {"name": "Inventory Reserve", "contribution": int(inventory_component), "reason": f"GF14 stock at Bharati sits at {inventory.current_quantity} units against a minimum reserve of {inventory.minimum_stock} and only {days_of_supply:.1f} days of supply."},
        {"name": "Asset Condition", "contribution": int(asset_component), "reason": f"Generator G07 is operating with a condition score of {asset.condition_score}/100 and maintenance is due in {asset.maintenance_due_days} days."},
        {"name": "Mission Dependency", "contribution": int(mission_component), "reason": f"Mission M12 is active and depends on Generator G07 and the replacement GF14 filter."},
    ]

    affected_entities = [
        f"Cargo {cargo.code}",
        f"Generator Filter {inventory.code}",
        "Bharati Station",
        f"Generator {asset.code}",
        f"Mission {mission.code}",
    ]

    dependency_chain = [
        transport.code,
        cargo.code,
        inventory.code,
        "Bharati Inventory",
        asset.code,
        mission.code,
    ]

    explanation = (
        f"Transport {transport.code} was delayed by {transport.delay_days} days, which pushed {cargo.code} beyond the planned delivery window for {inventory.code}. "
        f"At Bharati, the remaining stock is {inventory.current_quantity} {inventory.unit} versus a minimum reserve of {inventory.minimum_stock} and only {days_of_supply:.1f} days of supply. "
        f"This increases operational risk for {asset.code}, which supports mission {mission.code}."
    )

    recommendation_titles = [
        {
            "title": "Approve emergency replacement freight",
            "action": "APPROVE_EMERGENCY_REPLACEMENT",
            "rationale": "Prioritize an expedited convoy for the replacement filter to maintain Generator G07 availability for Mission M12.",
        },
        {
            "title": "Modify mission timeline",
            "action": "MODIFY_MISSION_SCHEDULE",
            "rationale": "Shift non-critical atmospheric observations to absorb the maintenance window while preserving the mission-critical observation sequence.",
        },
        {
            "title": "Reject the current plan and keep reserve inventory",
            "action": "REJECT_BASELINE_PLAN",
            "rationale": "Hold the current course until the procurement and maintenance decisions are confirmed by the expedition manager.",
        },
    ]

    return {
        "risk_type": "TRANSPORT_DELAY",
        "event_type": "TRANSPORT_DELAY",
        "score": score,
        "severity": severity,
        "title": f"{severity} RISK: {transport.code} delay impacts mission readiness",
        "description": f"Transport {transport.code} delayed by {transport.delay_days} days.",
        "explanation": explanation,
        "affected_entities": affected_entities,
        "dependency_chain": dependency_chain,
        "contributing_factors": contributing_factors,
        "recommendations": recommendation_titles,
        "days_of_supply": round(days_of_supply, 1),
        "reserve_gap": round(reserve_gap, 1),
        "transport_delay_days": transport.delay_days,
    }


def create_risk_event_and_recommendations(db: Session, transport_code: str = "T04") -> dict:
    result = evaluate_transport_delay(db, transport_code)

    event = RiskEvent(
        event_type=result["event_type"],
        risk_type=result["risk_type"],
        severity=result["severity"],
        score=result["score"],
        title=result["title"],
        description=result["description"],
        explanation=result["explanation"],
        affected_entities=result["affected_entities"],
        dependency_chain=result["dependency_chain"],
        contributing_factors=result["contributing_factors"],
        transport_code=transport_code,
        cargo_code="C018",
        inventory_code="GF14",
        asset_code="G07",
        mission_code="M12",
        created_at=datetime.utcnow(),
    )
    db.add(event)
    db.flush()

    recommendations = []
    for item in result["recommendations"]:
        recommendation = Recommendation(
            risk_event_id=event.id,
            title=item["title"],
            action=item["action"],
            rationale=item["rationale"],
            status="OPEN",
            created_at=datetime.utcnow(),
        )
        db.add(recommendation)
        db.flush()
        recommendations.append(recommendation)

    db.commit()

    return {
        "risk_event": event,
        "recommendations": recommendations,
    }
