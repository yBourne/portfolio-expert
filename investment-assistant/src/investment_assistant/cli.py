from __future__ import annotations

import argparse
from pathlib import Path

from investment_assistant.diagnosis import diagnose_portfolio
from investment_assistant.portfolio import load_holdings_csv, normalize_broker_summary_csv
from investment_assistant.report import render_health_report
from investment_assistant.rules import load_portfolio_rules


def run_diagnose(
    holdings_path: Path,
    rules_path: Path,
    output_path: Path,
    market_regime: str = "neutral",
    json_output_path: Path | None = None,
) -> Path:
    holdings = load_holdings_csv(holdings_path)
    rules = load_portfolio_rules(rules_path)
    result = diagnose_portfolio(holdings, rules, market_regime=market_regime)
    report = render_health_report(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    if json_output_path is not None:
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        json_output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def run_normalize(input_path: Path, metadata_path: Path, output_path: Path) -> Path:
    return normalize_broker_summary_csv(raw_path=input_path, metadata_path=metadata_path, output_path=output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="investment-assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose = subparsers.add_parser("diagnose", help="Generate a portfolio health report from holdings CSV")
    diagnose.add_argument("--holdings", required=True, type=Path)
    diagnose.add_argument("--rules", required=True, type=Path)
    diagnose.add_argument("--output", required=True, type=Path)
    diagnose.add_argument("--json-output", type=Path)
    diagnose.add_argument("--market-regime", default="neutral", choices=["neutral", "risk_off", "risk_on"])

    normalize = subparsers.add_parser("normalize", help="Convert broker summary CSV into internal holdings CSV")
    normalize.add_argument("--input", required=True, type=Path)
    normalize.add_argument("--metadata", required=True, type=Path)
    normalize.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "diagnose":
        output = run_diagnose(args.holdings, args.rules, args.output, args.market_regime, args.json_output)
        print(f"Report written to {output}")
        if args.json_output is not None:
            print(f"JSON report written to {args.json_output}")
    if args.command == "normalize":
        output = run_normalize(args.input, args.metadata, args.output)
        print(f"Holdings CSV written to {output}")


if __name__ == "__main__":
    main()
