# IA-DEV-20260602-002 Portfolio Rules Review

- 版本号：IA-DEV-20260602-002
- 日期：2026-06-02
- 类型：rules / documentation / config
- 状态：completed

## 目标

根据用户确认的真实投资偏好，替换初版占位仓位规则，并同步到所有核心文档和机器可读配置。

## 用户确认的规则

- 指数 / ETF：30% - 50%
- 个股总仓位上限：70%
- 单只个股上限：25%
- 高风险单只个股上限：10%
- 单一行业 / 主题上限：40%
- 现金最低比例：0%
- 单次调仓上限：15%
- 大额调仓继续需要 48 小时冷静期
- MVP 继续坚持“只给建议，不自动交易”

## 完成内容

- 更新组合规则为 Reviewed 状态。
- 更新投资宪法默认仓位原则。
- 更新 MVP PRD 中规则表、动态配置逻辑和 YAML 示例。
- 更新项目索引中的已确认决策点。
- 新增机器可读规则配置。

## 涉及文件

- `Portfolio Rules.md`
- `Investment Constitution v0.1.md`
- `Investment Assistant MVP PRD.md`
- `Investment Assistant - Index.md`
- `Config/portfolio_rules.v1.yaml`

## 验证结果

- 搜索旧占位参数，确认相关 Markdown 规则文档中不再残留：
  - 单票 8%
  - 行业 25%
  - 现金 3% / 5%
  - 单次调仓 5%-10% / 10%

## 下一步

基于确认后的规则，创建 MVP 代码仓库，实现 CSV 持仓导入、规则检查和 Markdown 报告输出。
