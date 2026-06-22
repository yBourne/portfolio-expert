# IA-DEV-20260606-001 Warning Severity and Action Hints

## 基本信息

- 版本号：`IA-DEV-20260606-001`
- 日期：2026-06-06
- 类型：代码开发 / 诊断规则增强
- 状态：已完成
- 对应路线图：P0 Task 4 — 增加 warning severity 和 action hints

## 目标

让每条组合诊断提示不只说明“哪里超限”，还提供：

- `severity`：`info` / `warning` / `critical`
- `action_hint`：给后续 API、Dashboard、周报和人工复核使用的机器可读建议动作

## 完成内容

1. 在规则 warning model 中新增字段：
   - `severity: Literal["info", "warning", "critical"]`
   - `action_hint: str`

2. 增加高风险单票接近上限提示：
   - ONDS 9.84% 接近 10% 高风险单票上限时，生成 `info` 级别提示。
   - 建议动作：`do_not_add_without_review`。

3. 增加单票超限建议动作：
   - 单票超过上限时，建议动作：`review_trim_to_limit`。
   - 单票超过上限 20% 以上时，严重程度升级为 `critical`。

4. 增加行业 / 主题集中度建议动作：
   - 行业超限：`avoid_adding_to_sector`。
   - 主题超限：`avoid_adding_to_theme`。
   - 行业 / 主题超过 50% 时，严重程度升级为 `critical`。

5. 更新结构化诊断结果：
   - `DiagnosisResult.warnings` 现在保留底层规则输出的 `severity` 和 `action_hint`。
   - 健康分数改为按严重程度扣分：`info` 扣 2 分，`warning` 扣 10 分，`critical` 扣 20 分。

6. 更新 Markdown 报告：
   - 规则检查结果显示 `[severity]`。
   - 每条 warning 显示对应 `action_hint`。
   - 建议动作章节补充 action hint 的含义。

## 涉及文件

- `investment-assistant/src/investment_assistant/rules.py`
- `investment-assistant/src/investment_assistant/diagnosis.py`
- `investment-assistant/src/investment_assistant/report.py`
- `investment-assistant/tests/test_rules.py`
- `investment-assistant/tests/test_diagnosis.py`
- `investment-assistant/reports/current-action-hints-report.md`
- `Next Development Roadmap.md`
- `Development Logs/Development Log - Index.md`

## TDD 记录

### RED

先新增聚焦测试并确认失败：

```bash
uv run pytest tests/test_rules.py::test_high_risk_position_near_limit_gets_info_warning -v
```

结果：

```text
tests/test_rules.py::test_high_risk_position_near_limit_gets_info_warning FAILED
E       assert 0 == 1
E        +  where 0 = len([])
```

失败原因符合预期：旧逻辑只在超过上限时返回 warning，不会对接近上限的高风险单票生成 `info` 提示。

### GREEN / 聚焦测试

```bash
uv run pytest tests/test_rules.py::test_high_risk_position_near_limit_gets_info_warning tests/test_rules.py::test_single_position_over_limit_gets_trim_action_hint tests/test_rules.py::test_sector_concentration_warning_gets_avoid_adding_action_hint -v
```

结果：

```text
3 passed in 0.40s
```

### 规则与诊断测试

```bash
uv run pytest tests/test_rules.py tests/test_diagnosis.py -q
```

结果：

```text
10 passed in 0.47s
```

### 全量测试

```bash
uv run pytest -q
```

结果：

```text
20 passed in 0.31s
```

## 真实 CLI / 数据验证

第一次直接运行 console script 时遇到本地 venv console script 包状态问题：

```text
ModuleNotFoundError: No module named 'investment_assistant'
```

按项目验证流程重新安装当前包：

```bash
uv pip install --python .venv/bin/python --reinstall .
```

随后运行真实持仓诊断：

```bash
uv run investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-action-hints-report.md
```

结果：

```text
Report written to reports/current-action-hints-report.md
```

读回报告确认包含：

```text
- ⚠️ [info] ONDS 高风险单只个股仓位 9.8% 接近上限 10.0%；建议动作：`do_not_add_without_review`
- ⚠️ [warning] 行业 Technology 暴露 47.6% 高于上限 40.0%；建议动作：`avoid_adding_to_sector`
```

## 结构化结果验证

真实组合诊断的结构化 warning 输出包含：

```json
[
  {
    "category": "position",
    "message": "ONDS 高风险单只个股仓位 9.8% 接近上限 10.0%",
    "current_weight": 0.0984,
    "limit": 0.1,
    "severity": "info",
    "action_hint": "do_not_add_without_review",
    "metadata": {"ticker": "ONDS"}
  },
  {
    "category": "sector",
    "message": "行业 Technology 暴露 47.6% 高于上限 40.0%",
    "current_weight": 0.47600000000000003,
    "limit": 0.4,
    "severity": "warning",
    "action_hint": "avoid_adding_to_sector",
    "metadata": {"kind": "sector", "name": "Technology"}
  }
]
```

健康分数：`88`。

## 下一步

进入 P0 Task 5：增加 JSON 输出，让 CLI 可以在生成 Markdown 报告的同时输出结构化 JSON 文件。