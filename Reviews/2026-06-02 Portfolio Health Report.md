# 2026-06-02 Portfolio Health Report

> 来源：上传的 `portfolio_summary.csv`。本报告由 Investment Assistant MVP 根据 `portfolio_rules.v1.yaml` 自动生成。

## 输入摘要

- 原始文件：`data/portfolio_summary.csv`
- 标准化持仓：`examples/current_holdings.csv`
- 生成报告：`reports/current-portfolio-health-report.md`

## 组合摘要

- 指数 / ETF 仓位：34.5%
- 个股仓位：61.0%
- 现金比例：4.4%
- 其他资产：0.0%
- 已录入权重合计：100.0%

## 规则检查结果

- ⚠️ 行业 Technology 暴露 47.6% 高于上限 40.0%。

## 主要持仓

- SPY：34.51%，ETF / 指数。
- NOK：17.04%，Technology / Telecom Equipment。
- GOOGL：13.42%，Communication Services / Internet/AI。
- ONDS：9.84%，Technology / Drones/Industrial IoT，暂按高风险个股处理。
- MRVL：6.64%，Technology / Semiconductors。
- MSFT：5.02%，Technology / Software/AI。
- TSM：4.87%，Technology / Semiconductors。
- HPQ：4.19%，Technology / Hardware。
- Cash Fund：4.44%，现金。

## 初步解读

- 指数 / ETF 34.5%，在 30%-50% 目标范围内。
- 个股总仓位 61.0%，低于 70% 上限。
- 最大单只个股为 NOK 17.04%，低于 25% 单票上限。
- ONDS 暂按高风险个股处理，当前 9.84%，接近但未超过 10% 高风险单票上限。
- 当前唯一硬性超限项是 Technology 行业集中度：47.6% > 40%。

## 建议动作

- 不需要因为单票或总个股仓位立即强制调仓。
- 下一次加仓前，优先避免继续增加 Technology 暴露。
- 如果要降风险，优先检查 Technology 内部低 conviction 或高波动持仓，而不是机械卖出指数底仓。
- 所有调仓建议仍需人工确认；大额调仓遵守 48 小时冷静期。

## 依据与风险提示

- 依据：[[Portfolio Rules]] 和 `Config/portfolio_rules.v1.yaml`。
- 本报告不是财务顾问意见，不自动交易。
