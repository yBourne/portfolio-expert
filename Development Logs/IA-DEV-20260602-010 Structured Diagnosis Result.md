# IA-DEV-20260602-010 Structured Diagnosis Result

## 基本信息

- 版本号：`IA-DEV-20260602-010`
- 日期：2026-06-02
- 类型：code
- 状态：completed
- 所属阶段：P0 — 让诊断更可信、更可复用
- 对应任务：`Next Development Roadmap.md` / Task 3: 增加结构化 `DiagnosisResult`

## 目标

把组合诊断从“直接拼 Markdown”升级为结构化结果对象，让诊断结果可以被 JSON、API、历史快照和 Dashboard 复用。

## 完成内容

1. 新增 `investment_assistant.diagnosis` 模块。
2. 新增结构化模型：
   - `RuleWarning`
   - `DiagnosisResult`
3. 新增 `diagnose_portfolio(holdings, rules, market_regime="neutral")`。
4. 将原来散落在 `report.py` 里的诊断流程迁移到 `diagnose_portfolio`：
   - `calculate_asset_allocation`
   - `check_allocation_limits`
   - `check_single_position_limits`
   - `check_sector_theme_limits`
5. `report.py` 改为渲染结构化 `DiagnosisResult`：
   - 新增 `render_health_report(result)`。
   - 保留 `generate_health_report(holdings, rules, market_regime)` 兼容旧调用。
6. 报告中新增 `健康分数` 字段。
7. 新增测试：
   - `test_diagnose_portfolio_returns_structured_result`
   - `test_diagnosis_result_can_be_serialized_to_json`
8. 使用真实标准化持仓数据验证结构化诊断和 Markdown 报告。

## 涉及文件

- `investment-assistant/src/investment_assistant/diagnosis.py`
- `investment-assistant/src/investment_assistant/report.py`
- `investment-assistant/tests/test_diagnosis.py`
- `investment-assistant/reports/current-structured-diagnosis-report.md`
- `Next Development Roadmap.md`

## TDD 记录

### RED

命令：

```bash
uv run pytest tests/test_diagnosis.py::test_diagnose_portfolio_returns_structured_result -v
```

结果：

```text
ModuleNotFoundError: No module named 'investment_assistant.diagnosis'
```

说明：测试先失败，原因符合预期：`diagnosis.py` 尚不存在。

### GREEN

命令：

```bash
uv run pytest tests/test_diagnosis.py -v
```

结果：

```text
tests/test_diagnosis.py::test_diagnose_portfolio_returns_structured_result PASSED
tests/test_diagnosis.py::test_diagnosis_result_can_be_serialized_to_json PASSED
2 passed in 1.69s
```

报告渲染兼容性测试：

```bash
uv run pytest tests/test_report_cli.py::test_generates_health_report_markdown -v
```

结果：

```text
tests/test_report_cli.py::test_generates_health_report_markdown PASSED
1 passed in 0.26s
```

## 完整验证

### 全量测试

命令：

```bash
uv run pytest -q
```

结果：

```text
17 passed in 0.29s
```

### 实际 CLI 诊断验证

先重新安装包以修复 console script import 环境：

```bash
uv pip install --python .venv/bin/python --reinstall .
```

然后运行：

```bash
uv run investment-assistant diagnose --holdings examples/current_holdings.csv --rules config/portfolio_rules.v1.yaml --output reports/current-structured-diagnosis-report.md
```

结果：

```text
Report written to reports/current-structured-diagnosis-report.md
```

报告摘要：

```text
指数 / ETF 仓位：34.5%
个股仓位：61.0%
现金比例：4.4%
已录入权重合计：100.0%
健康分数：90
行业 Technology 暴露 47.6% 高于上限 40.0%
```

### 结构化 JSON 验证

命令：

```bash
PYTHONPATH=src uv run python - <<'PY'
from pathlib import Path
from investment_assistant.diagnosis import diagnose_portfolio
from investment_assistant.portfolio import load_holdings_csv
from investment_assistant.rules import load_portfolio_rules
holdings = load_holdings_csv(Path('examples/current_holdings.csv'))
rules = load_portfolio_rules(Path('config/portfolio_rules.v1.yaml'))
result = diagnose_portfolio(holdings, rules)
print(result.model_dump_json(indent=2))
PY
```

结果：

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
      "category": "sector",
      "message": "行业 Technology 暴露 47.6% 高于上限 40.0%",
      "current_weight": 0.47600000000000003,
      "limit": 0.4,
      "severity": "warning",
      "metadata": {
        "kind": "sector",
        "name": "Technology"
      }
    }
  ],
  "health_score": 90,
  "summary": "行业 Technology 暴露 47.6% 高于上限 40.0%"
}
```

## 注意事项

- 当前 `severity` 先统一为 `warning`，用于建立结构化字段。
- 细分 `info / warning / critical` 和 `action_hint` 会在下一步 P0 Task 4 中完成。
- 当前健康分数是基础版本：`100 - 10 * warning_count`，后续可以根据 severity 加权。

## 下一步

继续 P0 Task 4：增加 warning severity 和 action hints。

目标是让风险提示不只说明“哪里超限”，还给出严重程度和建议动作，例如：

- `info`：接近上限但未超限。
- `warning`：轻微超限。
- `critical`：明显超限。
- `action_hint`：`avoid_adding_to_sector` / `review_trim_to_limit` / `do_not_add_without_review`。
