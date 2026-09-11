# Technical Project Status

**Last updated:** 2026-09-11  
**Release:** `v1.0.0`  
**Repository:** `TD-Pipeline-Demo`

## Current Milestone — Portfolio Release Complete ✅

The technical project core, QA evidence, measured workflow comparison, bilingual documentation, and Windows x64 playable release are complete.

Current verified evidence includes:

- playable indoor Unity Vertical Slice;
- Windows x86-64 standalone release tested from launch to Mission Complete;
- multi-table Content Pipeline V2;
- parse-once `SourceTable` architecture;
- typed `ContentModel`;
- schema / malformed-row / type / range / duplicate validation;
- legal `interactionType` validation;
- Item cross-table reference validation;
- active `VerticalSlice_01.unity` `configId` validation for supported Interactable components;
- fail-safe generation preserving previous valid JSON on ERROR;
- validated Batch Preview / atomic Apply;
- reusable 40-record Scale Fixture;
- systematic bad-data QA with two real validation defects found and fixed;
- controlled manual-vs-automated execution benchmark;
- bilingual Pipeline Case Study and QA record;
- GitHub Release `v1.0.0` with the tested Windows x64 build.

Playable release:

- [Release Notes](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)
- [Download Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/download/v1.0.0/TD-Pipeline-Demo-Windows-x64-v1.0.0.zip)

---

## Stable Gameplay Chain

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

Stable configured interaction counts:

```text
power_node        = 3
control_terminal  = 2
```

Active presentation / build Scene:

```text
Assets/Scenes/VerticalSlice_01.unity
```

Protected Week 1 baseline:

```text
Assets/Scenes/Prototype_01.unity
```

---

## Current Designer-Facing Pipeline

```text
ConfigSource/items.csv
+ ConfigSource/objectives.csv
+ ConfigSource/interactables.csv
        ↓
Tools/config_tool.py
        ↓
Parse Once SourceTables
        ↓
Schema / malformed-row / Type / Range / Duplicate Validation
        ↓
Typed ContentModel
        ↓
interactionType / Item Cross-Reference / active Scene configId Validation
        ↓
ERROR Gate
        ↓
Assets/Data/interactables.json
+ Assets/Data/objectives.json
        ↓
Unity Config Databases
        ↓
Runtime Gameplay + HUD
        ↓
Windows standalone demo
```

CLI:

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Verified guarantees:

- invalid source data blocks generation;
- previous valid generated JSON remains preserved after validation failure;
- successful generation uses the same typed model used by validation;
- Batch Preview performs no source modification;
- Batch Apply writes `interactables.csv` atomically after logical validation;
- active-Scene config references are checked for the current supported Interactable types;
- malformed CSV rows with unexpected extra values are rejected instead of silently truncating data.

---

## QA + Scale Evidence

Reusable fixture:

```text
QA/Fixtures/scale_valid/
├── items.csv                     8 records
├── objectives.csv               12 records
├── interactables.csv            20 records
└── batch_interaction_updates.csv 8 updates
```

Total content records used for Scale Test: **40**.

Test summary:

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | Baseline sanity check | PASS |
| QA-01 | Valid 40-record Scale Generation | PASS |
| QA-02 | 8-record Scale Batch Preview | PASS |
| QA-03 | 8-record Batch Apply + Regeneration | PASS |
| QA-04 | Missing required value + fail-safe preservation | PASS |
| QA-05 | Duplicate ID | PASS |
| QA-06 | Invalid integer type | PASS |
| QA-07 | Invalid range | PASS |
| QA-08 | Broken cross-table Item reference | PASS |
| QA-09 | Broken active V2 Scene `configId` | FAIL → FIXED → PASS |
| QA-10 | Missing required column | PASS |
| QA-11 | Invalid `interactionType` | PASS |
| QA-12 | Empty CSV input | PASS |
| QA-13 | Malformed CSV / extra column | FAIL → FIXED → PASS |

Full evidence:

- [`Docs/D11_QA.md`](Docs/D11_QA.md)
- [`Docs/D11_QA.zh-CN.md`](Docs/D11_QA.zh-CN.md)

Real fixes:

```text
97b24be fix: validate active scene config references
bb088b3 fix: reject malformed CSV rows with extra columns
```

Fail-safe behavior was independently verified by comparing SHA256 hashes of both generated JSON files before and after a failed generation; both remained unchanged.

---

## Before / After Measurement

Controlled execution-stage benchmark using the same 40-record fixture and the same 8 intended updates:

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

Automated path:

```text
batch-preview
→ batch-apply
→ generate
```

Both manual and automated outputs passed independent verification.

This measurement excludes authoring the Batch request itself and is not a claim that the entire content-production process is 670× faster.

Full Case Study:

- [`Docs/Pipeline_Case_Study.md`](Docs/Pipeline_Case_Study.md)
- [`Docs/Pipeline_Case_Study.zh-CN.md`](Docs/Pipeline_Case_Study.zh-CN.md)

---

## Scope Boundaries

The current release intentionally does not include:

- a generalized Quest framework;
- dependency visualization;
- Unity Editor GUI;
- dependency-cycle / unreachable-objective detection;
- generalized all-Scene / all-Prefab dependency scanning;
- a large automated-test framework;
- dedicated sound / VFX polish.

These are explicit scope decisions rather than hidden omissions. New complexity is added only when implementation, QA, or workflow evidence demonstrates a concrete need.

---

## AI-Assisted Development

AI / Codex was used as a development accelerator during implementation, diagnosis, and verification. Project claims are backed by concrete repository history, reproducible QA inputs, independent checks, measured results, and manual standalone testing.

---

## Documentation

Current portfolio documents:

- [`README.md`](README.md) / [`README.zh-CN.md`](README.zh-CN.md)
- [`Docs/Pipeline_Case_Study.md`](Docs/Pipeline_Case_Study.md) / [`Docs/Pipeline_Case_Study.zh-CN.md`](Docs/Pipeline_Case_Study.zh-CN.md)
- [`Docs/D11_QA.md`](Docs/D11_QA.md) / [`Docs/D11_QA.zh-CN.md`](Docs/D11_QA.zh-CN.md)
- [`Docs/README.md`](Docs/README.md)

Historical milestone records are preserved separately and are not presented as the current V2 specification.