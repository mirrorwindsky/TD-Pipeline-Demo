# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

**Playable Build:** [Download Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/download/v1.0.0/TD-Pipeline-Demo-Windows-x64-v1.0.0.zip) · [Release Notes](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

A **Technical Designer portfolio project** combining a playable Unity Vertical Slice with a designer-facing content Pipeline, validation tooling, Batch automation, QA evidence, and measured workflow improvement.

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

## Portfolio Snapshot

- Playable indoor Unity Vertical Slice and Windows x86-64 standalone release;
- multi-table CSV → typed Python model → generated Unity JSON Pipeline;
- schema / malformed-row / type / range / duplicate validation;
- `interactionType`, cross-table Item-reference, and active-Scene `configId` validation;
- fail-safe generation preserving previous valid output on ERROR;
- validated Batch Preview / atomic Apply;
- reusable **40-record Scale Fixture**;
- systematic QA with **two real validation bugs found and fixed**;
- controlled 8-record benchmark: **192.000 s manual vs 0.287 s automated execution**;
- bilingual QA record and Pipeline Case Study.

Primary supporting documents:

- Pipeline Case Study: [`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md)
- Day 11 QA Record: [`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md)
- [`Docs/README.md`](Docs/README.md) — current vs historical documentation index
- [`TODO.md`](TODO.md) — sprint execution record
- [`STATUS.md`](STATUS.md) — current project state

---

## Playable Build

Current portfolio release:

```text
v1.0.0
Windows x86-64
Unity 6.3 LTS
```

Download the complete archive from the GitHub Release above, extract it, and run:

```text
TD-Pipeline-Demo.exe
```

Controls:

- `WASD` — Move
- Mouse — Camera
- `E` — Interact
- `Esc` — Release cursor
- Close the window to exit

The release was manually tested from launch to Mission Complete. Repository build artifacts remain excluded from Git history; the packaged standalone build is distributed through GitHub Releases.

---

## Current Gameplay Slice

Active gameplay / build Scene:

```text
Assets/Scenes/VerticalSlice_01.unity
```

Preserved Week 1 baseline:

```text
Assets/Scenes/Prototype_01.unity
```

Gameplay dependency chain:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

The slice includes a multi-room industrial-facility layout, third-person mouse camera, player-relative movement, generic `IInteractable` interaction, Pickup / Device / Gate content, minimal inventory state, config-driven item dependencies and Objective text, event-driven gate / mission flow, HUD feedback, materials, lighting, and persistent world-state feedback.

Familiar-player timing after the presentation pass:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The earlier 5–8 minute target was intentionally retired rather than padded with filler.

---

## Designer-Facing Content Pipeline

Designer-authored source:

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

Normal generation flow:

```text
items.csv + objectives.csv + interactables.csv
        ↓
Parse Once SourceTables
        ↓
Schema / malformed-row / type / range / duplicate validation
        ↓
Typed ContentModel
        ↓
interactionType validation
        ↓
Item cross-reference validation
        ↓
active Scene configId validation
        ↓
ERROR / WARNING gate
        ↓
interactables.json + objectives.json
        ↓
Unity config databases
        ↓
Runtime gameplay + HUD
```

Typed model:

```text
ContentModel
├── items: list[ItemConfig]
├── objectives: list[ObjectiveConfig]
└── interactables: list[InteractableConfig]
```

Generated JSON is treated as Pipeline output rather than a second hand-maintained source of truth.

### CLI

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Generation contract:

- `ERROR` blocks generation;
- `WARNING` is reported but does not block generation;
- failed validation does not overwrite previous valid JSON;
- Batch Preview performs no source modification;
- Batch Apply writes source CSV atomically after full logical validation.

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

Total Scale Test content: **40 records**.

QA covered valid Scale generation, Batch Preview / Apply, missing values / columns, duplicate IDs, invalid types / ranges / `interactionType`, broken cross-table references, broken active-Scene config references, empty CSV input, malformed rows, and fail-safe output preservation.

Two real defects were discovered and fixed:

1. **Active V2 Scene reference coverage gap** — stale `configId` references in `VerticalSlice_01.unity` could incorrectly pass validation. Fixed in `97b24be`.
2. **Malformed CSV silent truncation** — an unescaped comma could be accepted and silently truncate Objective content. Fixed in `bb088b3`.

For one invalid-source test, SHA256 hashes of both generated JSON files were unchanged before / after failed generation, directly verifying the known-good-output preservation contract.

Full evidence: [`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md)

---

## Before / After Benchmark

The same 40-record fixture and the same 8 `requiredInteractions` changes were used for an equivalent-output comparison.

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

This is explicitly an **execution-stage benchmark**. It excludes authoring the Batch request itself and is not a claim that the entire content-production process is 670× faster. Error-risk reduction is supported separately by the QA evidence rather than inferred from this timing sample.

Full analysis: [`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md)

---

## Design Trade-offs

The project intentionally does **not** add a Unity Editor GUI, dependency visualization, generalized Quest framework, cycle / unreachable-objective detection, all-Scene / all-Prefab scanning, or a large test framework without demonstrated need.

Decision rule:

> Add complexity only when implementation, QA, or workflow evidence demonstrates that the complexity solves a real problem.

The active-Scene reference validator and malformed-row validation were both added only after real QA failures demonstrated the need.

---

## Documentation

Current portfolio documents:

```text
README.md / README.zh-CN.md
→ portfolio entry point + playable release

Docs/Pipeline_Case_Study.md / .zh-CN.md
→ problem, design, QA, benchmark, trade-offs, outcome

Docs/D11_QA.md / .zh-CN.md
→ reproducible QA and bug-fix evidence

QA/Fixtures/scale_valid/
→ reusable Scale / benchmark fixture
```

Historical records such as `D10_HANDOFF.md` and `Pipeline_V1.md` are intentionally preserved as milestone snapshots rather than rewritten as final V2 documentation.

---

## AI-Assisted Development

AI / Codex was used as a development accelerator, not as a substitute for validation or understanding. The two QA-discovered bugs were reproduced from concrete inputs, diagnosed, fixed with narrow changes, regression-tested, and documented. Anything used in the README, Case Study, video, or resume is intended to remain independently explainable without Codex.

---

## Portfolio / Interview Summary

> I built a Unity Vertical Slice and used its real content dependencies to drive a Python Content Pipeline. The Pipeline parses multi-table CSV into a typed intermediate model, validates schema, values, duplicate IDs, cross-table Item references, and active-Scene config references, then generates Unity-consumable JSON. I added validated atomic Batch updates for repeated interaction tuning, tested the system with a 40-record fixture, and used QA to discover and fix two real validation bugs. In a controlled 8-record execution benchmark, manual equivalent-output editing took 192 seconds while Batch Preview → Apply → Generate took 0.287 seconds; I treat that as execution-stage evidence rather than a claim about the entire production workflow.

---

## Current Status

The technical core, QA evidence, measured Pipeline Case Study, bilingual documentation, and playable **v1.0.0 Windows x64 Release** are complete.

The next priority is **resume, project explanation, and applications**, not additional feature development.
