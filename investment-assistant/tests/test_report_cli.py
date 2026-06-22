import json
from pathlib import Path

from investment_assistant.cli import run_diagnose, run_normalize
from investment_assistant.portfolio import load_holdings_csv
from investment_assistant.report import generate_health_report
from investment_assistant.rules import load_portfolio_rules


def test_generates_health_report_markdown():
    rules = load_portfolio_rules(Path("config/portfolio_rules.v1.yaml"))
    holdings = load_holdings_csv(Path("examples/holdings.sample.csv"))

    report = generate_health_report(holdings, rules)

    assert "# 组合健康报告" in report
    assert "## 组合摘要" in report
    assert "## 规则检查结果" in report
    assert "依据" in report


def test_cli_diagnose_writes_report(tmp_path):
    output = tmp_path / "portfolio-health-report.md"

    run_diagnose(
        holdings_path=Path("examples/holdings.sample.csv"),
        rules_path=Path("config/portfolio_rules.v1.yaml"),
        output_path=output,
    )

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "# 组合健康报告" in content
    assert "## 规则检查结果" in content


def test_cli_diagnose_writes_json_output(tmp_path):
    markdown_output = tmp_path / "portfolio-health-report.md"
    json_output = tmp_path / "portfolio-health-report.json"

    run_diagnose(
        holdings_path=Path("examples/current_holdings.csv"),
        rules_path=Path("config/portfolio_rules.v1.yaml"),
        output_path=markdown_output,
        json_output_path=json_output,
    )

    assert markdown_output.exists()
    assert json_output.exists()
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["allocation"]["stock_weight"] == 0.6102
    assert data["allocation"]["etf_weight"] == 0.3451
    assert data["health_score"] == 88
    assert "Technology" in data["summary"]
    action_hints = {warning["action_hint"] for warning in data["warnings"]}
    assert action_hints >= {"avoid_adding_to_sector", "do_not_add_without_review"}


def test_cli_normalize_writes_internal_holdings_csv(tmp_path):
    raw = tmp_path / "broker_summary.csv"
    raw.write_text("Ticker,MarketValueUSD,WeightPct\nSPY,34510,34.51\nONDS,9840,9.84\n", encoding="utf-8")
    output = tmp_path / "current_holdings.csv"

    run_normalize(input_path=raw, metadata_path=Path("config/ticker_metadata.v1.yaml"), output_path=output)

    holdings = load_holdings_csv(output)
    assert holdings[0].ticker == "SPY"
    assert holdings[0].weight == 0.3451
    assert holdings[1].ticker == "ONDS"
