# IA-DEV-20260622-001 JSON Diagnostic Output

## 元信息

- 版本号：`IA-DEV-20260622-001`
- 日期：2026-06-22
- 类型：Feature / CLI output
- 状态：Completed
- Roadmap 对应：P0 Task 5：增加 JSON 输出

## 目标

让 `investment-assistant diagnose` 在生成 Markdown 组合健康报告的同时，也能通过 `--json-output` 输出结构化 JSON 诊断结果，方便后续 API、Dashboard、历史快照和周报复用。

## 完成内容

- `run_diagnose(...)` 新增可选参数：`json_output_path: Path | None = None`。
- CLI `diagnose` 子命令新增参数：`--json-output`。
- 诊断流程改为在 CLI 层复用 `diagnose_portfolio(...)` 的结构化 `DiagnosisResult`：
  - Markdown 使用 `render_health_report(result)` 生成。
  - JSON 使用 `result.model_dump_json(indent=2)` 输出。
- CLI 成功生成 JSON 时输出：`JSON report written to ...`。
- 新增测试覆盖 JSON 文件写入和核心字段：
  - `allocation`
  - `warnings`
  - `health_score`
  - `summary`
  - `action_hint`

## 涉及文件

- `investment-assistant/src/investment_assistant/cli.py`
- `investment-assistant/tests/test_report_cli.py`
- `investment-assistant/reports/current-portfolio-health-report.md`
- `investment-assistant/reports/current-portfolio-health-report.json`
- `Next Development Roadmap.md`
- `Development Logs/Development Log - Index.md`

## TDD 记录

### RED

先新增测试：

```bash
uv run pytest tests/test_report_cli.py::test_cli_diagnose_writes_json_output -v
```

失败符合预期：

```text
FAILED tests/test_report_cli.py::test_cli_diagnose_writes_json_output
TypeError: run_diagnose() got an unexpected keyword argument 'json_output_path'
```

### GREEN / 聚焦测试

实现后运行：

```bash
uv run pytest tests/test_report_cli.py::test_cli_diagnose_writes_json_output -v
```

结果：

```text
tests/test_report_cli.py::test_cli_diagnose_writes_json_output PASSED
1 passed in 0.27s
```

### CLI 相关测试

```bash
uv run pytest tests/test_report_cli.py -q
```

结果：

```text
4 passed in 0.26s
```

### 全量测试

```bash
uv run pytest -q
```

结果：

```text
21 passed in 0.30s
```

## 真实 CLI 验证

首次直接运行 console script 时遇到本地 venv 安装状态问题：

```text
ModuleNotFoundError: No module named 'investment_assistant'
```

按项目验证流程重新安装当前包：

```bash
uv pip install --python .venv/bin/python --reinstall .
```

随后确认 help 中已有 `--json-output`：

```bash
uv run investment-assistant diagnose --help
```

关键输出：

```text
--json-output JSON_OUTPUT
```

使用真实当前持仓生成 Markdown + JSON：

```bash
uv run investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-portfolio-health-report.md \
  --json-output reports/current-portfolio-health-report.json
```

结果：

```text
Report written to reports/current-portfolio-health-report.md
JSON report written to reports/current-portfolio-health-report.json
```

## 生成结果读回确认

Markdown 报告包含：

```text
健康分数：88
[info] ONDS 高风险单只个股仓位 9.8% 接近上限 10.0%；建议动作：do_not_add_without_review
[warning] 行业 Technology 暴露 47.6% 高于上限 40.0%；建议动作：avoid_adding_to_sector
```

JSON 报告核心内容：

```json
{
  "allocation": {
    "etf_weight": 0.3451,
    "stock_weight": 0.6102,
    "cash_weight": 0.0444,
    "other_weight": 0.0,
    "total_weight": 0.9997
  },
  "health_score": 88,
  "warnings": [
    {
      "category": "position",
      "severity": "info",
      "action_hint": "do_not_add_without_review"
    },
    {
      "category": "sector",
      "severity": "warning",
      "action_hint": "avoid_adding_to_sector"
    }
  ]
}
```

## Roadmap 更新

- `Next Development Roadmap.md` 中 Task 5 已标记完成：`IA-DEV-20260622-001`。
- Current sprint 已更新为 P0 Task 1-5 已完成；下一轮建议进入 Task 6-7。

## 下一步

进入：P0 Task 6：SQLite 保存历史快照。

目标：每次诊断可以保存快照，后续支持趋势、周报和复盘。
