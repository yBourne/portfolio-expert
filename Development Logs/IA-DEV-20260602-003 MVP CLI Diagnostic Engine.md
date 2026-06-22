# IA-DEV-20260602-003 MVP CLI Diagnostic Engine

- 版本号：IA-DEV-20260602-003
- 日期：2026-06-02
- 类型：code / MVP / CLI
- 状态：completed

## 目标

创建第一个可运行的 MVP 最小闭环：CSV 持仓导入 → 规则读取 → 组合诊断 → Markdown 健康报告。

## 完成内容

- 创建 `investment-assistant` Python 项目。
- 配置 `pyproject.toml`、pytest、editable package。
- 实现持仓模型：ETF / 个股 / 现金 / 其他。
- 实现规则模型与 YAML 加载。
- 实现资产配置计算。
- 实现规则检查：
  - 指数 / ETF 区间。
  - 个股总仓位上限。
  - 单票上限。
  - 高风险单票上限。
  - 行业 / 主题集中度上限。
- 实现 Markdown 健康报告生成。
- 实现 CLI：`investment-assistant diagnose`。
- 创建 sample holdings 和 sample report。

## 涉及文件

- `investment-assistant/pyproject.toml`
- `investment-assistant/config/portfolio_rules.v1.yaml`
- `investment-assistant/examples/holdings.sample.csv`
- `investment-assistant/src/investment_assistant/__init__.py`
- `investment-assistant/src/investment_assistant/portfolio.py`
- `investment-assistant/src/investment_assistant/rules.py`
- `investment-assistant/src/investment_assistant/report.py`
- `investment-assistant/src/investment_assistant/cli.py`
- `investment-assistant/tests/test_portfolio.py`
- `investment-assistant/tests/test_rules.py`
- `investment-assistant/tests/test_report_cli.py`
- `investment-assistant/.gitignore`

## 验证结果

实际运行：

```bash
uv run pytest -q
```

结果：

```text
10 passed
```

实际运行 CLI：

```bash
uv run investment-assistant diagnose \
  --holdings examples/holdings.sample.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/portfolio-health-report.md
```

结果：

```text
Report written to reports/portfolio-health-report.md
```

## 注意事项

- 曾遇到 editable package 在 `.venv` 中未正确可见的问题，已通过重新同步 / 重装项目包解决。
- 当前 CLI 已可运行，但后续需要把原始 broker CSV 标准化流程产品化。

## 下一步

导入真实持仓 CSV，跑第一版真实组合诊断报告。
