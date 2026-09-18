# AI and Decision Models

## Demand forecasting
- Model: deterministic consumption forecasting implemented in the backend
- Features: recent inventory history, station context, item_code, and trend slope
- Forecast horizon: configurable, default 30 days
- Metric: simple forecasting error proxy and confidence score
- Limitation: this is a synthetic demonstration model and should not be treated as an official operational forecasting system

## Shortage prediction
- Formula: compares available inventory, reserved inventory, predicted daily consumption, and next resupply interval
- Outputs: estimated days of supply, resupply gap, and severity grade
- Use case: detects when stock will likely fall below a safe reserve threshold before a mission is impacted

## Asset risk
- Features: condition score, maintenance timing, uptime pressure, and operational role
- Result: an asset risk indicator and explainable conditions that reduce confidence in critical systems

## Cargo optimization
- Engine: OR-Tools CP-SAT
- Objective: maximize mission value while respecting weight and volume constraints
- Output: selected cargo IDs, deferred cargo IDs, and utilization metrics
- Constraints: weight and volume capacity must remain inside the configured limits

## Risk fusion
- Risk fusion combines weighted contributions from inventory risk, transport risk, asset risk, mission risk, and environment risk
- Output: final risk score and factor explanation
- Scope: demonstration-level and configurable; not an official NCPOR thresholding system

## Safety statement
All model outputs in the demo are based on synthetic data and should be validated with real expedition data before operational deployment.
