from pathlib import Path

import pytest
from pydantic import ValidationError

from investment_assistant.portfolio import AssetType, Holding, RiskLevel, calculate_asset_allocation, load_holdings_csv, normalize_broker_summary_csv


def test_holding_validates_weight_bounds():
    Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.25, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL)

    with pytest.raises(ValidationError):
        Holding(ticker="BAD", name="Bad", asset_type=AssetType.STOCK, weight=1.01, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL)

    with pytest.raises(ValidationError):
        Holding(ticker="BAD", name="Bad", asset_type=AssetType.STOCK, weight=-0.01, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL)


def test_loads_holdings_from_csv():
    holdings = load_holdings_csv(Path("examples/holdings.sample.csv"))

    assert len(holdings) == 3
    assert holdings[0].ticker == "VOO"
    assert holdings[0].asset_type == AssetType.ETF
    assert holdings[2].asset_type == AssetType.CASH


def test_calculates_asset_allocation():
    holdings = [
        Holding(ticker="VOO", name="VOO", asset_type=AssetType.ETF, weight=0.30, sector="Index", theme="US", risk_level=RiskLevel.NORMAL),
        Holding(ticker="AAPL", name="Apple", asset_type=AssetType.STOCK, weight=0.10, sector="Technology", theme="AI", risk_level=RiskLevel.NORMAL),
        Holding(ticker="CASH", name="Cash", asset_type=AssetType.CASH, weight=0.05, sector=None, theme=None, risk_level=RiskLevel.NORMAL),
    ]

    allocation = calculate_asset_allocation(holdings)

    assert allocation.etf_weight == 0.30
    assert allocation.stock_weight == 0.10
    assert allocation.cash_weight == 0.05
    assert allocation.other_weight == 0.0
    assert allocation.total_weight == 0.45


def test_normalizes_broker_summary_csv_with_metadata(tmp_path):
    raw = tmp_path / "broker_summary.csv"
    raw.write_text(
        "Ticker,MarketValueUSD,WeightPct\nSPY,34510,34.51\nONDS,9840,9.84\nCASH,4440,4.44\n",
        encoding="utf-8",
    )
    output = tmp_path / "current_holdings.csv"

    result = normalize_broker_summary_csv(
        raw_path=raw,
        metadata_path=Path("config/ticker_metadata.v1.yaml"),
        output_path=output,
    )

    assert result == output
    holdings = load_holdings_csv(output)
    assert holdings[0].ticker == "SPY"
    assert holdings[0].weight == 0.3451
    assert holdings[0].asset_type == AssetType.ETF
    assert holdings[1].ticker == "ONDS"
    assert holdings[1].risk_level == RiskLevel.HIGH
    assert holdings[1].sector == "Technology"
    assert holdings[2].asset_type == AssetType.CASH


def test_normalizes_broker_cash_fund_to_cash(tmp_path):
    raw = tmp_path / "broker_summary.csv"
    raw.write_text("Ticker,MarketValueUSD,WeightPct\nCash Fund,4000,4.44\n", encoding="utf-8")
    output = tmp_path / "current_holdings.csv"

    normalize_broker_summary_csv(raw_path=raw, metadata_path=Path("config/ticker_metadata.v1.yaml"), output_path=output)

    holdings = load_holdings_csv(output)
    assert holdings[0].ticker == "CASH"
    assert holdings[0].name == "Cash"
    assert holdings[0].asset_type == AssetType.CASH
    assert holdings[0].weight == 0.0444
