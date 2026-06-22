# Investment Assistant Next Development Roadmap

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 在已完成的 CLI 组合诊断 MVP 基础上，推进到“可持续使用”的个人投资助理：能保存历史快照、生成更有行动价值的建议、提供 API，并为 Dashboard 做好准备。

**Architecture:** 继续保持本地优先。短期用 CSV + YAML + Markdown + SQLite，避免过早接入复杂行情源或券商 API。核心链路是：持仓输入 → 标准化 → 规则诊断 → 风险解释 → 建议动作 → 历史记录 → 周报 / API 输出。

**Tech Stack:** Python 3.11、Pydantic、Pandas、PyYAML、pytest、SQLite、FastAPI、Markdown/Obsidian。前端 Dashboard 暂缓到 API 和数据模型稳定后再做。

---

## 当前状态

已完成并验证：

- `investment-assistant` Python 项目结构。
- `portfolio_rules.v1.yaml` 规则配置。
- CSV 持仓导入。
- ETF / 个股 / 现金 / 其他资产占比计算。
- 单票、高风险单票、行业 / 主题、指数仓位、个股总仓位规则检查。
- Markdown 健康报告生成。
- CLI：`investment-assistant diagnose`。
- 真实持仓 `portfolio_summary.csv` 已跑通。
- JSON 诊断结果输出：CLI 支持 `--json-output`。
- 测试：`uv run pytest -q` 当前 21 passed。

当前真实组合诊断结论：

- 指数 / ETF：34.5%，在 30%-50% 范围内。
- 个股：61.0%，低于 70% 上限。
- 现金：4.4%，高于 0% 下限。
- 唯一硬性超限：Technology 行业暴露 47.6% > 40%。
- ONDS 暂按高风险个股处理，9.84%，接近 10% 上限但未超限。

---

## 下一阶段优先级

### P0：让诊断更可信、更可复用

1. 增加持仓标准化 / 映射配置，避免每次手工补 sector/theme/risk_level。
2. 增加诊断结果结构化 JSON 输出，方便 API / Dashboard / 历史记录使用。
3. 增加超限严重程度和建议动作，不只输出 warning。
4. 增加 SQLite 历史快照，保存每次组合诊断结果。
5. 增加 `snapshot` / `history` CLI 命令。

### P1：让系统开始像“投资助理”

6. 增加再平衡建议生成器：给出候选降风险方向，但不自动下单。
7. 增加周报生成：比较本周和上次快照变化。
8. 增加 FastAPI `POST /diagnose` 和 `GET /snapshots`。

### P2：再考虑界面和外部数据

9. Dashboard 首页。
10. 股票池评分与个股基本面 Agent。
11. 行情 / 财报数据源。

---

## Implementation Plan

### Task 1: 新增 ticker metadata 配置

**Status:** ✅ Completed — `IA-DEV-20260602-007`

**Objective:** 用机器可读配置管理 ticker 的名称、资产类型、行业、主题、高风险标记，替代临时手工映射。

**Files:**
- Create: `investment-assistant/config/ticker_metadata.v1.yaml`
- Modify: `investment-assistant/src/investment_assistant/portfolio.py`
- Test: `investment-assistant/tests/test_metadata.py`

**Config example:**

```yaml
tickers:
  SPY:
    name: SPDR S&P 500 ETF Trust
    asset_type: etf
    sector: Index
    theme: US Large Cap
    risk_level: normal
  ONDS:
    name: Ondas Holdings Inc
    asset_type: stock
    sector: Technology
    theme: Drones/Industrial IoT
    risk_level: high
```

**Step 1: Write failing test**

```python
def test_loads_ticker_metadata():
    metadata = load_ticker_metadata(Path("config/ticker_metadata.v1.yaml"))
    assert metadata["SPY"].asset_type == AssetType.ETF
    assert metadata["ONDS"].risk_level == RiskLevel.HIGH
```

**Step 2: Run test to verify failure**

Run:

```bash
uv run pytest tests/test_metadata.py::test_loads_ticker_metadata -v
```

Expected: FAIL — `load_ticker_metadata` missing.

**Step 3: Implement minimal code**

Add:

- `TickerMetadata` Pydantic model.
- `load_ticker_metadata(path)`.

**Step 4: Run test to verify pass**

```bash
uv run pytest tests/test_metadata.py::test_loads_ticker_metadata -v
uv run pytest -q
```

---

### Task 2: 支持从原始 broker summary CSV 自动标准化

**Status:** ✅ Completed — `IA-DEV-20260602-009`

**Objective:** 支持用户上传 `Ticker,MarketValueUSD,WeightPct` 形式 CSV 后，自动根据 metadata 转成内部 `Holding` CSV。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/portfolio.py`
- Modify: `investment-assistant/src/investment_assistant/cli.py`
- Test: `investment-assistant/tests/test_portfolio.py`
- Test: `investment-assistant/tests/test_report_cli.py`

**New function:**

```python
def normalize_broker_summary_csv(raw_path: Path, metadata_path: Path, output_path: Path) -> Path:
    ...
```

**New CLI:**

```bash
investment-assistant normalize \
  --input data/portfolio_summary.csv \
  --metadata config/ticker_metadata.v1.yaml \
  --output examples/current_holdings.csv
```

**Step 1: Write failing test**

Test that raw CSV with `WeightPct=34.51` produces internal weight `0.3451`.

**Step 2: Run RED**

```bash
uv run pytest tests/test_portfolio.py::test_normalizes_broker_summary_csv -v
```

**Step 3: Implement normalization**

- Convert `WeightPct / 100`.
- Use metadata for `name`, `asset_type`, `sector`, `theme`, `risk_level`.
- If ticker is missing metadata, default to `stock` but emit a warning / exception based on strict mode.

**Step 4: Verify**

```bash
uv run pytest -q
uv run investment-assistant normalize --input data/portfolio_summary.csv --metadata config/ticker_metadata.v1.yaml --output examples/current_holdings.csv
```

---

### Task 3: 增加结构化 DiagnosisResult

**Status:** ✅ Completed — `IA-DEV-20260602-010`

**Objective:** 把诊断结果从“直接拼 Markdown”升级为结构化对象，便于 JSON、API、历史记录和报告复用。

**Files:**
- Create: `investment-assistant/src/investment_assistant/diagnosis.py`
- Modify: `investment-assistant/src/investment_assistant/report.py`
- Modify: `investment-assistant/src/investment_assistant/cli.py`
- Test: `investment-assistant/tests/test_diagnosis.py`

**Models:**

```python
class DiagnosisResult(BaseModel):
    allocation: AssetAllocation
    warnings: list[RuleWarning]
    health_score: int
    summary: str
```

**Step 1: Write failing test**

```python
def test_diagnose_portfolio_returns_structured_result():
    result = diagnose_portfolio(holdings, rules)
    assert result.allocation.stock_weight == 0.61
    assert result.warnings[0].severity in {"info", "warning", "critical"}
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_diagnosis.py::test_diagnose_portfolio_returns_structured_result -v
```

**Step 3: Implement**

- Move calls to `check_allocation_limits`, `check_single_position_limits`, `check_sector_theme_limits` into `diagnose_portfolio`.
- Keep `generate_health_report` as a renderer of `DiagnosisResult`.

**Step 4: Verify**

```bash
uv run pytest -q
```

---

### Task 4: 增加 warning severity 和 action hints

**Status:** ✅ Completed — `IA-DEV-20260606-001`

**Objective:** 每条规则提示不只说明“哪里超限”，还说明严重程度和建议动作。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/rules.py`
- Modify: `investment-assistant/src/investment_assistant/report.py`
- Test: `investment-assistant/tests/test_rules.py`

**Severity rules:**

- `info`：接近上限但未超限，比如 ONDS 9.84% 接近 10%。
- `warning`：轻微超限，比如行业 40%-50%。
- `critical`：明显超限，比如单票超过上限 20% 以上或行业超过 50%。

**Action hints:**

- Technology 行业超限：`avoid_adding_to_sector`。
- 高风险单票接近上限：`do_not_add_without_review`。
- 单票超限：`review_trim_to_limit`。

**Step 1: Write failing test**

```python
def test_high_risk_position_near_limit_gets_info_warning():
    warnings = check_single_position_limits([onds_984], rules)
    assert warnings[0].severity == "info"
    assert warnings[0].action_hint == "do_not_add_without_review"
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_rules.py::test_high_risk_position_near_limit_gets_info_warning -v
```

**Step 3: Implement minimal logic**

Add fields:

- `severity: Literal["info", "warning", "critical"]`
- `action_hint: str`

**Step 4: Verify**

```bash
uv run pytest -q
```

---

### Task 5: 增加 JSON 输出

**Status:** ✅ Completed — `IA-DEV-20260622-001`

**Objective:** CLI 可以同时输出 Markdown 和 JSON，方便后续 API / Dashboard 使用。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/cli.py`
- Test: `investment-assistant/tests/test_report_cli.py`

**CLI:**

```bash
investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-portfolio-health-report.md \
  --json-output reports/current-portfolio-health-report.json
```

**Step 1: Write failing test**

```python
def test_cli_diagnose_writes_json_output(tmp_path):
    run_diagnose(..., json_output_path=tmp_path / "report.json")
    data = json.loads((tmp_path / "report.json").read_text())
    assert data["allocation"]["stock_weight"] == 0.6102
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_report_cli.py::test_cli_diagnose_writes_json_output -v
```

**Step 3: Implement**

Use `DiagnosisResult.model_dump_json(indent=2)`.

**Step 4: Verify**

```bash
uv run pytest -q
uv run investment-assistant diagnose --holdings examples/current_holdings.csv --rules config/portfolio_rules.v1.yaml --output reports/current.md --json-output reports/current.json
```

---

### Task 6: SQLite 保存历史快照

**Objective:** 每次诊断可以保存快照，后续支持趋势、周报和复盘。

**Files:**
- Create: `investment-assistant/src/investment_assistant/storage.py`
- Test: `investment-assistant/tests/test_storage.py`

**Schema:**

```sql
CREATE TABLE portfolio_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  source_file TEXT,
  market_regime TEXT NOT NULL,
  holdings_json TEXT NOT NULL,
  diagnosis_json TEXT NOT NULL
);
```

**Step 1: Write failing test**

```python
def test_saves_and_loads_snapshot(tmp_path):
    db = tmp_path / "portfolio.db"
    snapshot_id = save_snapshot(db, holdings, diagnosis)
    loaded = load_snapshot(db, snapshot_id)
    assert loaded.id == snapshot_id
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_storage.py::test_saves_and_loads_snapshot -v
```

**Step 3: Implement**

Use standard-library `sqlite3`, no new dependency.

**Step 4: Verify**

```bash
uv run pytest -q
```

---

### Task 7: CLI 增加 snapshot 和 history

**Objective:** 让用户可以保存当前诊断，并列出历史快照。

**Files:**
- Modify: `investment-assistant/src/investment_assistant/cli.py`
- Modify: `investment-assistant/src/investment_assistant/storage.py`
- Test: `investment-assistant/tests/test_report_cli.py`

**Commands:**

```bash
investment-assistant snapshot \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --db data/portfolio.db

investment-assistant history --db data/portfolio.db
```

**Step 1: Write failing tests**

- `snapshot` writes one row to SQLite.
- `history` prints at least snapshot id and created_at.

**Step 2: Run RED**

```bash
uv run pytest tests/test_cli.py::test_snapshot_command_saves_snapshot -v
```

**Step 3: Implement**

Wire `diagnose_portfolio` → `save_snapshot`.

**Step 4: Verify**

```bash
uv run pytest -q
uv run investment-assistant snapshot --holdings examples/current_holdings.csv --rules config/portfolio_rules.v1.yaml --db data/portfolio.db
uv run investment-assistant history --db data/portfolio.db
```

---

### Task 8: 增加再平衡建议生成器 v0

**Objective:** 对当前超限项生成保守的候选动作，但不输出确定性买卖指令。

**Files:**
- Create: `investment-assistant/src/investment_assistant/rebalance.py`
- Modify: `investment-assistant/src/investment_assistant/report.py`
- Test: `investment-assistant/tests/test_rebalance.py`

**Design:**

For Technology 47.6% > 40%:

- 建议：`avoid_adding_to_sector`。
- 如果需要降风险，列出 Technology 持仓按权重排序。
- 不直接说“卖出 X 股”，只输出“复核候选”。

**Step 1: Write failing test**

```python
def test_rebalance_suggests_review_for_overweight_sector():
    suggestions = generate_rebalance_suggestions(holdings, diagnosis)
    assert suggestions[0].action == "review_sector_exposure"
    assert "Technology" in suggestions[0].reason
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_rebalance.py::test_rebalance_suggests_review_for_overweight_sector -v
```

**Step 3: Implement**

Minimal suggestion model:

```python
class RebalanceSuggestion(BaseModel):
    action: str
    reason: str
    candidates: list[str]
    requires_manual_confirmation: bool = True
```

**Step 4: Verify**

```bash
uv run pytest -q
```

---

### Task 9: FastAPI diagnose endpoint

**Objective:** 为未来 Dashboard 提供 HTTP API。

**Files:**
- Create: `investment-assistant/src/investment_assistant/api.py`
- Modify: `investment-assistant/pyproject.toml`
- Test: `investment-assistant/tests/test_api.py`

**Endpoint:**

- `POST /diagnose`
  - Input: holdings JSON + optional market_regime。
  - Output: `DiagnosisResult` JSON + `report_markdown`。

**Step 1: Write failing test**

```python
def test_post_diagnose_returns_allocation_and_warnings():
    client = TestClient(app)
    response = client.post("/diagnose", json={"holdings": [...], "market_regime": "neutral"})
    assert response.status_code == 200
    assert "allocation" in response.json()
```

**Step 2: Run RED**

```bash
uv run pytest tests/test_api.py::test_post_diagnose_returns_allocation_and_warnings -v
```

**Step 3: Implement**

Use FastAPI and load default rules from `config/portfolio_rules.v1.yaml` unless request provides rules.

**Step 4: Verify**

```bash
uv run pytest -q
uv run uvicorn investment_assistant.api:app --reload
```

Then open `/docs` if needed.

---

## Recommended execution order

Do not start with Dashboard yet. Recommended order:

1. Task 1：ticker metadata 配置。
2. Task 2：原始 CSV 自动标准化。
3. Task 3：结构化 DiagnosisResult。
4. Task 4：severity + action hints。
5. Task 5：JSON 输出。
6. Task 6-7：SQLite 快照 + history。
7. Task 8：再平衡建议生成器。
8. Task 9：FastAPI。

## Current sprint definition

P0 Task 1-5 已完成。下一轮建议进入历史快照能力：Task 6-7。

**Completed Sprint Goal:** 用户上传 broker summary CSV 后，一条命令能自动标准化、诊断，并同时输出 Markdown + JSON；报告能明确区分 `info / warning / critical`，并给出 action hints。

**Sprint Acceptance Criteria:**

1. `uv run pytest -q` 全部通过。
2. 以下命令可运行：

```bash
uv run investment-assistant normalize \
  --input data/portfolio_summary.csv \
  --metadata config/ticker_metadata.v1.yaml \
  --output examples/current_holdings.csv

uv run investment-assistant diagnose \
  --holdings examples/current_holdings.csv \
  --rules config/portfolio_rules.v1.yaml \
  --output reports/current-portfolio-health-report.md \
  --json-output reports/current-portfolio-health-report.json
```

3. JSON 输出包含：`allocation`, `warnings`, `health_score`, `summary`。
4. ONDS 接近高风险上限能输出 `info` 级别提示。
5. Technology 超过行业上限能输出 `warning` 级别提示和 `avoid_adding_to_sector` action hint。
