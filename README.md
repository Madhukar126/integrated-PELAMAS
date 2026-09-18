# POLARIS

POLARIS is a synthetic, dependency-aware expedition intelligence platform built for the Smart India Hackathon problem SIH26062. It models how a transport delay can propagate through cargo, inventory, assets, and mission execution, then explains the operational risk and the recommended mitigation path.

## Problem
Polar expedition operations rely on a coordinated network of transport, cargo flow, inventory reserve, asset availability, and mission continuity. A disruption in one node can cascade quickly across the full mission. Existing operational tooling often tracks each domain separately and does not surface the dependency chain or explain the impact in a human-reviewable way.

## Solution
POLARIS integrates:
- deterministic risk analysis
- inventory and mission dependency tracking
- cargo optimization under operational constraints
- demand and shortage forecasting
- asset risk evaluation
- human recommendation approval and audit logging
- judge-ready mission-control presentation

## Key features
- Mission Control dashboard for expedition status and alerting
- 8-day delay simulation for the T04 -> C018 -> GF14 -> G07 -> M12 chain
- Explainable risk event generation and recommendation workflow
- Inventory shortage detection and demand forecasting
- Cargo optimization using OR-Tools CP-SAT
- Asset health and mission risk evaluation
- Demo reset and repeatable SIH walkthrough flow
- Audit trail for approvals and rejections

## Architecture
The system uses a Next.js frontend and a FastAPI backend backed by PostgreSQL. The backend exposes operational APIs and decision-support outputs, while the frontend presents a mission-control dashboard and judge-oriented demo flows.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the detailed design.

## Technology stack
- Frontend: Next.js 16 + TypeScript + React + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL
- Optimization: OR-Tools CP-SAT
- Testing: Pytest

## AI / ML
The project contains deterministic, explainable operational intelligence for:
- demand forecasting
- shortage prediction
- asset risk analysis
- risk fusion
- cargo optimization

See [AI_MODELS.md](AI_MODELS.md) for the model details and synthetic-data caveats.

## Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL running on localhost:5433
- Optional: Docker Compose

### 1. Create the Python environment
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 2. Prepare environment files
Copy the examples and adjust values if needed.
```powershell
copy .env.example .env
copy backend\.env.example backend\.env
```

### 3. Start PostgreSQL
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS
& "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" -D ".postgres-data" -l ".postgres-data\postgres.log" -o "-p 5433 -h localhost" start
```

### 4. Start the backend
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS\backend
$env:PYTHONPATH = "$PWD"
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Start the frontend
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS\frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

## Demo data
The project uses synthetic demonstration data and labels it as such throughout the UI and documentation.

The core demo path is:
- Maitri
- Bharati
- Goa
- Cape Town
- Transport T04
- Cargo C018
- Generator Filter GF14
- Generator G07
- Mission M12

## SIH Demo Mode
The project exposes the demo entry page at http://localhost:3000/demo and the operational dashboard at http://localhost:3000/.

Controls include:
- RESET DEMO
- START DEMO
- SIMULATE DELAY
- VIEW IMPACT
- RUN OPTIMIZATION

## How to test
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS
$env:PYTHONPATH = "$PWD\backend"
.\.venv\Scripts\python.exe -m pytest backend/tests -q
```

## Production build check
```powershell
cd c:\Users\madhu\Downloads\integrated PELAMS\frontend
npm run build
```

## Important docs
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DATABASE.md](DATABASE.md)
- [AI_MODELS.md](AI_MODELS.md)
- [JUDGE_QA.md](JUDGE_QA.md)
- [NOVELTY.md](NOVELTY.md)
- [DEMO.md](DEMO.md)

## Prototype limitations
- synthetic demonstration data only
- prototype risk weights and configuration
- no official NCPOR threshold claims
- human validation still required for critical operational decisions

## Future scope
- real integration with operational telemetry
- better calibration from historical data
- expanded role-based access and identity systems
- production-grade monitoring and deployment controls

## Final status
POLARIS is currently in a stable, judge-ready, synthetic-demo state. It preserves the validated Phase 1–4 functionality while adding the final deployment and documentation layer required for the SIH demo and review flow.
