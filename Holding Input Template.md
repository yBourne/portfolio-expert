# Holding Input Template

> 当前持仓输入模板。用于让 Investment Assistant 读取组合状态、识别集中度和生成调仓建议。

## 使用方式

每次需要组合诊断时，复制本模板，创建一份日期版本，例如：

`Holdings/2026-06-01 Holding Snapshot.md`

## 1. Snapshot Metadata

- 日期：YYYY-MM-DD
- 账户 / 组合名称：
- 总资产：
- 现金金额：
- 现金比例：
- 指数 / ETF 总比例：
- 个股总比例：
- 备注：

## 2. Portfolio Summary

- 当前市场状态：risk-on / neutral / risk-off / high-volatility / unknown
- 本次诊断目的：例：例行周检 / 新增标的 / 市场大跌 / 仓位超限
- 当前最大风险：
- 当前最想解决的问题：

## 3. Holdings

为每个持仓复制一段：

### Holding: TICKER / Name

- 标的代码：
- 标的名称：
- 类型：ETF / 个股 / 现金 / 其他
- 行业 / 主题：
- 当前仓位比例：
- 当前市值：
- 成本：
- 未实现盈亏：
- 持有时间：
- 当前投资逻辑：
- 买入理由是否仍然成立：yes / no / unclear
- 风险点：
- 希望 Agent 重点检查：

## 4. Watchlist / Candidate Stocks

### Candidate: TICKER / Name

- 标的代码：
- 标的名称：
- 行业 / 主题：
- 加入原因：
- 关注点：
- 可能替代的现有持仓：
- 需要基本面分析：yes / no

## 5. Questions for Agent

- 当前组合是否过于集中？
- 是否有持仓超过单票 / 行业上限？
- 是否需要提高或降低指数仓位？
- 哪些标的应进入减仓候选？
- 哪些候选股值得进一步研究？
- 本次不应做什么？
