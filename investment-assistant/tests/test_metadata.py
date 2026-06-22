from pathlib import Path

from investment_assistant.portfolio import AssetType, RiskLevel, load_ticker_metadata


def test_loads_ticker_metadata_config():
    metadata = load_ticker_metadata(Path("config/ticker_metadata.v1.yaml"))

    assert metadata["SPY"].name == "SPDR S&P 500 ETF Trust"
    assert metadata["SPY"].asset_type == AssetType.ETF
    assert metadata["ONDS"].risk_level == RiskLevel.HIGH


def test_ticker_metadata_keys_are_normalized_to_uppercase(tmp_path):
    metadata_file = tmp_path / "ticker_metadata.yaml"
    metadata_file.write_text(
        """
tickers:
  spy:
    name: SPDR S&P 500 ETF Trust
    asset_type: etf
    sector: Index
    theme: US Large Cap
    risk_level: normal
""".strip(),
        encoding="utf-8",
    )

    metadata = load_ticker_metadata(metadata_file)

    assert "SPY" in metadata
    assert metadata["SPY"].asset_type == AssetType.ETF
