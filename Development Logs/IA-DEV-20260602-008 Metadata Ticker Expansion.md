# IA-DEV-20260602-008 Metadata Ticker Expansion

## 基本信息

- 版本号：`IA-DEV-20260602-008`
- 日期：2026-06-02
- 类型：configuration
- 状态：completed
- 所属阶段：P0 — 让诊断更可信、更可复用
- 对应任务：扩充 `ticker_metadata.v1.yaml`

## 目标

根据用户提供的 moomoo 自选 / 持仓截图，补充 Investment Assistant 的 ticker metadata，使后续 broker CSV 标准化能识别更多当前关注和持仓标的。

## 从截图识别到的标的

### AI / SW / Following 自选页

- `NVDA` — NVIDIA Corp，已存在
- `GOOGL` — Alphabet Inc，已存在
- `IREN` — IREN Ltd
- `COHR` — Coherent Corp
- `TSM` — Taiwan Semiconductor Manufacturing Co Ltd
- `MSFT` — Microsoft Corp，已存在
- `INTC` — Intel Corp
- `MU` — Micron Technology Inc
- `FN` — Fabrinet
- `CLS` — Celestica Inc
- `SMCI` — Super Micro Computer Inc
- `NOK` — Nokia Oyj
- `HPQ` — HP Inc
- `MDB` — MongoDB Inc
- `MRVL` — Marvell Technology Inc
- `ONDS` — Ondas Holdings Inc，已存在
- `ACMR` — ACM Research Inc
- `HIMX` — Himax Technologies Inc
- `LPTH` — LightPath Technologies Inc
- `OUST` — Ouster Inc
- `MDT` — Medtronic plc

### Following 新截图

- `SPY` — SPDR S&P 500 ETF Trust，已存在
- `SNDK` — SanDisk Corp
- `EWY` — iShares MSCI South Korea ETF
- `SOXX` — iShares Semiconductor ETF
- `SOXL` — Direxion Daily Semiconductor Bull 3X Shares
- `OKLO` — Oklo Inc

## 完成内容

1. 扩充 `config/ticker_metadata.v1.yaml`。
2. 新增 22 个 metadata 条目。
3. 保留原有条目，并避免重复新增已有 ticker。
4. 对高风险 / 杠杆 / 小盘主题标的设置 `risk_level: high`：
   - `IREN`, `SMCI`, `ACMR`, `HIMX`, `LPTH`, `OUST`, `SOXL`, `OKLO`
5. 将 ETF 标的设置为 `asset_type: etf`：
   - `EWY`, `SOXX`, `SOXL`
6. 当前 metadata 总数从 12 增加到 34。

## 涉及文件

- `investment-assistant/config/ticker_metadata.v1.yaml`
- `Development Logs/IA-DEV-20260602-008 Metadata Ticker Expansion.md`
- `Development Logs/Development Log - Index.md`

## 验证结果

### metadata 加载验证

命令：

```bash
PYTHONPATH=src uv run python - <<'PY'
from pathlib import Path
from investment_assistant.portfolio import load_ticker_metadata
metadata = load_ticker_metadata(Path('config/ticker_metadata.v1.yaml'))
for ticker in ['IREN','COHR','INTC','FN','CLS','SMCI','NOK','HPQ','MDB','ACMR','HIMX','LPTH','OUST','MDT','SNDK','EWY','SOXX','SOXL','OKLO']:
    item = metadata[ticker]
    print(f'{ticker}: {item.name} | {item.asset_type} | {item.sector} | {item.theme} | {item.risk_level}')
print('TOTAL', len(metadata))
PY
```

结果：

```text
IREN: IREN Ltd | stock | Technology | Bitcoin Mining/AI Data Centers | high
COHR: Coherent Corp | stock | Technology | Optical Components/Semiconductors | normal
INTC: Intel Corp | stock | Technology | Semiconductors | normal
FN: Fabrinet | stock | Technology | Optical Manufacturing | normal
CLS: Celestica Inc | stock | Technology | Electronics Manufacturing/AI Infrastructure | normal
SMCI: Super Micro Computer Inc | stock | Technology | AI Servers/Data Centers | high
NOK: Nokia Oyj | stock | Technology | Telecom Equipment | normal
HPQ: HP Inc | stock | Technology | PCs/Printing | normal
MDB: MongoDB Inc | stock | Technology | Database/Cloud Software | normal
ACMR: ACM Research Inc | stock | Technology | Semiconductor Equipment | high
HIMX: Himax Technologies Inc | stock | Technology | Display Semiconductors | high
LPTH: LightPath Technologies Inc | stock | Technology | Optical Components | high
OUST: Ouster Inc | stock | Technology | LiDAR/Autonomous Systems | high
MDT: Medtronic plc | stock | Healthcare | Medical Devices | normal
SNDK: SanDisk Corp | stock | Technology | Data Storage/Memory | normal
EWY: iShares MSCI South Korea ETF | etf | Index | South Korea Equities | normal
SOXX: iShares Semiconductor ETF | etf | Index | Semiconductors | normal
SOXL: Direxion Daily Semiconductor Bull 3X Shares | etf | Index | Leveraged Semiconductors | high
OKLO: Oklo Inc | stock | Utilities | Nuclear Energy/Small Modular Reactors | high
TOTAL 34
```

### 测试

命令：

```bash
uv run pytest tests/test_metadata.py -q
```

结果：

```text
2 passed in 0.23s
```

命令：

```bash
uv run pytest -q
```

结果：

```text
12 passed in 0.26s
```

## 注意事项

- `SanDisk Corp` / `SNDK` 按截图 ticker 添加；后续如实际 broker 导出的名称不同，可再校正 name 字段。
- `SOXL` 是三倍杠杆半导体 ETF，已标记为 `risk_level: high`。
- `OKLO`, `OUST`, `LPTH`, `HIMX`, `ACMR`, `IREN`, `SMCI` 因小盘 / 高波动 / 主题集中度较高，暂标记为高风险。

## 下一步

继续 P0 Task 2：支持从原始 broker summary CSV 自动标准化。
