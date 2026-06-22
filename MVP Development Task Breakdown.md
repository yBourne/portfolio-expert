# MVP Development Task Breakdown

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 把 Investment Assistant 从文档阶段推进到可运行的 MVP：导入持仓、读取规则、计算组合风险、输出第一版组合健康报告。

**Architecture:** MVP 先采用本地优先架构：CSV / Markdown 输入 → Python/FastAPI 规则与诊断层 → SQLite 存储 → Next.js Dashboard。第一阶段先做 CLI + API 的最小闭环，前端可在数据结构稳定后接入。

**Tech Stack:** Python 3.11、FastAPI、SQLite、Pydantic、pytest、Pandas；前端建议 Next.js / React；知识库继续使用 Obsidian Markdown。

---

## Phase 0：项目落地准备

### Task 1: 创建 MVP 代码仓库结构

**Objective:** 建立最小可运行项目结构，后续所有实现都有明确路径。

**Files:**
- Create: `investment-assistant/pyproject.toml`
- Create: `investment-assistant/src/investment_assistant/__init__.py`
- Create: `investment-assistant/src/investment_assistant/rules.py`
- Create: `investment-assistant/src/investment_assistant/portfolio.py`
- Create: `investment-assistant/src/investment_assistant/report.py`
- Create: `investment-assistant/tests/test_rules.py`
- Create: `investment-assistant/tests/test_portfolio.py`

**Steps:**
1. 初始化 Python package。
2. 配置 pytest。
3. 保持首版依赖最小：`pydantic`, `pandas`, `pytest`, `fastapi`, `uvicorn`。
4. 运行 `pytest`，确认空测试环境可执行。

**Verification:**
- `pytest` 可运行。
- `python -c "import investment_assistant"` 成功。

---

## Phase 1：规则配置固化

### Task 2: 固化 portfolio_rules.v1.yaml

**Objective:** 将已确认仓位规则变成机器可读配置。

**Files:**
- Create: `investment-assistant/config/portfolio_rules.v1.yaml`
- Test: `investment-assistant/tests/test_rules.py`

**Rules:**
```yaml
portfolio_rules:
  target_index_weight:
    neutral: [0.30, 0.50]
    risk_off: [0.40, 0.50]
    risk_on: [0.30, 0.40]
  max_stock_weight: 0.70
  max_single_stock_weight: 0.25
  max_high_risk_single_stock_weight: 0.10
  max_sector_weight: 0.40
  max_theme_weight: 0.40
  min_cash_weight: 0.00
  max_turnover_per_rebalance: 0.15
  review_frequency: weekly
  stock_score_thresholds:
    add_candidate: 75
    hold: 60
    reduce: 45
    remove: 35
```

**Steps:**
1. 写 failing test：加载 YAML 后 `max_single_stock_weight == 0.25`。
2. 实现 `load_portfolio_rules(path)`。
3. 用 Pydantic model 校验每个比例在 `[0, 1]`。
4. 运行测试并修复。

**Verification:**
- 配置能被加载。
- 规则字段齐全。
- 百分比值均为 0-1 的小数。

---

## Phase 2：持仓输入与标准化

### Task 3: 定义 Holding 数据模型

**Objective:** 系统能够表示单条持仓，并区分 ETF / 个股 / 现金 / 其他。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/portfolio.py`
- Test: `investment-assistant/tests/test_portfolio.py`

**Fields:**
- `ticker: str`
- `name: str`
- `asset_type: enum[etf, stock, cash, other]`
- `weight: float`
- `sector: str | None`
- `theme: str | None`
- `risk_level: enum[normal, high]`

**Steps:**
1. 写 failing test：正常持仓可创建。
2. 写 failing test：`weight < 0` 或 `weight > 1` 报错。
3. 实现 Pydantic model。
4. 运行测试。

**Verification:**
- 权重边界被校验。
- 高风险个股能被标记。

### Task 4: 支持 CSV 持仓导入

**Objective:** 从手工 CSV 读取当前组合。

**Files:**
- Create: `investment-assistant/examples/holdings.sample.csv`
- Modify: `investment-assistant/src/investment_assistant/portfolio.py`
- Test: `investment-assistant/tests/test_portfolio.py`

**CSV columns:**
```csv
ticker,name,asset_type,weight,sector,theme,risk_level
VOO,Vanguard S&P 500 ETF,etf,0.30,Index,US Large Cap,normal
AAPL,Apple Inc,stock,0.10,Technology,AI/Consumer,normal
CASH,Cash,cash,0.05,,,normal
```

**Steps:**
1. 写 failing test：sample CSV 导入 3 条记录。
2. 实现 `load_holdings_csv(path)`。
3. 校验总权重不应明显超过 100%。
4. 运行测试。

**Verification:**
- CSV 能导入为 Holding list。
- 缺失可选字段不导致失败。

---

## Phase 3：组合诊断引擎

### Task 5: 计算组合基础暴露

**Objective:** 计算指数 / ETF、个股、现金、其他的总权重。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/portfolio.py`
- Test: `investment-assistant/tests/test_portfolio.py`

**Steps:**
1. 写 failing test：给定 holdings 后 ETF 权重为 0.30、个股为 0.10、现金为 0.05。
2. 实现 `calculate_asset_allocation(holdings)`。
3. 运行测试。

**Verification:**
- 输出包含 `etf_weight`, `stock_weight`, `cash_weight`, `other_weight`。

### Task 6: 检查单票和高风险单票上限

**Objective:** 找出超过 25% 的单只个股，以及超过 10% 的高风险个股。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/rules.py`
- Test: `investment-assistant/tests/test_rules.py`

**Steps:**
1. 写 failing test：普通个股 26% 被标记。
2. 写 failing test：高风险个股 11% 被标记。
3. 实现 `check_single_position_limits(holdings, rules)`。
4. 运行测试。

**Verification:**
- 返回 warning list，包含 ticker、当前权重、上限、原因。

### Task 7: 检查行业 / 主题集中度

**Objective:** 找出超过 40% 的行业或主题暴露。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/rules.py`
- Test: `investment-assistant/tests/test_rules.py`

**Steps:**
1. 写 failing test：Technology 合计 41% 被标记。
2. 写 failing test：AI 主题合计 41% 被标记。
3. 实现 `check_sector_theme_limits(holdings, rules)`。
4. 运行测试。

**Verification:**
- warning list 能区分 `sector` 和 `theme`。

### Task 8: 检查指数 / 个股 / 现金约束

**Objective:** 根据已确认规则检查指数是否在 30%-50%，个股是否不超过 70%，现金是否不为负。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/rules.py`
- Test: `investment-assistant/tests/test_rules.py`

**Steps:**
1. 写 failing test：ETF 29% 触发 warning。
2. 写 failing test：ETF 51% 触发 warning。
3. 写 failing test：个股 71% 触发 warning。
4. 实现 `check_allocation_limits(allocation, rules)`。
5. 运行测试。

**Verification:**
- 每个超限项有明确解释。

---

## Phase 4：第一版报告

### Task 9: 生成组合健康报告 Markdown

**Objective:** 输出可复制进 Obsidian 的组合诊断报告。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/report.py`
- Test: `investment-assistant/tests/test_report.py`

**Report sections:**
1. 组合摘要。
2. 规则检查结果。
3. 主要风险。
4. 建议动作：观察 / 调整 / 需要人工确认。
5. 依据与风险提示。

**Steps:**
1. 写 failing test：报告包含“组合摘要”和“规则检查结果”。
2. 实现 `generate_health_report(holdings, rules)`。
3. 对无 warning 的组合输出“暂无硬性超限”。
4. 运行测试。

**Verification:**
- Markdown 可读。
- 所有建议都带规则依据。

### Task 10: 提供 CLI 最小闭环

**Objective:** 用一条命令从 CSV 生成报告。

**Files:**
- Create: `investment-assistant/src/investment_assistant/cli.py`
- Modify: `investment-assistant/pyproject.toml`
- Test: `investment-assistant/tests/test_cli.py`

**Command:**
```bash
investment-assistant diagnose \
  --holdings examples/holdings.sample.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/portfolio-health-report.md
```

**Steps:**
1. 写 failing CLI test。
2. 实现 argparse / typer CLI。
3. 运行命令生成报告。
4. 验证输出文件存在且包含规则检查。

**Verification:**
- 一条命令完成 CSV → 规则诊断 → Markdown 报告。

---

## Phase 5：MVP 后续扩展

### Task 11: FastAPI 包装诊断接口

**Objective:** 为未来前端 Dashboard 提供 API。

**Endpoint:**
- `POST /diagnose`：输入 holdings JSON，返回 allocation、warnings、report_markdown。

**Verification:**
- `pytest` 覆盖 API。
- `uvicorn` 本地启动后 `/docs` 可访问。

### Task 12: Dashboard 页面接入

**Objective:** 展示组合摘要、集中度风险和建议动作。

**Pages:**
- Dashboard 首页。
- Portfolio 页面。
- Rebalance 建议页面。

**Verification:**
- 能用 sample holdings 展示所有核心指标。

---

## 当前最小闭环验收

MVP 第一个可交付版本只需要满足：

1. 能读取 `portfolio_rules.v1.yaml`。
2. 能导入一份持仓 CSV。
3. 能计算 ETF / 个股 / 现金比例。
4. 能识别单票、高风险单票、行业 / 主题、个股总仓位、指数仓位超限。
5. 能输出一份 Markdown 组合健康报告。
6. 不自动交易；所有建议必须等待人工确认。
