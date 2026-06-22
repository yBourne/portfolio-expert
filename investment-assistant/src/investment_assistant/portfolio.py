from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetType(StrEnum):
    ETF = "etf"
    STOCK = "stock"
    CASH = "cash"
    OTHER = "other"


class RiskLevel(StrEnum):
    NORMAL = "normal"
    HIGH = "high"


class TickerMetadata(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    name: str
    asset_type: AssetType
    sector: str | None = None
    theme: str | None = None
    risk_level: RiskLevel = RiskLevel.NORMAL

    @field_validator("name")
    @classmethod
    def non_empty_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("sector", "theme", mode="before")
    @classmethod
    def blank_metadata_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, float) and pd.isna(value):
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value


class Holding(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    ticker: str
    name: str
    asset_type: AssetType
    weight: float = Field(ge=0.0, le=1.0)
    sector: str | None = None
    theme: str | None = None
    risk_level: RiskLevel = RiskLevel.NORMAL

    @field_validator("ticker", "name")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("sector", "theme", mode="before")
    @classmethod
    def blank_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, float) and pd.isna(value):
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value


class AssetAllocation(BaseModel):
    etf_weight: float
    stock_weight: float
    cash_weight: float
    other_weight: float
    total_weight: float


def load_ticker_metadata(source: Path | str | dict[str, Any]) -> dict[str, TickerMetadata]:
    if isinstance(source, dict):
        data = source
    else:
        with Path(source).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

    tickers = data.get("tickers", {})
    return {ticker.upper(): TickerMetadata.model_validate(metadata) for ticker, metadata in tickers.items()}


def normalize_broker_summary_csv(raw_path: Path | str, metadata_path: Path | str, output_path: Path | str) -> Path:
    metadata = load_ticker_metadata(metadata_path)
    frame = pd.read_csv(raw_path)
    records: list[dict[str, object]] = []

    for raw_record in frame.to_dict(orient="records"):
        ticker = str(raw_record["Ticker"]).strip().upper()
        metadata_key = "CASH" if ticker in {"CASH FUND", "CASH"} else ticker
        if metadata_key not in metadata:
            raise ValueError(f"missing ticker metadata for {ticker}")
        ticker_metadata = metadata[metadata_key]
        records.append(
            {
                "ticker": metadata_key,
                "name": ticker_metadata.name,
                "asset_type": ticker_metadata.asset_type.value,
                "weight": round(float(raw_record["WeightPct"]) / 100, 10),
                "sector": ticker_metadata.sector,
                "theme": ticker_metadata.theme,
                "risk_level": ticker_metadata.risk_level.value,
            }
        )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame.from_records(records, columns=["ticker", "name", "asset_type", "weight", "sector", "theme", "risk_level"]).to_csv(output, index=False)
    return output


def load_holdings_csv(path: Path | str) -> list[Holding]:
    frame = pd.read_csv(path)
    holdings = [Holding(**record) for record in frame.to_dict(orient="records")]
    total_weight = sum(holding.weight for holding in holdings)
    if total_weight > 1.000001:
        raise ValueError(f"total holding weight exceeds 100%: {total_weight:.2%}")
    return holdings


def calculate_asset_allocation(holdings: list[Holding]) -> AssetAllocation:
    weights = {asset_type: 0.0 for asset_type in AssetType}
    for holding in holdings:
        weights[holding.asset_type] += holding.weight

    return AssetAllocation(
        etf_weight=round(weights[AssetType.ETF], 10),
        stock_weight=round(weights[AssetType.STOCK], 10),
        cash_weight=round(weights[AssetType.CASH], 10),
        other_weight=round(weights[AssetType.OTHER], 10),
        total_weight=round(sum(weights.values()), 10),
    )
