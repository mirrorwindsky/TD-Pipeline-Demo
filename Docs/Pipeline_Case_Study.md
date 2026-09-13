# Pipeline Case Study — TD Pipeline Demo

English | [简体中文](Pipeline_Case_Study.zh-CN.md)

**Playable Build:** [Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

## Overview

`TD-Pipeline-Demo` is a Technical Designer portfolio project built around one connected workflow:

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

The project uses a compact playable Unity slice to create real content-production problems, then solves only the problems demonstrated by implementation, QA, or workflow evidence.

Core stack:

- Unity 6.3 LTS
- C#
- Python
- CSV / JSON
- Git / GitHub

Playable flow:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ Mission Complete
```

---

## 1. Problem

The first pipeline version used one small configuration table and a simple CSV → JSON path. Once the playable slice introduced real content dependencies, several production risks appeared:

- multiple source tables needed consistent structure;
- `requiredInteractions` needed type / range validation;
- IDs needed uniqueness guarantees;
- `interactionType` needed semantic validation;
- Interactables referenced Item IDs from another table;
- Unity Scene objects held `configId` values that could become stale after content renaming;
- repeated tuning across many records required repetitive lookup and editing;
- malformed CSV could silently corrupt generated content;
- failed validation should not overwrite the previous known-good generated data.

The design question became:

> What is the smallest Pipeline that can make these content changes predictable before they reach Unity Runtime?

---

## 2. Pipeline Design

### Designer-Facing Source

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

The three content tables are parsed once into `SourceTable` objects and converted into typed data:

```text
SourceTable
→ ItemConfig
→ ObjectiveConfig
→ InteractableConfig
→ ContentModel
```

### Validation and Generation

```text
CSV Source
↓
Parse Once
↓
Schema / malformed-row validation
↓
Type / range / duplicate validation
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
Generated JSON
↓
Unity Config Databases
↓
Runtime Gameplay + HUD
```

Validation covers:

- missing CSV headers, required columns, and required values;
- malformed rows with unexpected extra columns;
- invalid integer / boolean values;
- invalid or suspicious interaction ranges;
- duplicate IDs;
- illegal `interactionType` values;
- unknown `requiredItemId` / `grantedItemId` references;
- supported Interactable `configId` references in `VerticalSlice_01.unity`;
- fail-safe output preservation when validation fails.

Generated outputs:

```text
Assets/Data/interactables.json
Assets/Data/objectives.json
```

Generated JSON is treated as Pipeline output rather than a second hand-maintained source of truth.

### Batch Workflow

The concrete Batch use case is bulk modification of `requiredInteractions`:

```text
batch_interaction_updates.csv
↓
full-batch validation
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source replacement
↓
normal generation
```

Designer-facing CLI:

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

`batch-preview` performs no source modification. `batch-apply` writes `interactables.csv` only after the complete logical batch passes validation.

---

## 3. QA + Scale Evidence

A reusable 40-record Scale Fixture was created:

```text
QA/Fixtures/scale_valid/
├── items.csv                     8 records
├── objectives.csv               12 records
├── interactables.csv            20 records
└── batch_interaction_updates.csv 8 updates
```

The purpose was not to simulate commercial-project scale, but to verify that the Pipeline did not depend on having only a handful of rows.

Scale results:

- valid 40-record generation: PASS;
- 20 Interactables generated correctly;
- 12 Objectives generated correctly;
- 8-record Batch Preview: PASS;
- 8-record Batch Apply: PASS;
- exactly 8 intended `requiredInteractions` fields changed;
- no other Interactable fields changed;
- all 8 expected values propagated into generated JSON.

Bad-data coverage included missing values / columns, duplicate IDs, invalid integer types, invalid ranges, invalid `interactionType`, broken cross-table Item references, broken active-Scene config references, empty CSV input, and malformed CSV rows.

### Real Bug 1 — Active V2 Scene Reference Coverage Gap

A real stale-reference failure was reproduced:

```text
VerticalSlice_01.unity
configId = control_terminal

source ID
control_terminal → control_terminal_renamed
```

Before the fix, generation incorrectly passed even though the active Scene still referenced the old ID.

Root cause: the validator still targeted the V1 baseline Scene and only recognized the old `ConfigurableInteractable` contract.

The validator was updated to target `VerticalSlice_01.unity` and the current config-driven component whitelist:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same broken dependency is now blocked before generation.

Main fix:

```text
97b24be fix: validate active scene config references
```

### Real Bug 2 — Malformed CSV Silent Truncation

An unescaped comma produced an extra CSV value:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` placed the overflow under the `None` key. Before the fix, the Pipeline ignored that value and generated a truncated Objective description while still reporting success.

`validate_schema()` now rejects unexpected extra row values with a row-level ERROR.

Main fix:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

### Fail-Safe Output Evidence

For a missing required value, SHA256 hashes of both generated JSON files were captured before and after failed generation. Both hashes were unchanged:

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

Full reproducible QA evidence: [`D11_QA.md`](D11_QA.md)

---

## 4. Before / After Measurement

The same 40-record fixture and the same 8 intended `requiredInteractions` changes were used for an equivalent-output execution benchmark.

Target updates:

```text
cube_sturdy          3 → 4
power_node           3 → 2
control_terminal     2 → 1
aux_power_box        2 → 3
coolant_pump         3 → 4
sensor_array         4 → 2
backup_generator     5 → 3
maintenance_panel    4 → 5
```

### Manual Path

The manual path required locating and editing the 8 source records, locating the corresponding generated JSON records, applying the same values manually, checking both files, and saving them.

Measured execution time:

```text
192.000 s
```

Independent verification:

```text
CSV records: 20
JSON records: 20
overall: PASS
All 8 intended updates are correct in both CSV and JSON.
No unintended CSV field changes were detected.
```

### Automated Path

```text
batch-preview
→ batch-apply
→ generate
```

Measured with PowerShell `Measure-Command`:

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

This is explicitly an **execution-stage benchmark**. It excludes authoring the Batch request itself and is not a claim that the entire content-production process is 670× faster.

The timing sample produced zero manual errors and zero automated errors, so error-risk reduction is supported separately by the QA evidence rather than inferred from this benchmark.

---

## 5. Before / After Workflow

### Before — Manual Equivalent Output

```text
change request
↓
find target rows manually
↓
edit source values manually
↓
find corresponding generated records manually
↓
edit generated values manually
↓
manually review consistency
↓
Unity Runtime
```

### After — Pipeline Workflow

```text
structured change request
↓
Batch Preview
↓
full-batch validation
↓
Batch Apply
↓
atomic source replacement
↓
normal Pipeline validation
↓
Typed ContentModel
↓
Cross-Table + active-Scene validation
↓
Generated JSON
↓
Unity Runtime
```

Demonstrated benefits:

- deterministic bulk updates;
- validation before generated output is replaced;
- row / field / value-level error localization;
- cross-table and active-Scene reference checks;
- previous known-good generated data preserved on failure;
- generated data remains derived from source rather than becoming a parallel hand-maintained truth.

---

## 6. Trade-offs and Scope Decisions

The project intentionally does not add complexity without demonstrated need. Deferred systems include:

- Unity Editor GUI;
- dependency visualization;
- generalized Quest framework;
- dependency-cycle / unreachable-objective detection;
- all-Scene / all-Prefab scanning;
- a large automated-test framework.

Decision rule:

> Add complexity only when implementation, QA, or workflow evidence demonstrates that it solves a real problem.

Examples:

- Unity Editor integration was skipped because the CLI already exposes Generate / Preview / Apply without additional Editor-only maintenance overhead.
- dependency-cycle / unreachable-objective checks were skipped because the current architecture does not externalize a generalized objective dependency graph.
- active-Scene reference validation was expanded only after QA reproduced a stale-ID failure.
- malformed-row validation was added only after QA reproduced silent content truncation.

---

## 7. Outcome

The final project demonstrates one connected Technical Designer workflow:

```text
Playable Vertical Slice
+
Data-Driven Content
+
Typed Multi-Table Pipeline
+
Validation
+
Batch Automation
+
Scale / QA Evidence
+
Measured Execution Improvement
```

Concrete evidence:

- 40-record Scale Test;
- 8-record Batch Preview / Apply;
- 192 s manual vs 0.287 s automated execution for the controlled 8-record benchmark;
- approximately 670× execution-stage speedup under the stated benchmark scope;
- systematic bad-data QA coverage;
- two real validation defects found and fixed;
- fail-safe generated-output preservation verified by hash comparison;
- tested Windows x64 v1.0.0 standalone release playable from launch to Mission Complete.

The Pipeline's value is not the raw benchmark number alone. It is the combination of faster repetitive execution, earlier error detection, preserved known-good outputs, and a workflow small enough to remain understandable and maintainable.