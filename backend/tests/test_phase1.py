import os
import sys
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import Base
from app.db.models import Asset, CargoShipment, InventoryItem, Mission, Station, Transport
from app.services.polaris_engine import evaluate_transport_delay


def _build_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    station = Station(code="BHARATI", name="Bharati Station", region="Antarctica")
    session.add(station)
    session.flush()

    transport = Transport(
        code="T04",
        status="IN_TRANSIT",
        origin_station_id=station.id,
        destination_station_id=station.id,
        planned_departure=datetime.utcnow(),
        actual_departure=datetime.utcnow(),
        planned_arrival=datetime.utcnow() + timedelta(days=7),
        estimated_arrival=datetime.utcnow() + timedelta(days=7),
        eta_days=7,
        delay_days=0,
    )
    session.add(transport)
    session.flush()

    cargo = CargoShipment(
        code="C018",
        transport_id=transport.id,
        origin_station_id=station.id,
        destination_station_id=station.id,
        item_code="GF14",
        item_name="Generator Filter GF14",
        weight_kg=240,
        volume_m3=1.9,
        priority="CRITICAL",
        criticality="CRITICAL",
        status="IN_TRANSIT",
        planned_arrival=datetime.utcnow() + timedelta(days=7),
        estimated_arrival=datetime.utcnow() + timedelta(days=7),
        eta_days=7,
    )
    session.add(cargo)

    inventory = InventoryItem(
        code="GF14",
        item_name="Generator Filter GF14",
        station_id=station.id,
        category="SPARE_PART",
        current_quantity=8,
        reserved_quantity=2,
        minimum_stock=12,
        reorder_threshold=14,
        daily_usage=1.5,
        unit="unit",
    )
    session.add(inventory)

    asset = Asset(
        code="G07",
        asset_type="Generator",
        station_id=station.id,
        status="OPERATING",
        condition_score=72,
        operating_hours=4442,
        maintenance_due_days=5,
    )
    session.add(asset)

    mission = Mission(
        code="M12",
        name="Atmospheric Observation",
        station_id=station.id,
        status="ACTIVE",
        priority="HIGH",
    )
    session.add(mission)
    session.commit()
    return session


def test_evaluate_transport_delay_identifies_high_risk() -> None:
    session = _build_session()
    transport = session.query(Transport).filter(Transport.code == "T04").one()
    transport.delay_days = 8
    session.commit()

    result = evaluate_transport_delay(session, "T04")

    assert result["severity"] == "HIGH"
    assert result["score"] >= 70
    assert "T04" in result["dependency_chain"][0]
    assert "M12" in result["dependency_chain"][-1]
    assert any(f["name"] == "Transport Delay" for f in result["contributing_factors"])
