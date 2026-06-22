from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from investment_assistant.portfolio import AssetAllocation, AssetType, Holding, RiskLevel


class TargetIndexWeight(BaseModel):
    neutral: tuple[float, float]
    risk_off: tuple[float, float]
    risk_on: tuple[float, float]

    @field_validator("neutral", "risk_off", "risk_on")
    @classmethod
    def valid_range(cls, value: tuple[float, float]) -> tuple[float, float]:
        low, high = value
        if low < 0 or high > 1 or low > high:
            raise ValueError("target index ranges must be within [0, 1] and ordered")
        return value


class StockScoreThresholds(BaseModel):
    add_candidate: int
    hold: int
    reduce: int
    remove: int


class PortfolioRules(BaseModel):
    target_index_weight: TargetIndexWeight
    max_stock_weight: float = Field(ge=0.0, le=1.0)
    max_single_stock_weight: float = Field(ge=0.0, le=1.0)
    max_high_risk_single_stock_weight: float = Field(ge=0.0, le=1.0)
    max_sector_weight: float = Field(ge=0.0, le=1.0)
    max_theme_weight: float = Field(ge=0.0, le=1.0)
    min_cash_weight: float = Field(ge=0.0, le=1.0)
    max_turnover_per_rebalance: float = Field(ge=0.0, le=1.0)
    review_frequency: str
    stock_score_thresholds: StockScoreThresholds


class PositionLimitWarning(BaseModel):
    ticker: str
    current_weight: float
    limit: float
    message: str
    severity: Literal["info", "warning", "critical"] = "warning"
    action_hint: str = "review_position"


class ConcentrationWarning(BaseModel):
    kind: Literal["sector", "theme"]
    name: str
    current_weight: float
    limit: float
    message: str
    severity: Literal["info", "warning", "critical"] = "warning"
    action_hint: str = "review_concentration"


class AllocationWarning(BaseModel):
    metric: str
    current_weight: float
    limit: float | tuple[float, float]
    message: str
    severity: Literal["info", "warning", "critical"] = "warning"
    action_hint: str = "review_allocation"


def load_portfolio_rules(source: Path | str | dict[str, Any]) -> PortfolioRules:
    if isinstance(source, dict):
        data = source
    else:
        with Path(source).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    return PortfolioRules.model_validate(data["portfolio_rules"])


def check_single_position_limits(holdings: list[Holding], rules: PortfolioRules) -> list[PositionLimitWarning]:
    warnings: list[PositionLimitWarning] = []
    for holding in holdings:
        if holding.asset_type != AssetType.STOCK:
            continue
        limit = rules.max_high_risk_single_stock_weight if holding.risk_level == RiskLevel.HIGH else rules.max_single_stock_weight
        near_limit = holding.risk_level == RiskLevel.HIGH and holding.weight >= limit * 0.95
        if holding.weight > limit or near_limit:
            label = "高风险单只个股" if holding.risk_level == RiskLevel.HIGH else "单只个股"
            if holding.weight <= limit:
                severity: Literal["info", "warning", "critical"] = "info"
                action_hint = "do_not_add_without_review"
                message = f"{holding.ticker} {label}仓位 {holding.weight:.1%} 接近上限 {limit:.1%}"
            else:
                severity = "critical" if holding.weight >= limit * 1.2 else "warning"
                action_hint = "review_trim_to_limit"
                message = f"{holding.ticker} {label}仓位 {holding.weight:.1%} 高于上限 {limit:.1%}"
            warnings.append(
                PositionLimitWarning(
                    ticker=holding.ticker,
                    current_weight=holding.weight,
                    limit=limit,
                    message=message,
                    severity=severity,
                    action_hint=action_hint,
                )
            )
    return warnings


def check_sector_theme_limits(holdings: list[Holding], rules: PortfolioRules) -> list[ConcentrationWarning]:
    sector_weights: dict[str, float] = {}
    theme_weights: dict[str, float] = {}
    for holding in holdings:
        if holding.sector:
            sector_weights[holding.sector] = sector_weights.get(holding.sector, 0.0) + holding.weight
        if holding.theme:
            theme_weights[holding.theme] = theme_weights.get(holding.theme, 0.0) + holding.weight

    warnings: list[ConcentrationWarning] = []
    for sector, weight in sector_weights.items():
        if weight > rules.max_sector_weight:
            severity: Literal["info", "warning", "critical"] = "critical" if weight > 0.50 else "warning"
            warnings.append(ConcentrationWarning(kind="sector", name=sector, current_weight=weight, limit=rules.max_sector_weight, message=f"行业 {sector} 暴露 {weight:.1%} 高于上限 {rules.max_sector_weight:.1%}", severity=severity, action_hint="avoid_adding_to_sector"))
    for theme, weight in theme_weights.items():
        if weight > rules.max_theme_weight:
            severity = "critical" if weight > 0.50 else "warning"
            warnings.append(ConcentrationWarning(kind="theme", name=theme, current_weight=weight, limit=rules.max_theme_weight, message=f"主题 {theme} 暴露 {weight:.1%} 高于上限 {rules.max_theme_weight:.1%}", severity=severity, action_hint="avoid_adding_to_theme"))
    return warnings


def check_allocation_limits(allocation: AssetAllocation, rules: PortfolioRules, market_regime: Literal["neutral", "risk_off", "risk_on"] = "neutral") -> list[AllocationWarning]:
    warnings: list[AllocationWarning] = []
    index_min, index_max = getattr(rules.target_index_weight, market_regime)
    if allocation.etf_weight < index_min:
        warnings.append(AllocationWarning(metric="etf_weight", current_weight=allocation.etf_weight, limit=(index_min, index_max), message=f"指数 / ETF 仓位 {allocation.etf_weight:.1%} 低于 {market_regime} 下限 {index_min:.1%}"))
    if allocation.etf_weight > index_max:
        warnings.append(AllocationWarning(metric="etf_weight", current_weight=allocation.etf_weight, limit=(index_min, index_max), message=f"指数 / ETF 仓位 {allocation.etf_weight:.1%} 高于 {market_regime} 上限 {index_max:.1%}"))
    if allocation.stock_weight > rules.max_stock_weight:
        warnings.append(AllocationWarning(metric="stock_weight", current_weight=allocation.stock_weight, limit=rules.max_stock_weight, message=f"个股总仓位 {allocation.stock_weight:.1%} 高于上限 {rules.max_stock_weight:.1%}"))
    if allocation.cash_weight < rules.min_cash_weight:
        warnings.append(AllocationWarning(metric="cash_weight", current_weight=allocation.cash_weight, limit=rules.min_cash_weight, message=f"现金比例 {allocation.cash_weight:.1%} 低于最低比例 {rules.min_cash_weight:.1%}"))
    return warnings
