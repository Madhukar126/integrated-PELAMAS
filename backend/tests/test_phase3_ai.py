from backend.polaris.forecasting.demand_forecasting import DemandForecastingEngine
from backend.polaris.inventory.shortage_predictor import ShortagePredictor
from backend.polaris.optimization.cargo_optimizer import CargoOptimizer
from backend.polaris.risk.dependency_analyzer import DependencyAnalyzer
from backend.polaris.risk.risk_fusion import RiskFusionEngine


def test_demand_forecast_predicts_reductions_for_low_stock_item() -> None:
    history = [120, 118, 110, 106, 101, 95, 92, 88]
    engine = DemandForecastingEngine(history=history, horizon_days=14)
    result = engine.forecast()

    assert result["model_used"] in {"moving_average", "random_forest"}
    assert result["forecast_horizon_days"] == 14
    assert result["predicted_consumption"] > 0
    assert "explanation" in result


def test_shortage_prediction_reports_days_of_supply_and_status() -> None:
    predictor = ShortagePredictor(available_inventory=1200, reserved_inventory=100, predicted_daily_consumption=35, next_resupply_days=40, minimum_reserve=250)
    result = predictor.evaluate()

    assert result["estimated_days_of_supply"] > 0
    assert result["severity"] in {"SAFE", "WATCH", "HIGH RISK", "CRITICAL"}
    assert "gap_days" in result


def test_cargo_optimizer_selects_high_priority_goods_within_capacity() -> None:
    optimizer = CargoOptimizer(
        weight_capacity=10000,
        volume_capacity=40,
        cargo=[
            {"id": "med-1", "weight_kg": 2500, "volume_m3": 8, "criticality": 5, "required_by_days": 3, "shortage_risk": 0.8, "mission_impact": 5},
            {"id": "food-1", "weight_kg": 3000, "volume_m3": 10, "criticality": 3, "required_by_days": 7, "shortage_risk": 0.5, "mission_impact": 4},
            {"id": "gf14", "weight_kg": 1800, "volume_m3": 5, "criticality": 5, "required_by_days": 2, "shortage_risk": 0.95, "mission_impact": 9},
            {"id": "routine-1", "weight_kg": 5000, "volume_m3": 16, "criticality": 1, "required_by_days": 20, "shortage_risk": 0.1, "mission_impact": 2},
        ],
    )
    result = optimizer.optimize()

    assert result["selected_ids"]
    assert result["total_weight_kg"] <= 10000
    assert result["total_volume_m3"] <= 40
    assert "gf14" in "".join(result["selected_ids"])


def test_dependency_analyzer_builds_graph_and_risk_fusion_scores() -> None:
    analyzer = DependencyAnalyzer()
    graph = analyzer.analyze_transport_chain(
        transport_code="T04",
        cargo_code="C018",
        inventory_code="GF14",
        asset_code="G07",
        mission_code="M12",
    )

    assert graph["nodes"]
    assert graph["edges"]
    assert any(node["id"] == "T04" for node in graph["nodes"])

    fusion = RiskFusionEngine()
    score = fusion.calculate(
        inventory_risk=72,
        transport_risk=82,
        asset_risk=60,
        mission_risk=55,
        environment_risk=40,
    )

    assert 0 <= score["overall_score"] <= 100
    assert score["severity"] in {"LOW", "MODERATE", "HIGH", "CRITICAL"}
    assert score["contributors"]
