# Portfolio Expert / Investment Assistant

Portfolio Expert 是一个本地优先的个人投资组合诊断 MVP。它读取持仓 CSV 和组合规则 YAML，生成组合健康报告，并输出结构化 JSON，供后续历史快照、周报、API 和 Dashboard 复用。

> 重要提示：本项目只提供投资组合诊断和复核建议，不自动交易，也不构成财务顾问意见。所有买入、卖出、调仓动作都需要人工确认。

## 当前能力

已完成的 MVP 闭环：

```text
broker CSV → 标准化 holdings CSV → 规则诊断 → Markdown 报告 + JSON 输出
```

当前支持：

- 从 broker summary CSV 标准化持仓数据。
- 通过 YAML 配置维护 ticker metadata 和组合规则。
- 计算 ETF、个股、现金、其他资产占比。
- 检查指数仓位、个股总仓位、单票仓位、高风险单票、行业 / 主题集中度。
- 输出 human-readable Markdown 健康报告。
- 输出 machine-readable JSON 诊断结果。
- 对 warning 标记 `info` / `warning` / `critical` 严重程度。
- 输出稳定的 `action_hint`，例如：
  - `do_not_add_without_review`
  - `avoid_adding_to_sector`
  - `review_trim_to_limit`

## 仓库结构

```text
.
├── Investment Assistant - Index.md       # Obsidian 项目索引
├── Investment Assistant MVP PRD.md       # MVP PRD
├── Next Development Roadmap.md           # 下一阶段路线图
├── Development Logs/                     # 每个开发节点的版本日志
├── Portfolio Rules.md                    # 人类可读组合规则
├── Config/portfolio_rules.v1.yaml        # Obsidian 侧规则配置备份
└── investment-assistant/                 # Python CLI MVP
    ├── config/
    │   ├── portfolio_rules.v1.yaml
    │   └── ticker_metadata.v1.yaml
    ├── data/
    │   └── portfolio_summary.csv
    ├── examples/
    │   ├── current_holdings.csv
    │   └── holdings.sample.csv
    ├── src/investment_assistant/
    │   ├── cli.py
    │   ├── diagnosis.py
    │   ├── portfolio.py
    │   ├── report.py
    │   └── rules.py
    └── tests/
```

## 环境要求

- Python 3.11+
- uv

项目依赖定义在：

```text
investment-assistant/pyproject.toml
```

主要依赖：

- Pydantic
- Pandas
- PyYAML
- pytest

## 快速开始

进入 Python MVP 目录：

```bash
cd investment-assistant
```

安装 / 同步依赖：

```bash
uv sync --extra dev
```

如果本地 console script 出现 `ModuleNotFoundError: No module named 'investment_assistant'`，可以重新安装当前包：

```bash
uv pip install --python .venv/bin/python --reinstall .
```

## 使用方式

### 1. 标准化 broker summary CSV

输入示例：

```text
Ticker,MarketValueUSD,WeightPct
SPY,31055.11,34.51
NOK,15338.49,17.04
Cash Fund,4000.0,4.44
```

运行：

```bash
uv run investment-assistant normalize \
  --input data/portfolio_summary.csv \
  --metadata config/ticker_metadata.v1.yaml \
  --output examples/current_holdings.csv
```

输出：

```text
Holdings CSV written to examples/current_holdings.csv
```

### 2. 生成组合健康报告和 JSON 诊断结果

```bash
uv run investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-portfolio-health-report.md \
  --json-output reports/current-portfolio-health-report.json
```

输出：

```text
Report written to reports/current-portfolio-health-report.md
JSON report written to reports/current-portfolio-health-report.json
```

### 3. 可选市场状态

`diagnose` 支持：

```bash
--market-regime neutral
--market-regime risk_off
--market-regime risk_on
```

默认是：

```bash
--market-regime neutral
```

## JSON 输出格式

JSON 输出包含：

```json
{
  "allocation": {
    "etf_weight": 0.3451,
    "stock_weight": 0.6102,
    "cash_weight": 0.0444,
    "other_weight": 0.0,
    "total_weight": 0.9997
  },
  "warnings": [
    {
      "category": "position",
      "message": "ONDS 高风险单只个股仓位 9.8% 接近上限 10.0%",
      "current_weight": 0.0984,
      "limit": 0.1,
      "severity": "info",
      "action_hint": "do_not_add_without_review",
      "metadata": {
        "ticker": "ONDS"
      }
    }
  ],
  "health_score": 88,
  "summary": "..."
}
```

## 测试

在 `investment-assistant/` 目录运行：

```bash
uv run pytest -q
```

当前基线：

```text
21 passed
```

## 开发日志规则

本项目使用开发日志记录每个明确功能点 / 文档里程碑。

日志目录：

```text
Development Logs/
```

版本号格式：

```text
IA-DEV-YYYYMMDD-NNN
```

每次完成一个功能点后，应：

1. 新增一条开发日志。
2. 更新 `Development Logs/Development Log - Index.md`。
3. 更新 `Next Development Roadmap.md` 中对应任务状态。

## 当前路线图

当前 P0 Task 1-5 已完成，MVP 已具备最小 CLI 使用闭环。

下一步计划：

1. SQLite 保存历史快照。
2. `snapshot` / `history` CLI 命令。
3. 再平衡建议生成器 v0。
4. FastAPI diagnose endpoint。

详见：

```text
Next Development Roadmap.md
```

## Git / 生成文件说明

以下内容默认不提交：

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `investment-assistant/reports/*`
- 本地 SQLite / DB 文件
- macOS / iCloud 临时文件

`reports/.gitkeep` 会保留目录结构，但实际报告文件为本地生成物。
