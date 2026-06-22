# Agent Workflow

> Investment Assistant 的 Agent 分工、输入、输出和触发时机。

## 1. 总体原则

- Agent 只给建议，不直接交易。
- 每个 Agent 输出必须标注依据、置信度和不确定性。
- Risk Control Agent 拥有否决权。
- Report Agent 负责把复杂结果转换成人能快速 review 的结论。

## 2. Workflow Overview

1. 输入当前持仓、股票池、操作记录、市场状态和知识库资料。
2. Portfolio State Agent 整理组合状态。
3. Fundamental Analysis Agent 分析个股质量。
4. Sector Exposure Agent 检查行业 / 主题集中度。
5. Market Regime Agent 判断市场状态。
6. Portfolio Optimizer Agent 生成目标仓位和调仓建议。
7. Risk Control Agent 审核是否违反规则。
8. Behavior Coach Agent 分析操作行为与纪律。
9. Report Agent 生成可读报告。
10. 用户人工确认。

## 3. Agent Definitions

### 3.1 Portfolio State Agent

- 输入：[[Holding Input Template]]、当前持仓快照。
- 输出：组合摘要、指数 / 个股 / 现金比例、最大持仓、最大行业暴露。
- 触发：每次组合诊断、每周复盘、重大调仓前。

### 3.2 Fundamental Analysis Agent

- 输入：股票代码、财报、估值、新闻、行业信息。
- 输出：质量、成长、估值、风险、综合评分和建议动作。
- 触发：新增股票池标的、持仓基本面变化、周期性复查。

### 3.3 Sector Exposure Agent

- 输入：持仓列表、行业分类、主题标签。
- 输出：行业 / 主题暴露、集中度风险、超限提醒。
- 触发：每次组合诊断和调仓建议前。

### 3.4 Market Regime Agent

- 输入：指数趋势、波动率、市场宽度、宏观风险、新闻摘要。
- 输出：risk-on / neutral / risk-off / high-volatility 标签和理由。
- 触发：每周复盘、市场大幅波动、调仓前。

### 3.5 Portfolio Optimizer Agent

- 输入：组合状态、个股评分、市场状态、[[Portfolio Rules]]。
- 输出：目标仓位、调仓建议、买入 / 卖出优先级。
- 触发：组合超限、新增高质量标的、市场状态变化。

### 3.6 Risk Control Agent

- 输入：调仓建议、[[Investment Constitution v0.1]]、[[Portfolio Rules]]。
- 输出：通过 / 不通过、违反规则列表、修正建议。
- 触发：每次调仓建议后。

### 3.7 Behavior Coach Agent

- 输入：[[Trade Log Template]]、历史操作、市场状态。
- 输出：行为偏差、纪律评分、改进建议。
- 触发：交易后复盘、每周复盘、连续亏损或频繁交易后。

### 3.8 Knowledge Agent

- 输入：[[Knowledge Base Sources]]、投资大师资料、个人笔记。
- 输出：相关原则、历史案例、可引用观点。
- 触发：重大决策前、复盘时、规则修订时。

### 3.9 Report Agent

- 输入：所有 Agent 输出。
- 输出：组合诊断报告、调仓建议报告、每周 / 每月复盘。
- 触发：每次完整 workflow 结束。

## 4. 标准输出格式

每次完整诊断应输出：

- 组合状态摘要。
- 主要风险。
- 违反规则项。
- 建议动作。
- 不建议做的动作。
- 需要人工确认的问题。
- 下一步数据需求。

## 5. MVP 阶段优先级

MVP 先实现：

1. Portfolio State Agent
2. Sector Exposure Agent
3. Portfolio Optimizer Agent
4. Risk Control Agent
5. Report Agent

后续再加入：

- Fundamental Analysis Agent
- Market Regime Agent
- Behavior Coach Agent
- Knowledge Agent
