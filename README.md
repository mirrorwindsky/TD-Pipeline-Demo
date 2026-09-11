# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

A **Technical Designer portfolio project** combining a playable Unity Vertical Slice with a designer-facing content Pipeline, validation tooling, Batch automation, QA evidence, and measured workflow improvement.

The project is intentionally built as one connected workflow rather than as separate gameplay and scripting exercises:

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

## Portfolio Snapshot

Current project evidence:

- playable indoor Unity Vertical Slice;
- Windows standalone build smoke-tested from launch to Mission Complete;
- multi-table CSV → typed Python model → generated Unity JSON Pipeline;
- schema / malformed-row / type / range / duplicate validation;
- `interactionType` semantic validation;
- cross-table Item-reference validation;
- active-Scene `configId` validation;
- fail-safe generation preserving previous valid output;
- validated Batch Preview / atomic Apply;
- reusable **40-record Scale Fixture**;
- systematic QA with **two real validation bugs found and fixed**;
- controlled 8-record benchmark: **192.000 s manual vs 0.287 s automated execution**;
- bilingual QA record and Pipeline Case Study.

Primary supporting documents:

- Pipeline Case Study: [`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md);
- Day 11 QA Record: [`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md);
- [`Docs/README.md`](Docs/README.md) — current vs historical documentation index;
- [`TODO.md`](TODO.md) — sprint execution record;
- [`STATUS.md`](STATUS.md) — current project state and next focus.

---

## Current Gameplay Slice

The active gameplay / build Scene is:

```text
Assets/Scenes/VerticalSlice_01.unity
```

The preserved Week 1 baseline is:

```text
Assets/Scenes/Prototype_01.unity
```

Current gameplay dependency chain:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

The slice includes:

- enclosed multi-room industrial-facility layout;
- mouse-controlled third-person camera;
- player-relative CharacterController movement with gravity;
- generic interaction through `IInteractable`;
- Pickup / Device / Gate gameplay types;
- minimal ID-based inventory state;
- required-item and prerequisite-device dependencies;
- event-driven gate unlocking and objective progression;
- config-driven Objective text;
- `[E] Interact`, transient Feedback, and persistent Mission Complete HUD;
- materials, indoor lighting, room differentiation, and readable interactables;
- persistent PowerNode / ControlTerminal / Exit completion-state feedback.

Familiar-player timing after the presentation pass:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The earlier 5–8 minute target was intentionally retired rather than padded with slower movement, empty corridors, inflated interaction counts, arbitrary searching, or unrelated gameplay systems.

A Windows x86-64 standalone build was completed and manually smoke-tested from launch to Mission Complete. Build artifacts remain local and are ignored by Git.

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
items.csv
+ objectives.csv
+ interactables.csv
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

Typed intermediate model:

```text
ContentModel
├── items: list[ItemConfig]
├── objectives: list[ObjectiveConfig]
└── interactables: list[InteractableConfig]
```

Generated output:

```text
Assets/Data/
├── interactables.json
└── objectives.json
```

Generated JSON is treated as Pipeline output rather than normal designer-authored source.

### Current Validation Coverage

The Pipeline currently checks:

- missing CSV headers;
- missing required columns / values;
- unexpected extra columns / malformed rows;
- invalid integer / boolean values;
- invalid or suspicious interaction ranges;
- duplicate IDs;
- illegal `interactionType` values;
- unknown `requiredItemId` / `grantedItemId` references;
- supported Interactable `configId` references in `VerticalSlice_01.unity`;
- fail-safe output preservation after validation failure.

The active-Scene reference validator intentionally targets the current known config-driven Interactable component types. It is **not** a generalized all-Scene / all-Prefab dependency scanner.

---

## CLI

Tool entry point:

```text
Tools/config_tool.py
```

Requirements:

- Python 3
- Unity 6.3 LTS for the playable project

Show available commands:

```powershell
py Tools/config_tool.py --help
```

Normal validation + generation:

```powershell
py Tools/config_tool.py
```

or:

```powershell
py Tools/config_tool.py generate
```

Preview a validated Batch without changing source files:

```powershell
py Tools/config_tool.py batch-preview
```

Apply a validated Batch:

```powershell
py Tools/config_tool.py batch-apply
```

After Batch Apply, run normal generation again to validate and propagate the changed source into Unity data.

Current generation contract:

- `ERROR` blocks generation;
- `WARNING` is reported but does not block generation;
- failed validation does not overwrite previous valid JSON;
- Batch Preview performs no source modification;
- Batch Apply writes source CSV atomically after logical validation.

---

## Batch Processing

The current real Batch use case is bulk modification of `requiredInteractions`.

Workflow:

```text
batch_interaction_updates.csv
↓
full-batch validation
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source-file replacement
↓
normal Pipeline generation
↓
Unity Runtime
```

The normal Demo Batch example includes:

```text
cube_sturdy:       3 → 4
power_node:        3 → 2
control_terminal:  2 → 1
```

Day 11 additionally verified an 8-record Batch against a 20-Interactable Scale Fixture. Exactly the intended eight `requiredInteractions` fields changed, no other source fields changed, and all eight values propagated into generated JSON.

---

## QA + Scale Evidence

Reusable valid fixture:

```text
QA/Fixtures/scale_valid/
├── items.csv                    8 records
├── objectives.csv              12 records
├── interactables.csv           20 records
└── batch_interaction_updates.csv 8 updates
```

Total Scale Test content:

```text
40 records
```

QA coverage included:

- valid 40-record generation;
- 8-record Batch Preview;
- 8-record Batch Apply + regeneration;
- missing required values;
- missing required columns;
- duplicate IDs;
- invalid integer types;
- invalid ranges;
- invalid `interactionType` values;
- broken cross-table Item references;
- broken active-Scene `configId` references;
- empty CSV input;
- malformed CSV rows;
- fail-safe output preservation.

Full evidence: [`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md)

### Real Bug 1 — Active V2 Scene Reference Coverage

QA reproduced a source rename where `VerticalSlice_01.unity` still referenced `control_terminal`, but generated JSON no longer contained that ID. The pre-fix validator still targeted the V1 baseline Scene and incorrectly passed generation.

The validator was updated to target the active Scene and the current config-driven Interactable component whitelist. The same broken reference is now blocked before generation.

Main fix:

```text
97b24be fix: validate active scene config references
```

### Real Bug 2 — Malformed CSV Silent Truncation

An unescaped comma produced an unexpected extra CSV value. Before the fix, `csv.DictReader` stored the overflow under the `None` key, validation passed, and an Objective description was silently truncated.

`validate_schema()` now rejects unexpected extra values with a row-level ERROR.

Main fix:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

### Fail-Safe Evidence

For a missing required value, SHA256 hashes of both generated JSON files were captured before and after failed generation. Both hashes remained unchanged.

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

---

## Before / After Benchmark

The same 40-record fixture and the same 8 intended `requiredInteractions` changes were used for a controlled equivalent-output comparison.

### Manual Path

The manual workflow required:

1. locate the 8 targets in `ConfigSource/interactables.csv`;
2. edit the 8 source values;
3. locate the corresponding generated JSON records;
4. manually apply the same 8 values;
5. check and save both files.

Measured execution time:

```text
192.000 s
```

Independent verification:

```text
CSV records: 20
JSON records: 20
overall: PASS
0 unintended CSV field changes detected
```

### Automated Path

```text
batch-preview
→ batch-apply
→ generate
```

Measured execution time:

```text
0.2865603 s
```

Independent verification also passed.

### Result

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

This is explicitly an **execution-stage benchmark**. It excludes the time required to author the Batch request itself and is not presented as a claim that the entire content-production process is 670× faster.

The timing sample produced 0 manual errors and 0 automated errors. Error-risk reduction is therefore supported separately by the QA evidence rather than inferred from this benchmark.

Full analysis: [`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md)

---

## Design Trade-offs

Several possible extensions were intentionally not implemented:

- Unity Editor GUI;
- dependency visualization;
- generalized Quest framework;
- dependency-cycle detection;
- unreachable-objective detection;
- all-Scene / all-Prefab scanning;
- large automated-test framework.

Decision rule:

> Add complexity only when current content, QA, or workflow evidence demonstrates that the complexity solves a real problem.

Examples:

- Unity Editor integration was skipped because the CLI already exposes Generate / Preview / Apply without adding process-launching and Editor-only maintenance overhead.
- dependency-cycle / unreachable-objective checks were skipped because the current architecture does not externalize a generalized objective dependency graph.
- active-Scene reference validation was expanded only after QA demonstrated a real stale-ID failure.
- malformed-row validation was added only after QA reproduced silent content corruption.

---

## Project Structure

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   ├── interactables.json
│   │   └── objectives.json
│   ├── Materials/
│   │   └── D10Facility/
│   ├── Scenes/
│   │   ├── Prototype_01.unity
│   │   └── VerticalSlice_01.unity
│   └── Scripts/
│
├── ConfigSource/
│   ├── items.csv
│   ├── objectives.csv
│   ├── interactables.csv
│   └── batch_interaction_updates.csv
│
├── QA/
│   └── Fixtures/
│       └── scale_valid/
│
├── Docs/
│   ├── README.md
│   ├── D10_HANDOFF.md
│   ├── D11_QA.md
│   ├── D11_QA.zh-CN.md
│   ├── Pipeline_Case_Study.md
│   ├── Pipeline_Case_Study.zh-CN.md
│   ├── Pipeline_V1.md
│   └── Pipeline_V1.zh-CN.md
│
├── Tools/
│   └── config_tool.py
│
├── README.md
├── README.zh-CN.md
├── STATUS.md
└── TODO.md
```

---

## AI-Assisted Development

AI / Codex was used as a development accelerator, not as a substitute for validation or understanding.

No artificial AI-generated failure was created simply to satisfy a checklist. Day 11 did include genuine AI-assisted debugging on two real QA-discovered defects. Both failures were reproduced from concrete inputs, diagnosed, fixed with narrow changes, regression-tested, and integrated into `main`.

Anything presented in the README, Case Study, video, or resume is intended to remain independently explainable without Codex.

---

## Portfolio / Interview Summary

A concise explanation of the project:

> I built a Unity Vertical Slice and used its real content dependencies to drive a Python Content Pipeline. The Pipeline parses multi-table CSV into a typed intermediate model, validates schema, values, duplicate IDs, cross-table Item references, and active-Scene config references, then generates Unity-consumable JSON. I added validated atomic Batch updates for repeated interaction tuning, tested the system with a 40-record fixture, and used QA to discover and fix two real validation bugs. In a controlled 8-record execution benchmark, manual equivalent-output editing took 192 seconds while Batch Preview → Apply → Generate took 0.287 seconds; I treat that as execution-stage evidence rather than a claim about the entire production workflow.

---

## Current Packaging Status

The technical project core, QA evidence, measured Pipeline Case Study, and bilingual core documentation are complete.

Immediate next work is resume / application packaging rather than more feature development.

Optional follow-up after the resume is usable:

- record a short final demo video;
- collect external TD / user feedback if available.

The stable portfolio source is the GitHub `main` branch.