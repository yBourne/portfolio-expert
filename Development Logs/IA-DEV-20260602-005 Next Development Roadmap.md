# IA-DEV-20260602-005 Next Development Roadmap

- 版本号：IA-DEV-20260602-005
- 日期：2026-06-02
- 类型：planning / roadmap
- 状态：completed

## 目标

在已完成 CLI 诊断 MVP 后，规划下一阶段项目开发内容，明确 P0 / P1 / P2 优先级和下一轮 sprint 验收标准。

## 完成内容

- 创建下一阶段开发路线图。
- 明确短期不优先做 Dashboard，先打稳诊断能力和数据结构。
- 定义 P0：
  - ticker metadata 配置。
  - 原始 broker summary CSV 自动标准化。
  - 结构化 `DiagnosisResult`。
  - warning severity + action hints。
  - JSON 输出。
- 定义 P1：
  - SQLite 历史快照。
  - `snapshot` / `history` CLI。
  - 再平衡建议生成器。
  - FastAPI。
- 定义 P2：
  - Dashboard。
  - 股票池评分与个股基本面 Agent。
  - 行情 / 财报数据源。
- 将 roadmap 加入项目索引。

## 涉及文件

- `Next Development Roadmap.md`
- `Investment Assistant - Index.md`

## 当前 Sprint Goal

用户上传 broker summary CSV 后，一条命令能自动标准化、诊断，并同时输出 Markdown + JSON；报告能明确区分 `info / warning / critical`，并给出 action hints。

## Sprint Acceptance Criteria

- `uv run pytest -q` 全部通过。
- `investment-assistant normalize` 可运行。
- `investment-assistant diagnose --json-output ...` 可运行。
- JSON 输出包含：`allocation`, `warnings`, `health_score`, `summary`。
- ONDS 接近高风险上限输出 `info`。
- Technology 超过行业上限输出 `warning` 和 `avoid_adding_to_sector` action hint。

## 验证结果

实际运行：

```bash
uv run pytest -q
```

结果：

```text
10 passed in 0.43s
```

## 下一步

执行 P0 sprint，从 `ticker_metadata.v1.yaml` 和 `normalize` CLI 开始。
