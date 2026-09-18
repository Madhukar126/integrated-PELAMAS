from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import (
    Asset,
    AssetMaintenance,
    CargoShipment,
    Expedition,
    ExpeditionStation,
    InventoryItem,
    InventoryTransaction,
    Mission,
    MissionDependency,
    Personnel,
    PersonnelMovement,
    Station,
    Transport,
)


def _ensure_station(db: Session, code: str, name: str, region: str) -> Station:
    station = db.query(Station).filter(Station.code == code).first()
    if station is None:
        station = Station(code=code, name=name, region=region)
        db.add(station)
        db.flush()
    return station


def _ensure_expedition(db: Session) -> Expedition:
    expedition = db.query(Expedition).filter(Expedition.code == "SIH26062").first()
    if expedition is None:
        expedition = Expedition(
            code="SIH26062",
            name="Polar Expedition SIH26062",
            status="ACTIVE",
            description="Synthetic/demo expedition for Phase 2 validation.",
            start_date=datetime.utcnow() - timedelta(days=21),
            end_date=datetime.utcnow() + timedelta(days=120),
        )
        db.add(expedition)
        db.flush()
    return expedition


def seed_demo_data(db: Session) -> None:
    goa = _ensure_station(db, "GOA", "NCPOR Goa", "India")
    bharati = _ensure_station(db, "BHARATI", "Bharati Station", "Antarctica")
    cape_town = _ensure_station(db, "CAPE_TOWN", "Cape Town Logistics Hub", "South Africa")
    maitri = _ensure_station(db, "MAITRI", "Maitri Station", "Antarctica")
    db.flush()

    expedition = _ensure_expedition(db)

    if not db.query(ExpeditionStation).filter_by(expedition_id=expedition.id, station_id=goa.id).first():
        db.add(ExpeditionStation(expedition_id=expedition.id, station_id=goa.id))
    if not db.query(ExpeditionStation).filter_by(expedition_id=expedition.id, station_id=bharati.id).first():
        db.add(ExpeditionStation(expedition_id=expedition.id, station_id=bharati.id))
    if not db.query(ExpeditionStation).filter_by(expedition_id=expedition.id, station_id=maitri.id).first():
        db.add(ExpeditionStation(expedition_id=expedition.id, station_id=maitri.id))

    transport = db.query(Transport).filter(Transport.code == "T04").first()
    if transport is None:
        transport = Transport(
            code="T04",
            status="IN_TRANSIT",
            expedition_id=expedition.id,
            origin_station_id=goa.id,
            destination_station_id=bharati.id,
            planned_departure=datetime.utcnow() - timedelta(days=5),
            actual_departure=datetime.utcnow() - timedelta(days=5),
            planned_arrival=datetime.utcnow() + timedelta(days=7),
            estimated_arrival=datetime.utcnow() + timedelta(days=7),
            actual_arrival=None,
            eta_days=7,
            delay_days=0,
        )
        db.add(transport)
        db.flush()

    cargo = db.query(CargoShipment).filter(CargoShipment.code == "C018").first()
    if cargo is None:
        cargo = CargoShipment(
            code="C018",
            expedition_id=expedition.id,
            transport_id=transport.id,
            origin_station_id=goa.id,
            destination_station_id=bharati.id,
            item_code="GF14",
            item_name="Generator Filter GF14",
            weight_kg=240.0,
            volume_m3=1.9,
            priority="CRITICAL",
            criticality="CRITICAL",
            status="IN_TRANSIT",
            required_by_date=datetime.utcnow() + timedelta(days=4),
            planned_departure=datetime.utcnow() - timedelta(days=5),
            actual_departure=datetime.utcnow() - timedelta(days=5),
            planned_arrival=datetime.utcnow() + timedelta(days=7),
            estimated_arrival=datetime.utcnow() + timedelta(days=7),
            actual_arrival=None,
            eta_days=7,
        )
        db.add(cargo)
        db.flush()

    inventory = db.query(InventoryItem).filter(InventoryItem.code == "GF14").first()
    if inventory is None:
        inventory = InventoryItem(
            code="GF14",
            item_name="Generator Filter GF14",
            expedition_id=expedition.id,
            station_id=bharati.id,
            category="SPARE_PART",
            current_quantity=8.0,
            reserved_quantity=2.0,
            minimum_stock=12.0,
            reorder_threshold=14.0,
            daily_usage=1.5,
            unit="unit",
            last_updated=datetime.utcnow(),
        )
        db.add(inventory)
        db.flush()

    if not db.query(InventoryTransaction).filter_by(inventory_item_id=inventory.id, transaction_type="IN").first():
        db.add(InventoryTransaction(
            inventory_item_id=inventory.id,
            station_id=bharati.id,
            transaction_type="IN",
            quantity=10.0,
            reference="PHASE1-INITIAL",
            notes="Initial stock receipt for Bharati Generator support.",
            recorded_at=datetime.utcnow() - timedelta(days=12),
        ))

    asset = db.query(Asset).filter(Asset.code == "G07").first()
    if asset is None:
        asset = Asset(
            code="G07",
            name="Generator G07",
            asset_type="Generator",
            expedition_id=expedition.id,
            station_id=bharati.id,
            status="OPERATING",
            condition_score=72,
            operating_hours=4442,
            maintenance_due_days=5,
            last_maintenance=datetime.utcnow() - timedelta(days=120),
            next_maintenance=datetime.utcnow() + timedelta(days=5),
        )
        db.add(asset)
        db.flush()

    if not db.query(AssetMaintenance).filter_by(asset_id=asset.id, maintenance_type="INSPECTION").first():
        db.add(AssetMaintenance(
            asset_id=asset.id,
            maintenance_type="INSPECTION",
            status="DUE",
            performed_at=datetime.utcnow() - timedelta(days=7),
            next_due_at=datetime.utcnow() + timedelta(days=5),
            notes="Generator inspection is pending due to sustained load on the observation mission.",
        ))

    mission = db.query(Mission).filter(Mission.code == "M12").first()
    if mission is None:
        mission = Mission(
            code="M12",
            name="Atmospheric Observation",
            expedition_id=expedition.id,
            station_id=bharati.id,
            status="ACTIVE",
            priority="HIGH",
            start_date=datetime.utcnow() - timedelta(days=3),
            end_date=datetime.utcnow() + timedelta(days=14),
            description="Environmental and atmospheric monitoring for the Antarctic research cycle.",
        )
        db.add(mission)
        db.flush()

    if not db.query(MissionDependency).filter_by(mission_id=mission.id, required_code="GF14").first():
        db.add(MissionDependency(
            mission_id=mission.id,
            required_type="INVENTORY",
            required_entity_id=inventory.id,
            required_code="GF14",
            required_name="Generator Filter GF14",
            notes="Required spare for generator reliability.",
        ))

    existing_personnel = db.query(Personnel).count()
    if existing_personnel == 0:
        personnel_names = [
            ("Asha Menon", "Field Engineer", "Power Systems", bharati.id),
            ("Rohan Pillai", "Logistics Officer", "Transport Coordination", goa.id),
            ("Leena Dutta", "Science Lead", "Atmospheric Science", bharati.id),
            ("Sameer Khan", "Maintenance Technician", "Power Systems", maitri.id),
            ("Priya Nair", "Station Manager", "Operations", bharati.id),
        ]
        for name, role, specialization, location_id in personnel_names:
            person = Personnel(
                name=name,
                role=role,
                specialization=specialization,
                expedition_id=expedition.id,
                station_id=location_id,
                arrival_date=datetime.utcnow() - timedelta(days=10),
                movement_status="ASSIGNED",
            )
            db.add(person)
            db.flush()
            db.add(PersonnelMovement(
                personnel_id=person.id,
                from_location="Goa",
                to_location="Antarctica",
                movement_type="ARRIVAL",
                movement_date=datetime.utcnow() - timedelta(days=10),
                notes="Deployment to the expedition zone.",
            ))

    if not db.query(Transport).filter(Transport.code == "T03").first():
        db.add(Transport(
            code="T03",
            expedition_id=expedition.id,
            status="IN_TRANSIT",
            origin_station_id=goa.id,
            destination_station_id=maitri.id,
            planned_departure=datetime.utcnow() - timedelta(days=2),
            actual_departure=datetime.utcnow() - timedelta(days=2),
            planned_arrival=datetime.utcnow() + timedelta(days=5),
            estimated_arrival=datetime.utcnow() + timedelta(days=5),
            eta_days=5,
            delay_days=0,
        ))

    if not db.query(CargoShipment).filter(CargoShipment.code == "C021").first():
        db.add(CargoShipment(
            code="C021",
            expedition_id=expedition.id,
            transport_id=transport.id,
            origin_station_id=goa.id,
            destination_station_id=maitri.id,
            item_code="ISS-12",
            item_name="Ice Sensor Array",
            weight_kg=160.0,
            volume_m3=1.4,
            priority="HIGH",
            criticality="HIGH",
            status="IN_TRANSIT",
            required_by_date=datetime.utcnow() + timedelta(days=6),
            planned_arrival=datetime.utcnow() + timedelta(days=5),
            estimated_arrival=datetime.utcnow() + timedelta(days=5),
            eta_days=5,
        ))

    if not db.query(Asset).filter(Asset.code == "S-104").first():
        asset_two = Asset(
            code="S-104",
            name="Snow Vehicle S-104",
            asset_type="Snow Vehicle",
            expedition_id=expedition.id,
            station_id=maitri.id,
            status="MAINTENANCE_DUE",
            condition_score=63,
            operating_hours=1280,
            maintenance_due_days=3,
            last_maintenance=datetime.utcnow() - timedelta(days=90),
            next_maintenance=datetime.utcnow() + timedelta(days=3),
        )
        db.add(asset_two)
        db.flush()
        db.add(AssetMaintenance(
            asset_id=asset_two.id,
            maintenance_type="BRAKE_CHECK",
            status="SCHEDULED",
            performed_at=datetime.utcnow() - timedelta(days=20),
            next_due_at=datetime.utcnow() + timedelta(days=3),
            notes="Winter operations require brake inspection before the next route cycle.",
        ))

    if not db.query(InventoryItem).filter(InventoryItem.code == "MED-01").first():
        db.add(InventoryItem(
            code="MED-01",
            item_name="Medical Kit",
            expedition_id=expedition.id,
            station_id=maitri.id,
            category="MEDICAL",
            current_quantity=12.0,
            reserved_quantity=3.0,
            minimum_stock=6.0,
            reorder_threshold=8.0,
            daily_usage=0.8,
            unit="kit",
            last_updated=datetime.utcnow(),
        ))

    db.commit()


def seed_demo_data_if_needed(db: Session) -> None:
    seed_demo_data(db)
