# IA-DEV-20260602-009 Broker Summary CSV Normalization

## 基本信息

- 版本号：`IA-DEV-20260602-009`
- 日期：2026-06-02
- 类型：code
- 状态：completed
- 所属阶段：P0 — 让诊断更可信、更可复用
- 对应任务：`Next Development Roadmap.md` / Task 2: 支持从原始 broker summary CSV 自动标准化

## 目标

支持从原始 broker summary CSV 自动生成系统内部 holdings CSV，减少手工填写 `name`、`asset_type`、`sector`、`theme`、`risk_level` 的工作。

输入格式：

```csv
Ticker,MarketValueUSD,WeightPct
SPY,31055.11,34.51
...
```

输出格式：

```csv
ticker,name,asset_type,weight,sector,theme,risk_level
SPY,SPDR S&P 500 ETF Trust,etf,0.3451,Index,US Large Cap,normal
...
```

## 完成内容

1. 新增 `normalize_broker_summary_csv(raw_path, metadata_path, output_path)`。
2. 新增 CLI 子命令：

```bash
investment-assistant normalize \
  --input data/portfolio_summary.csv \
  --metadata config/ticker_metadata.v1.yaml \
  --output examples/current_holdings.csv
```

3. 标准化逻辑：
   - 将 `Ticker` 统一转成大写。
   - 将 `WeightPct` 转成 0-1 小数权重，例如 `34.51` → `0.3451`。
   - 从 `ticker_metadata.v1.yaml` 补齐：
     - `name`
     - `asset_type`
     - `sector`
     - `theme`
     - `risk_level`
   - 对真实 broker CSV 中的 `Cash Fund` 自动标准化为 `CASH`。
   - 如果 ticker 缺少 metadata，抛出明确错误，避免静默错分行业 / 风险等级。
4. 新增测试：
   - `test_normalizes_broker_summary_csv_with_metadata`
   - `test_normalizes_broker_cash_fund_to_cash`
   - `test_cli_normalize_writes_internal_holdings_csv`
5. 使用真实 `data/portfolio_summary.csv` 生成：
   - `examples/current_holdings.csv`
6. 用标准化后的 holdings CSV 成功生成诊断报告：
   - `reports/current-normalized-portfolio-health-report.md`

## 涉及文件

- `investment-assistant/src/investment_assistant/portfolio.py`
- `investment-assistant/src/investment_assistant/cli.py`
- `investment-assistant/tests/test_portfolio.py`
- `investment-assistant/tests/test_report_cli.py`
- `investment-assistant/examples/current_holdings.csv`
- `investment-assistant/reports/current-normalized-portfolio-health-report.md`
- `Next Development Roadmap.md`

## TDD 记录

### RED 1 — portfolio 标准化函数

命令：

```bash
uv run pytest tests/test_portfolio.py::test_normalizes_broker_summary_csv_with_metadata -v
```

结果：

```text
ImportError: cannot import name 'normalize_broker_summary_csv' from 'investment_assistant.portfolio'
```

说明：测试先失败，原因符合预期：标准化函数尚不存在。

### RED 2 — CLI normalize 入口

命令：

```bash
uv run pytest tests/test_report_cli.py::test_cli_normalize_writes_internal_holdings_csv -v
```

结果：

```text
ImportError: cannot import name 'run_normalize' from 'investment_assistant.cli'
```

说明：CLI 包装函数尚不存在。

### RED 3 — 真实 broker 的 Cash Fund

第一次真实 CLI 验证暴露出 broker CSV 中现金行是 `Cash Fund`，不是 `CASH`。

命令：

```bash
uv run investment-assistant normalize --input data/portfolio_summary.csv --metadata config/ticker_metadata.v1.yaml --output examples/current_holdings.csv
```

结果：

```text
ValueError: missing ticker metadata for CASH FUND
```

随后补充 failing test：

```bash
uv run pytest tests/test_portfolio.py::test_normalizes_broker_cash_fund_to_cash -v
```

结果：

```text
ValueError: missing ticker metadata for CASH FUND
```

## 验证结果

### 具体测试通过

命令：

```bash
uv run pytest tests/test_portfolio.py::test_normalizes_broker_summary_csv_with_metadata -v
uv run pytest tests/test_report_cli.py::test_cli_normalize_writes_internal_holdings_csv -v
uv run pytest tests/test_portfolio.py::test_normalizes_broker_cash_fund_to_cash -v
```

结果：

```text
test_normalizes_broker_summary_csv_with_metadata PASSED
test_cli_normalize_writes_internal_holdings_csv PASSED
test_normalizes_broker_cash_fund_to_cash PASSED
```

### 全量测试

命令：

```bash
uv run pytest -q
```

结果：

```text
15 passed in 0.29s
```

### 实际 CLI 标准化验证

命令：

```bash
uv run investment-assistant normalize --input data/portfolio_summary.csv --metadata config/ticker_metadata.v1.yaml --output examples/current_holdings.csv
```

结果：

```text
Holdings CSV written to examples/current_holdings.csv
```

生成内容摘要：

```csv
ticker,name,asset_type,weight,sector,theme,risk_level
SPY,SPDR S&P 500 ETF Trust,etf,0.3451,Index,US Large Cap,normal
NOK,Nokia Oyj,stock,0.1704,Technology,Telecom Equipment,normal
GOOGL,Alphabet Inc,stock,0.1342,Communication Services,AI/Advertising,normal
ONDS,Ondas Holdings Inc,stock,0.0984,Technology,Drones/Industrial IoT,high
MRVL,Marvell Technology Inc,stock,0.0664,Technology,Semiconductors/AI Infrastructure,normal
MSFT,Microsoft Corp,stock,0.0502,Technology,AI/Cloud,normal
TSM,Taiwan Semiconductor Manufacturing Co Ltd,stock,0.0487,Technology,Semiconductors/Foundry,normal
HPQ,HP Inc,stock,0.0419,Technology,PCs/Printing,normal
CASH,Cash,cash,0.0444,,,normal
```

### 标准化后诊断验证

命令：

```bash
uv run investment-assistant diagnose --holdings examples/current_holdings.csv --rules config/portfolio_rules.v1.yaml --output reports/current-normalized-portfolio-health-report.md
```

结果：

```text
Report written to reports/current-normalized-portfolio-health-report.md
```

## 下一步

继续 P0 Task 3：增加结构化 `DiagnosisResult`。

目标是把当前诊断从直接生成 Markdown，升级为结构化诊断对象，方便后续 JSON 输出、API、历史快照和 Dashboard 复用。
