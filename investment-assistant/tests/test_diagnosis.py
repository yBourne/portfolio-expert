from pathlib import Path

from investment_assistant.diagnosis import DiagnosisResult, diagnose_portfolio
from investment_assistant.portfolio import load_holdings_csv
from investment_assistant.rules import load_portfolio_rules


def test_diagnose_portfolio_returns_structured_result():
    holdings = load_holdings_csv(Path("examples/current_holdings.csv"))
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))

    result = diagnose_portfolio(holdings, rules)

    assert isinstance(result, DiagnosisResult)
    assert result.allocation.stock_weight == 0.6102
    assert result.allocation.etf_weight == 0.3451
    assert result.health_score < 100
    assert "Technology" in result.summary
    technology_warning = next(warning for warning in result.warnings if warning.metadata.get("name") == "Technology")
    assert technology_warning.severity == "warning"
    assert technology_warning.action_hint == "avoid_adding_to_sector"
    assert technology_warning.message == "行业 Technology 暴露 47.6% 高于上限 40.0%"
    onds_warning = next(warning for warning in result.warnings if warning.metadata.get("ticker") == "ONDS")
    assert onds_warning.severity == "info"
    assert onds_warning.action_hint == "do_not_add_without_review"


def test_diagnosis_result_can_be_serialized_to_json():
    holdings = load_holdings_csv(Path("examples/current_holdings.csv"))
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))

    result = diagnose_portfolio(holdings, rules)
    data = result.model_dump()

    assert data["allocation"]["stock_weight"] == 0.6102
    assert {warning["action_hint"] for warning in data["warnings"]} >= {"avoid_adding_to_sector", "do_not_add_without_review"}
