# Database Design

## Core entities

### Transport
Represents the movement of material between logistics hubs. The demo scenario centers on Transport T04, which is delayed to simulate downstream mission disruption.

### Cargo
Cargo shipments such as C018 are linked to transport, destination, inventory needs, and mission criticality. Delay propagation starts at cargo shipment disruption.

### Inventory
Inventory items such as GF14 represent critical consumables or replacement parts. The model tracks current quantity, reserved quantity, minimum stock, and reorder thresholds.

### Asset
Assets such as G07 provide operational capability. The system models condition, status, maintenance timing, and mission-critical availability.

### Mission
Mission records like M12 describe the expedition objective that can be placed under operational risk when dependencies degrade.

## Relationship flow
Transport -> Cargo -> Inventory -> Asset -> Mission

This is the core explainability path used by POLARIS.

## Important schema notes
- Each expedition connects multiple stations, personnel, assets, and mission plans
- Inventory and cargo records are linked to station and expedition context
- Risk events and recommendations are recorded separately so the operational cause and decision outcome remain traceable
- Audit logs record the human decision and commentary so approvals and rejections are explainable

## Demo configuration
The seed data includes the demonstration chain:
- Maitri
- Bharati
- Goa
- Cape Town
- Transport T04
- Cargo C018
- Generator Filter GF14
- Generator G07
- Mission M12
