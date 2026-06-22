# IA-DEV-20260602-007 Ticker Metadata Configuration

## 基本信息

- 版本号：`IA-DEV-20260602-007`
- 日期：2026-06-02
- 类型：code
- 状态：completed
- 所属阶段：P0 — 让诊断更可信、更可复用
- 对应任务：`Next Development Roadmap.md` / Task 1: 新增 ticker metadata 配置

## 目标

新增机器可读的 ticker metadata 配置，让系统能够集中管理每个 ticker 的名称、资产类型、行业、主题和风险等级，为后续 broker CSV 自动标准化打基础。

## 完成内容

1. 新增 `TickerMetadata` Pydantic model。
2. 新增 `load_ticker_metadata(source)`：
   - 支持从 YAML 文件加载。
   - 支持从 dict 加载，方便测试。
   - 将 ticker key 统一规范为大写，例如 `spy` → `SPY`。
3. 新增 metadata 配置文件：
   - `config/ticker_metadata.v1.yaml`
   - 当前包含 12 个 ticker / 资产项：`SPY`, `QQQ`, `IBIT`, `AAPL`, `TSLA`, `NVDA`, `MSFT`, `AMZN`, `GOOGL`, `META`, `ONDS`, `CASH`。
4. 新增测试文件：
   - 验证 `SPY` 能加载为 ETF。
   - 验证 `ONDS` 被标记为 high risk。
   - 验证 ticker key 自动大写规范化。
5. 修复实际 console script 验证前的环境问题：
   - 发现 `uv run python` / `uv run investment-assistant` 无法 import installed package。
   - 执行 `uv pip install --python .venv/bin/python --reinstall .` 后恢复。

## 涉及文件

- `investment-assistant/config/ticker_metadata.v1.yaml`
- `investment-assistant/src/investment_assistant/portfolio.py`
- `investment-assistant/tests/test_metadata.py`
- `Next Development Roadmap.md`

## TDD 记录

### RED

命令：

```bash
uv run pytest tests/test_metadata.py -v
```

结果：

```text
ImportError: cannot import name 'load_ticker_metadata' from 'investment_assistant.portfolio'
```

说明：测试先失败，原因符合预期：功能尚不存在。

### GREEN

命令：

```bash
uv run pytest tests/test_metadata.py -v
```

结果：

```text
tests/test_metadata.py::test_loads_ticker_metadata_config PASSED
tests/test_metadata.py::test_ticker_metadata_keys_are_normalized_to_uppercase PASSED
2 passed in 0.32s
```

## 完整验证

### 全量测试

命令：

```bash
uv run pytest -q
```

结果：

```text
12 passed in 9.95s
```

### metadata 实际加载验证

命令：

```bash
uv run python - <<'PY'
from pathlib import Path
from investment_assistant.portfolio import load_ticker_metadata
metadata = load_ticker_metadata(Path('config/ticker_metadata.v1.yaml'))
print(len(metadata))
print(metadata['ONDS'].asset_type, metadata['ONDS'].risk_level, metadata['ONDS'].sector)
PY
```

结果：

```text
12
stock high Technology
```

### CLI smoke test

命令：

```bash
uv run investment-assistant --help
```

结果：

```text
usage: investment-assistant [-h] {diagnose} ...
```

命令：

```bash
uv run investment-assistant diagnose --holdings examples/holdings.sample.csv --rules config/portfolio_rules.v1.yaml --output reports/metadata-task-smoke-report.md
```

结果：

```text
Report written to reports/metadata-task-smoke-report.md
```

## 下一步

继续 P0 Task 2：支持从原始 broker summary CSV 自动标准化。

目标是用 `ticker_metadata.v1.yaml` 把 `Ticker,MarketValueUSD,WeightPct` 形式的原始 CSV 转换成系统内部 holdings CSV。
