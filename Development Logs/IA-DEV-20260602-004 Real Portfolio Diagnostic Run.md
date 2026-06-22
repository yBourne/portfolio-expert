# IA-DEV-20260602-004 Real Portfolio Diagnostic Run

- 版本号：IA-DEV-20260602-004
- 日期：2026-06-02
- 类型：data / diagnostic run / report
- 状态：completed

## 目标

使用用户上传的真实 `portfolio_summary.csv`，跑通 MVP 的真实组合诊断流程，并保存报告到 Obsidian。

## 输入数据

用户上传文件：`portfolio_summary.csv`

原始列：

- `Ticker`
- `MarketValueUSD`
- `WeightPct`

主要持仓：

- SPY：34.51%
- NOK：17.04%
- GOOGL：13.42%
- ONDS：9.84%
- MRVL：6.64%
- MSFT：5.02%
- TSM：4.87%
- HPQ：4.19%
- Cash Fund：4.44%

## 完成内容

- 将上传文件复制到代码项目数据目录。
- 临时手工补充 ticker metadata。
- 将 broker summary CSV 标准化成 MVP 可读取的 holdings CSV。
- 运行真实组合诊断。
- 保存 Markdown 报告到代码项目。
- 保存复盘报告到 Obsidian `Reviews/`。

## 涉及文件

- `investment-assistant/data/portfolio_summary.csv`
- `investment-assistant/examples/current_holdings.csv`
- `investment-assistant/reports/current-portfolio-health-report.md`
- `Reviews/2026-06-02 Portfolio Health Report.md`

## 诊断结果

- 指数 / ETF：34.5%，在 30%-50% 范围内。
- 个股：61.0%，低于 70% 上限。
- 现金：4.4%，高于 0% 下限。
- 最大单只个股：NOK 17.04%，低于 25% 单票上限。
- ONDS 暂按高风险个股处理：9.84%，接近但未超过 10% 高风险单票上限。
- 唯一硬性超限：Technology 行业暴露 47.6%，超过 40% 上限。

## 验证结果

实际运行：

```bash
uv sync --all-extras
uv run pytest -q
uv run investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-portfolio-health-report.md
```

测试结果：

```text
10 passed in 0.25s
```

CLI 输出：

```text
Report written to reports/current-portfolio-health-report.md
```

## 下一步

把 ticker metadata 和 broker CSV 标准化从临时脚本变成正式功能。
