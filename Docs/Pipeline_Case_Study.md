# Pipeline Case Study — TD Pipeline Demo

## Overview

This project is a Technical Designer portfolio case built around one connected workflow:

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

The goal was not to build a commercial-scale game or a large general-purpose framework. The goal was to demonstrate how a small playable Unity slice can create real content-production problems, and how a focused tooling layer can reduce repetitive work, catch content errors before Runtime, and preserve a stable designer-facing workflow.

Current stack:

- Unity 6.3 LTS
- C#
- Python
- CSV / JSON
- Git / GitHub

The playable slice uses the chain:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ Mission Complete
```

The content Pipeline supports multi-table source data, typed intermediate models, validation, Batch processing, fail-safe generation, and active-Scene config-reference checks.

---

## 1. Problem

The first version of the project used a small configuration table and a simple CSV → JSON flow. That was sufficient for a minimal prototype, but it became fragile once the gameplay slice introduced real content dependencies.

The main production risks were:

- multiple source tables had to remain structurally valid;
- `requiredInteractions` values needed type / range validation;
- IDs had to remain unique;
- `interactionType` values had to remain legal;
- Interactables could reference Item IDs from another table;
- Unity Scene objects referenced config IDs that could become stale after content renaming;
- repeated parameter edits across multiple records were slow and easy to mistype;
- malformed CSV input could produce incorrect generated content;
- failed validation should not destroy the previous known-good generated data.

A manual workflow also required repetitive lookup and checking across source data and generated data. That work is straightforward at very small scale, but it becomes increasingly error-prone as the number of records and cross-references grows.

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

The three main tables are parsed once into `SourceTable` objects and then converted into typed Python data:

```text
SourceTable
→ ItemConfig
→ ObjectiveConfig
→ InteractableConfig
→ ContentModel
```

This avoids repeatedly reparsing the same CSV files in separate validation functions.

### Validation Flow

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
ERROR gate
↓
Generated JSON
```

Current validation covers:

- missing CSV headers;
- missing required columns and values;
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

Generated JSON is treated as Pipeline output rather than normal designer-authored source.

### Batch Workflow

The current real Batch use case is bulk modification of `requiredInteractions`.

```text
batch_interaction_updates.csv
↓
validate complete batch
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source-file replacement
↓
normal generation
```

Designer-facing CLI:

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

`batch-preview` performs no source modification. `batch-apply` writes `interactables.csv` only after the complete logical batch has passed validation.

---

## 3. QA + Scale Evidence

Day 11 used a reusable 40-record Scale Fixture:

```text
QA/Fixtures/scale_valid/
├── items.csv                    8 records
├── objectives.csv              12 records
├── interactables.csv           20 records
└── batch_interaction_updates.csv 8 updates
```

The purpose was not to simulate commercial-project scale. It was to verify that Pipeline behavior did not depend on having only a few rows.

### Scale Results

- valid 40-record generation: PASS;
- 20 Interactables generated correctly;
- 12 Objectives generated correctly;
- 8-record Batch Preview: PASS;
- 8-record Batch Apply: PASS;
- exactly 8 intended `requiredInteractions` fields changed;
- no other Interactable fields changed;
- all 8 expected values propagated into generated JSON.

### Bad-Data Coverage

The QA pass exercised:

- missing required values;
- missing required columns;
- duplicate IDs;
- invalid integer types;
- invalid ranges;
- invalid `interactionType` values;
- broken cross-table Item references;
- broken active-Scene config references;
- empty CSV input;
- malformed CSV rows.

Two real validation defects were discovered instead of adding new speculative features.

### Bug 1 — Active V2 Scene Reference Coverage Gap

The old validator still targeted the V1 baseline Scene and only recognized the V1 `ConfigurableInteractable` component.

A real failure was reproduced:

```text
VerticalSlice_01.unity
configId = control_terminal

source ID
control_terminal → control_terminal_renamed
```

Before the fix, validation incorrectly passed and generated JSON no longer contained `control_terminal`, while the active Scene still referenced it.

The validator was updated to target `VerticalSlice_01.unity` and an explicit whitelist of config-driven Interactable component types:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same broken reference is now rejected before generation.

### Bug 2 — Malformed CSV Silent Truncation

An unescaped comma created an extra CSV value:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

Python `csv.DictReader` stored the overflow under the `None` key. Before the fix, the Pipeline ignored the overflow, reported success, and generated the truncated description:

```text
Objective: Inspect storage
```

This was a silent data-corruption bug rather than a crash.

`validate_schema()` now rejects unexpected extra row values and reports a row-level error before generation.

### Fail-Safe Output Evidence

For a missing required value, SHA256 hashes of both generated JSON files were captured before and after failed generation.

Both hashes were unchanged.

Verified behavior:

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

Full QA evidence is documented in [`D11_QA.md`](D11_QA.md).

---

## 4. Before / After Measurement

A controlled execution-stage benchmark used the same 40-record Scale Fixture and the same 8 intended `requiredInteractions` changes.

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

### Manual Equivalent-Output Path

The manual benchmark required:

1. locating the 8 target IDs in `ConfigSource/interactables.csv`;
2. editing the 8 `requiredInteractions` values;
3. locating the corresponding records in `Assets/Data/interactables.json`;
4. applying the same 8 changes manually;
5. checking the edited records and saving both files.

Measured time:

```text
192.000 s
```

Independent verification result:

```text
CSV records: 20
JSON records: 20
overall: PASS
All 8 intended updates are correct in both CSV and JSON.
No unintended CSV field changes were detected.
```

### Automated Path

The automated execution path was:

```text
batch-preview
→ batch-apply
→ generate
```

Measured with PowerShell `Measure-Command`:

```text
0.2865603 s
```

Independent verification produced the same PASS result.

### Result

```text
Manual execution:     192.000 s
Automated execution:    0.287 s
Execution speedup:      ~670×
Execution-time reduction: ~99.85%
```

This number is intentionally scoped as an **execution-stage benchmark**.

It does **not** include the time required to author the Batch request itself, and it should not be interpreted as a claim that the entire content-production process is 670× faster.

The useful conclusion is narrower:

> Once a bulk change request is structured, the Pipeline removes almost all repetitive lookup / edit / propagation work from the execution stage while applying the same validation path used by normal generation.

The controlled benchmark produced zero manual errors and zero automated errors. Therefore, error-risk reduction is not inferred from this timing sample. It is supported separately by the Day 11 QA evidence, where invalid data and two real defects were caught before or during Pipeline validation.

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

Risks:

- repeated lookup work;
- missed targets;
- source / generated-data mismatch;
- no systematic pre-Runtime validation;
- silent malformed-data errors may survive manual review.

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

Benefits demonstrated by the current project:

- deterministic bulk updates;
- validation before generated output is replaced;
- row / field / value-level error localization;
- cross-table reference checks;
- active-Scene config-reference checks;
- previous known-good generated data preserved on failure;
- generated data stays derived from source rather than becoming a parallel hand-maintained truth.

---

## 6. Trade-offs and Scope Decisions

Several possible extensions were intentionally not implemented:

- Unity Editor GUI;
- dependency visualization;
- generalized Quest framework;
- dependency-cycle detection;
- unreachable-objective detection;
- all-Scene / all-Prefab scanning;
- large automated-test framework.

The decision rule was simple:

> Add complexity only when the current content or QA produces evidence that the complexity solves a real workflow problem.

Examples:

- Unity Editor integration was skipped because the CLI already exposed Generate / Preview / Apply clearly without adding Python process-launching and Editor-only maintenance overhead.
- dependency-cycle / unreachable-objective checks were skipped because the current architecture does not externalize a generalized objective dependency graph.
- Scene-reference validation was expanded only after QA demonstrated that the active V2 Scene could contain stale config IDs.
- malformed-row validation was added only after QA reproduced silent content truncation.

This kept the project focused on Pipeline reliability rather than feature accumulation.

---

## 7. Outcome

The final project now demonstrates one connected Technical Designer workflow rather than isolated gameplay and scripting exercises:

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
- Windows standalone Vertical Slice playable from launch to Mission Complete.

The main value of the Pipeline is not the raw benchmark number alone. It is the combination of faster repetitive execution, earlier error detection, preserved known-good outputs, and a workflow that remains small enough to explain and maintain.

---

## Interview / Portfolio Summary

A concise explanation of the project:

> I built a Unity Vertical Slice and used its real content dependencies to drive a Python Content Pipeline. The Pipeline parses multi-table CSV into a typed intermediate model, validates schema, values, duplicate IDs, cross-table Item references, and active-Scene config references, then generates Unity-consumable JSON. I added validated atomic Batch updates for repeated interaction tuning, tested the system with a 40-record fixture, and used QA to discover and fix two real validation bugs. In a controlled 8-record execution benchmark, manual equivalent-output editing took 192 seconds while Batch Preview → Apply → Generate took 0.287 seconds; I treat that as execution-stage evidence rather than a claim about the entire production workflow.
