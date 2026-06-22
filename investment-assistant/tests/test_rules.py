from pathlib import Path

import pytest
from pydantic import ValidationError

from investment_assistant.portfolio import AssetType, Holding, RiskLevel, calculate_asset_allocation
from investment_assistant.rules import (
    check_allocation_limits,
    check_sector_theme_limits,
    check_single_position_limits,
    load_portfolio_rules,
)


def test_loads_confirmed_portfolio_rules():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))

    assert rules.target_index_weight.neutral == (0.30, 0.50)
    assert rules.max_stock_weight == 0.70
    assert rules.max_single_stock_weight == 0.25
    assert rules.max_high_risk_single_stock_weight == 0.10
    assert rules.max_sector_weight == 0.40
    assert rules.min_cash_weight == 0.00
    assert rules.max_turnover_per_rebalance == 0.15


def test_rejects_invalid_rule_percentages():
    with pytest.raises(ValidationError):
        load_portfolio_rules(
            {
                "portfolio_rules": {
                    "target_index_weight": {"neutral": [0.30, 1.20], "risk_off": [0.40, 0.50], "risk_on": [0.30, 0.40]},
                    "max_stock_weight": 0.70,
                    "max_single_stock_weight": 0.25,
                    "max_high_risk_single_stock_weight": 0.10,
                    "max_sector_weight": 0.40,
                    "max_theme_weight": 0.40,
                    "min_cash_weight": 0.00,
                    "max_turnover_per_rebalance": 0.15,
                    "review_frequency": "weekly",
                    "stock_score_thresholds": {"add_candidate": 75, "hold": 60, "reduce": 45, "remove": 35},
                }
            }
        )


def test_flags_single_stock_and_high_risk_position_limits():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = [
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.26, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
        Holding(ticker="TSLA", name="Tesla", asset_type=AssetType.STOCK, weight=0.11, sector="Consumer", theme="EV", risk_level=RiskLevel.HIGH),
    ]

    warnings = check_single_position_limits(holdings, rules)

    assert {warning.ticker for warning in warnings} == {"AAPL", "TSLA"}
    assert any("单只个股" in warning.message for warning in warnings)
    assert any("高风险" in warning.message for warning in warnings)


def test_flags_sector_and_theme_concentration_limits():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = [
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.21, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
        Holding(ticker="MSFT", name="Microsoft", asset_type=AssetType.STOCK, weight=0.20, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
    ]

    warnings = check_sector_theme_limits(holdings, rules)

    assert any(warning.kind == "sector" and warning.name == "Technology" for warning in warnings)
    assert any(warning.kind == "theme" and warning.name == "AI" for warning in warnings)


def test_high_risk_position_near_limit_gets_info_warning():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = [
        Holding(
            ticker="ONDS",
            name="Ondas Holdings",
            asset_type=AssetType.STOCK,
            weight=0.0984,
            sector="Technology",
            theme="Drones/Industrial IoT",
            risk_level=RiskLevel.HIGH,
        )
    ]

    warnings = check_single_position_limits(holdings, rules)

    assert len(warnings) == 1
    assert warnings[0].severity == "info"
    assert warnings[0].action_hint == "do_not_add_without_review"


def test_single_position_over_limit_gets_trim_action_hint():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = [
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.26, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
    ]

    warnings = check_single_position_limits(holdings, rules)

    assert warnings[0].severity == "warning"
    assert warnings[0].action_hint == "review_trim_to_limit"


def test_sector_concentration_warning_gets_avoid_adding_action_hint():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = [
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.21, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
        Holding(ticker="MSFT", name="Microsoft", asset_type=AssetType.STOCK, weight=0.20, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
    ]

    warnings = check_sector_theme_limits(holdings, rules)

    technology_warning = next(warning for warning in warnings if warning.kind == "sector" and warning.name == "Technology")
    assert technology_warning.severity == "warning"
    assert technology_warning.action_hint == "avoid_adding_to_sector"


def test_flags_allocation_limits():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    allocation = calculate_asset_allocation([
        Holding(ticker="VOO", name="VOO", asset_type=AssetType.ETF, weight=0.29, sector="Index", theme="US", risk_level=RiskLevel.NORMAL),
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.71, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
    ])

    warnings = check_allocation_limits(allocation, rules, market_regime="neutral")

    assert any("指数" in warning.message and "低于" in warning.message for warning in warnings)
    assert any("个股总仓位" in warning.message for warning in warnings)
