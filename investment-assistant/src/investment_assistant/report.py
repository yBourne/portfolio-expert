from __future__ import annotations

from investment_assistant.diagnosis import DiagnosisResult, diagnose_portfolio
from investment_assistant.portfolio import Holding
from investment_assistant.rules import PortfolioRules


def render_health_report(result: DiagnosisResult) -> str:
    allocation = result.allocation
    lines = [
        "# 组合健康报告",
        "",
        "## 组合摘要",
        "",
        f"- 指数 / ETF 仓位：{allocation.etf_weight:.1%}",
        f"- 个股仓位：{allocation.stock_weight:.1%}",
        f"- 现金比例：{allocation.cash_weight:.1%}",
        f"- 其他资产：{allocation.other_weight:.1%}",
        f"- 已录入权重合计：{allocation.total_weight:.1%}",
        f"- 健康分数：{result.health_score}",
        "",
        "## 规则检查结果",
        "",
    ]

    if result.warnings:
        for warning in result.warnings:
            lines.append(f"- ⚠️ [{warning.severity}] {warning.message}；建议动作：`{warning.action_hint}`")
    else:
        lines.append("- ✅ 暂无硬性超限。")

    lines.extend(
        [
            "",
            "## 建议动作",
            "",
            "- 本报告只提供诊断和建议，不自动交易。",
            "- `avoid_adding_to_sector`：该行业超限前，避免继续加仓同一行业。",
            "- `do_not_add_without_review`：接近高风险单票上限，未复核前不继续加仓。",
            "- `review_trim_to_limit`：单票超限，复核是否分批降至规则上限内。",
            "- 如出现超限，优先进入人工复核；大额调仓继续遵守 48 小时冷静期。",
            "",
            "## 依据与风险提示",
            "",
            "- 依据：`portfolio_rules.v1.yaml` 与 Obsidian 中的 [[Portfolio Rules]]。",
            "- 风险提示：本报告不是财务顾问意见，所有买入、卖出、调仓动作必须由本人确认。",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_health_report(holdings: list[Holding], rules: PortfolioRules, market_regime: str = "neutral") -> str:
    return render_health_report(diagnose_portfolio(holdings, rules, market_regime=market_regime))
