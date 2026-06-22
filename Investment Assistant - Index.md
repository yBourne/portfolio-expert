# Investment Assistant - Index

> 个人投资助理 / 仓位管理 / 股票池研究 / 投资行为复盘项目索引。

## 项目目标

建立一个面向个人投资者的 AI 投资助理，持续读取持仓、股票池、操作记录、市场状态和投资知识库，帮助做组合诊断、仓位管理、个股研究、调仓建议和投资行为复盘。

核心原则：

- 先建议，后确认；不直接自动交易。
- 先规则，后模型；投资宪法优先于单次模型建议。
- 先复盘，后优化；通过交易日志和周复盘持续改进决策质量。

## 当前阶段

当前处于 **MVP 文档与规则定义阶段**。

已完成：

- PRD + MVP 实施计划。
- 系统架构图 HTML。
- 项目文档迁移到 Obsidian `sync-idea` vault。
- 初版投资宪法、组合规则、输入模板、Agent Workflow 和复盘模板。

下一步：

- 基于模板录入第一份真实持仓快照。
- 补充回撤阈值和再平衡频率。
- 进入 MVP 开发任务拆解。

## 核心文档

- [[Investment Assistant MVP PRD]]：完整 PRD + MVP 实施计划。
- [[Investment Constitution v0.1]]：投资宪法、仓位原则、交易纪律。
- [[Portfolio Rules]]：可执行的组合约束和风险规则。
- [[Agent Workflow]]：各个 Agent 的职责、输入、输出、触发时机。
- [[MVP Development Task Breakdown]]：MVP 开发任务拆解与最小闭环验收。
- [[Next Development Roadmap]]：下一阶段开发路线图与当前 sprint 计划。
- [[Development Log - Index]]：项目开发进度日志与唯一版本号记录。
- 规则配置：`Config/portfolio_rules.v1.yaml`
- 架构图 HTML：`Assets/investment-assistant-architecture.html`

## 输入与模板

- [[Holding Input Template]]：当前持仓输入模板。
- [[Trade Log Template]]：买入、卖出、加减仓和操作复盘模板。
- [[Weekly Investment Review Template]]：每周投资复盘模板。

## 知识库

- [[Knowledge Base Sources]]：巴菲特、芒格、股东信、书摘、NotebookLM 资料来源规划。

## 建议目录结构

```text
Projects/Investment Assistant/
  Investment Assistant - Index.md
  Investment Assistant MVP PRD.md
  Investment Constitution v0.1.md
  Portfolio Rules.md
  Agent Workflow.md
  MVP Development Task Breakdown.md
  Next Development Roadmap.md
  Development Logs/
    Development Log - Index.md
    IA-DEV-YYYYMMDD-NNN *.md
  Holding Input Template.md
  Trade Log Template.md
  Weekly Investment Review Template.md
  Knowledge Base Sources.md
  Config/
    portfolio_rules.v1.yaml
  Assets/
    investment-assistant-architecture.html
  Holdings/
  Trade Logs/
  Reviews/
```

## 已确认决策点

1. 大额调仓继续需要 48 小时冷静期。
2. MVP 继续坚持“只给建议，不自动交易”。
3. 指数 / ETF 目标仓位：30% - 50%。
4. 个股总仓位上限：70%。
5. 单只个股上限：25%。
6. 高风险单只个股上限：10%。
7. 单一行业 / 主题上限：40%。
8. 现金最低比例：0%。
9. 单次调仓上限：组合总资产的 15%。

## 文档维护规则

- 投资策略项目相关文档默认维护在本目录。
- 新增长期规则先写入 [[Investment Constitution v0.1]] 或 [[Portfolio Rules]]。
- 新增持仓数据使用 [[Holding Input Template]]。
- 新增交易记录使用 [[Trade Log Template]]。
- 每周复盘使用 [[Weekly Investment Review Template]]。
