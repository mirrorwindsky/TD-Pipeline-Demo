# Documentation Index / 文档索引

This folder contains both **current portfolio evidence** and **historical milestone records**.

本目录同时包含**当前作品集材料**与**历史里程碑记录**。如果只想快速了解当前项目，优先阅读 Current Portfolio Documents。

## Current Portfolio Documents / 当前作品集文档

| Document | English | 简体中文 | Purpose / 用途 |
| --- | --- | --- | --- |
| Pipeline Case Study | [`Pipeline_Case_Study.md`](Pipeline_Case_Study.md) | [`Pipeline_Case_Study.zh-CN.md`](Pipeline_Case_Study.zh-CN.md) | Problem → design → QA → Before / After benchmark → trade-offs → outcome / 问题、设计、QA、量化、取舍、结果 |
| D11 QA + Scale Test | [`D11_QA.md`](D11_QA.md) | [`D11_QA.zh-CN.md`](D11_QA.zh-CN.md) | 40-record Scale Test, bad-data QA, real bug fixes, fail-safe evidence / Scale Test、坏数据 QA、真实 Bug 与 fail-safe 证据 |

Repository entry point / 仓库入口：

- [`../README.md`](../README.md) / [`../README.zh-CN.md`](../README.zh-CN.md)
- [Windows x64 v1.0.0 Release](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

## Project Records / 项目记录

These files document project state and development sequence. They are useful for tracing decisions, but they are not required reading for the portfolio overview.

以下文件用于记录项目状态与开发顺序，适合追踪决策过程，但不是快速阅读作品集时的必读材料。

- [`../STATUS.md`](../STATUS.md) — current technical release snapshot / 当前技术状态快照；
- [`../TODO.md`](../TODO.md) — 14-day implementation record / 14 天实现记录。

## Historical Milestone Records / 历史里程碑记录

These documents are intentionally preserved as snapshots of earlier stages. They are **not** the current Pipeline specification.

以下文档被有意保留为早期阶段快照，**不代表当前 Pipeline 的最终规格**。

- [`D10_HANDOFF.md`](D10_HANDOFF.md) — sealed Day 10 presentation / build / CLI handoff before QA;
- [`Pipeline_V1.md`](Pipeline_V1.md) / [`Pipeline_V1.zh-CN.md`](Pipeline_V1.zh-CN.md) — Week 1 single-table Pipeline V1 architecture before the later multi-table V2, active-Scene validation, Scale QA, and measured Batch evidence.

## Current Evidence Snapshot / 当前证据摘要

```text
Playable Unity Vertical Slice
+
Multi-Table Typed Content Pipeline
+
Validation + Batch Automation
+
40-record Scale / QA Evidence
+
2 real validation bugs found and fixed
+
192.000 s manual vs 0.287 s automated execution benchmark
+
Windows x64 v1.0.0 playable release
```

The stable portfolio source is the repository `main` branch.

稳定作品集内容以仓库 `main` 分支为准。
