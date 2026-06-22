from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from investment_assistant.portfolio import AssetAllocation, Holding, calculate_asset_allocation
from investment_assistant.rules import (
    PortfolioRules,
    check_allocation_limits,
    check_sector_theme_limits,
    check_single_position_limits,
)


class RuleWarning(BaseModel):
    category: str
    message: str
    current_weight: float
    limit: float | tuple[float, float]
    severity: Literal["info", "warning", "critical"] = "warning"
    action_hint: str = "review"
    metadata: dict[str, Any] = {}


class DiagnosisResult(BaseModel):
    allocation: AssetAllocation
    warnings: list[RuleWarning]
    health_score: int
    summary: str


def _to_rule_warning(warning: BaseModel) -> RuleWarning:
    data = warning.model_dump()
    if "metric" in data:
        category = str(data["metric"])
    elif "ticker" in data:
        category = "position"
    elif "kind" in data:
        category = str(data["kind"])
    else:
        category = "rule"

    metadata = {key: value for key, value in data.items() if key not in {"message", "current_weight", "limit", "severity", "action_hint"}}
    return RuleWarning(
        category=category,
        message=str(data["message"]),
        current_weight=float(data["current_weight"]),
        limit=data["limit"],
        severity=data.get("severity", "warning"),
        action_hint=data.get("action_hint", "review"),
        metadata=metadata,
    )


def _summarize_warnings(warnings: list[RuleWarning]) -> str:
    if not warnings:
        return "暂无硬性超限。"
    return "；".join(warning.message for warning in warnings)


def _calculate_health_score(warnings: list[RuleWarning]) -> int:
    severity_penalties = {"info": 2, "warning": 10, "critical": 20}
    return max(0, 100 - sum(severity_penalties[warning.severity] for warning in warnings))


def diagnose_portfolio(holdings: list[Holding], rules: PortfolioRules, market_regime: str = "neutral") -> DiagnosisResult:
    allocation = calculate_asset_allocation(holdings)
    raw_warnings = [
        *check_allocation_limits(allocation, rules, market_regime=market_regime),
        *check_single_position_limits(holdings, rules),
        *check_sector_theme_limits(holdings, rules),
    ]
    warnings = [_to_rule_warning(warning) for warning in raw_warnings]
    return DiagnosisResult(
        allocation=allocation,
        warnings=warnings,
        health_score=_calculate_health_score(warnings),
        summary=_summarize_warnings(warnings),
    )
