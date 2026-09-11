# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

> The English README reflects the current Day 11 milestone. The Simplified Chinese version will be synchronized during the final documentation pass.

A Technical Designer portfolio project combining a **playable Unity Vertical Slice** with a **designer-facing content pipeline, validation tooling, batch automation, config-driven runtime behavior, and QA evidence**.

The project is intentionally built as one connected workflow rather than as separate gameplay and tooling exercises.

```text
Designer-facing multi-table CSV
├── items.csv
├── objectives.csv
└── interactables.csv
        ↓
Python parse / validation
        ↓
Typed ContentModel
        ↓
Cross-reference / semantic / active-scene validation
        ↓
Generated Unity JSON
├── interactables.json
└── objectives.json
        ↓
Unity configuration databases
        ↓
Config-driven gameplay + HUD
        ↓
Playable Windows standalone demo
```

The Pipeline also includes a validated Batch workflow for designer-facing interaction tuning and a reusable Day 11 QA fixture for Scale / bad-data testing.

The project is intended to demonstrate:

- gameplay / content implementation;
- data-driven design;
- Python tooling and automation;
- pre-runtime content validation;
- runtime content dependencies;
- end-to-end content-pipeline understanding;
- QA, debugging, and iteration;
- scope / trade-off decisions;
- explainable AI-assisted development.

---

## Current Milestone

**Day 11 — QA + Scale Test is complete.**

The project now combines:

- a presentation-ready indoor Unity Vertical Slice;
- Content Pipeline V2;
- unified CLI workflow;
- validated Batch Preview / Apply;
- Windows standalone delivery;
- a reusable 40-record Scale Fixture;
- reproducible bad-data QA evidence;
- two real validation bugs discovered and fixed through QA.

The original Week 1 prototype remains preserved in:

```text
Assets/Scenes/Prototype_01.unity
```

The current gameplay / build scene is:

```text
Assets/Scenes/VerticalSlice_01.unity
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

The current slice includes:

- an enclosed multi-room industrial-facility layout;
- third-person mouse-controlled camera yaw / pitch with camera-wall shortening;
- player-relative CharacterController WASD movement with gravity;
- generic interaction through `IInteractable`;
- Pickup, Device, and Gate gameplay types;
- minimal ID-based inventory state;
- required-item and prerequisite-device dependencies;
- event-driven gate unlocking and objective progression;
- config-driven Objective content;
- `[E] Interact`, transient Feedback, and Mission Complete HUD presentation;
- basic materials, indoor lighting, room differentiation, and readable interactables;
- persistent world-state feedback for PowerNode, ControlTerminal, and Exit unlock;
- a complete start-to-end mission loop that does not require the Unity Console.

### Presentation / Delivery Result

The first open-graybox timing was `0:27`. After the D10 camera and spatial restructure, the familiar-player timing was measured at `0:46`:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The earlier 5–8 minute target was intentionally **not** forced. Extending the slice through slower movement, long empty corridors, inflated interaction counts, or arbitrary searching would add filler rather than portfolio value. Final unfamiliar-player timing is deferred to the later user-test stage.

A Windows x86-64 standalone build was completed and manually smoke-tested from launch to Mission Complete. Build artifacts remain local and ignored by Git; the repository stores the build configuration, not the binaries.

---

## Quick Start

### Requirements

- Unity 6.3 LTS
- Python 3

### 1. Use the Content Pipeline CLI

Designer-facing sources:

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

Show available commands:

```powershell
py Tools/config_tool.py --help
```

Normal validation + generation:

```powershell
py Tools/config_tool.py
```

or explicitly:

```powershell
py Tools/config_tool.py generate
```

Dry-run Batch Preview:

```powershell
py Tools/config_tool.py batch-preview
```

Apply a validated Batch to designer-facing source data:

```powershell
py Tools/config_tool.py batch-apply
```

After a Batch Apply, run normal generation again to validate and propagate the changed source into Unity data.

If validation succeeds, the Pipeline writes:

```text
Assets/Data/
├── interactables.json
└── objectives.json
```

Current generation behavior:

- `ERROR` blocks generation;
- `WARNING` is reported but does not block generation;
- invalid source data does not overwrite previous valid generated data;
- generated JSON is not manually edited in the normal workflow;
- successful generation prints a concise validation / output summary;
- Batch Preview explicitly confirms that source files were not modified.

### 2. Run the Vertical Slice in Unity

1. Open the project with Unity 6.3 LTS.
2. Open `Assets/Scenes/VerticalSlice_01.unity`.
3. Enter Play Mode.
4. Follow the on-screen objective.
5. Find and pick up the Power Cell in Storage.
6. Repair the Power Node in Maintenance.
7. Activate the Control Terminal.
8. Enter the unlocked Exit area.
9. Reach the EndMarker to complete the mission.

Current gameplay flow:

```text
Find PowerCell
→ Repair PowerNode
→ Activate ControlTerminal
→ Unlock ExitDoor
→ Reach Exit
→ Mission Complete
```

The final build configuration also starts directly in `VerticalSlice_01.unity`.

---

## Gameplay Architecture

### Player / Camera

The current V2 scene uses player-relative movement and a mouse-controlled third-person camera.

```text
Mouse delta
→ camera yaw / pitch
→ player facing

WASD
→ player-relative movement vector
→ normalization
→ CharacterController.Move()
→ gravity
```

The camera follows in `LateUpdate`, clamps pitch, and shortens its distance when solid geometry blocks the normal follow position.

The V2 movement mode is serialized as an opt-in so the preserved V1 baseline can retain its previous behavior.

### Generic Interaction

```text
E / forward Raycast
→ Interactable tag
→ IInteractable
→ object-specific behavior
```

Current implementations:

```text
IInteractable
├── ConfigurableInteractable   (V1 baseline)
├── PickupInteractable         (V2 pickup)
└── DeviceInteractable         (V2 device)
```

### Inventory / Pickup

```text
PowerCell
→ PickupInteractable
→ PlayerInventory
→ grantedItemId = power_cell
```

`PlayerInventory` currently uses a `HashSet<string>` because the slice only needs unique item-ID membership checks.

### Device State / Dependency

`DeviceInteractable` tracks prerequisite satisfaction, interaction progress, and completion.

```text
PlayerInventory has power_cell
→ PowerNode becomes usable
→ power_cell is consumed
→ configured interaction progress
→ PowerNode.Completed
```

ControlTerminal uses an existing serialized prerequisite-device relationship:

```text
PowerNode incomplete
→ ControlTerminal blocked

PowerNode completed
→ ControlTerminal usable
```

### Gate / World-State Presentation

```text
ControlTerminal.Completed
├── GateController → ExitDoor opens
└── CompletionVisualFeedback → Exit frame shows unlocked state
```

`CompletionVisualFeedback` is presentation-only. It subscribes to existing `DeviceInteractable.Completed` events and swaps assigned Renderer material references without changing gameplay state.

Accepted world-state changes:

- PowerNode: warm amber → powered cyan;
- ControlTerminal: cyan → success green;
- Exit: closed Gate → open path with persistent brighter green frame cue.

### Mission / Objective / HUD Flow

Gameplay events determine **when** mission progression occurs; player-facing Objective descriptions come from configuration.

```text
gameplay event
→ objective ID
→ ObjectiveConfigDatabase
→ ObjectiveConfig.description
→ PlayerHUD
```

Current sequence:

```text
Find a Power Cell in Storage
→ Repair the Power Node in Maintenance
→ Activate the Control Terminal
→ Reach the Exit
→ Mission Complete
```

The final HUD presentation includes:

- top-left config-driven Objective card;
- bottom-center `[E] Interact` prompt;
- upper-center transient Feedback card;
- distinct persistent Mission Complete card.

---

## Content Model

Pipeline V2 uses three real designer-facing content tables.

### `items.csv`

Fields:

- `id`
- `displayName`

It is the authoritative registry for Item IDs referenced by interaction content.

### `objectives.csv`

Fields:

- `id`
- `displayName`
- `description`

Objective descriptions are generated into `objectives.json` and loaded by `ObjectiveConfigDatabase`.

Current Demo IDs:

- `find_power_cell`
- `repair_power_node`
- `activate_control_terminal`
- `reach_exit`
- `mission_complete`

### `interactables.csv`

Fields:

- `id`
- `displayName`
- `interactionType`
- `requiredInteractions`
- `requiredItemId`
- `grantedItemId`
- `blockedMessage`
- `completionMessage`
- `deactivateOnComplete`

Current example dependency:

```text
power_cell.grantedItemId = power_cell

power_node.requiredItemId = power_cell
power_node.requiredInteractions = 3
```

The Python Pipeline converts source tables into typed intermediate data:

```text
SourceTable
→ ItemConfig / ObjectiveConfig / InteractableConfig
→ ContentModel
```

The model intentionally stops short of a generalized quest framework. Prerequisite-device relationships and ExitDoor control remain in the existing Unity gameplay architecture where that is currently simpler.

---

## Python Tool / Pipeline V2

Tool entry point:

```text
Tools/config_tool.py
```

Normal-generation flow:

```text
items.csv
+ objectives.csv
+ interactables.csv
        ↓
Parse each source table once
        ↓
SourceTable
        ↓
Schema / malformed-row / type / range / duplicate validation
        ↓
Typed ContentModel
        ↓
interactionType / Item-reference / active-Scene configId validation
        ↓
ERROR / WARNING gate
        ↓
interactables.json + objectives.json
```

Current validation includes:

- missing CSV headers;
- missing required columns / values;
- unexpected extra columns / malformed rows;
- invalid integer / boolean values;
- invalid or suspicious interaction ranges;
- duplicate IDs;
- illegal `interactionType` values;
- unknown `requiredItemId` / `grantedItemId` references;
- `configId` references used by supported Interactable components in `VerticalSlice_01.unity`;
- fail-safe generation behavior.

### Cross-Table Validation Iteration

The concrete V1 → V2 iteration came from a real failure:

```text
power_node.requiredItemId
power_cell → fake_cell
```

Before cross-reference validation, this invalid dependency could reach Unity Runtime. Pipeline V2 now produces:

```text
unknown item reference
→ Python ERROR
→ generation blocked
→ previous valid generated data preserved
→ invalid dependency never reaches runtime
```

A separate valid `backup_cell` test confirmed that the validator still permits valid designer-authored dependency changes.

### Active Scene Reference Validation

Day 11 found that the old Scene-reference validator still targeted the V1 baseline and did not cover the V2 `PickupInteractable` / `DeviceInteractable` `configId` contract.

Reproduced failure:

```text
VerticalSlice_01.unity
configId = control_terminal

source ID
control_terminal → control_terminal_renamed

before fix
→ Validation incorrectly PASSED
```

The validator was updated to target the active `VerticalSlice_01.unity` Scene and an explicit whitelist of config-driven Interactable component types. The same broken reference is now blocked before JSON generation.

### Malformed CSV Validation

Day 11 also found a silent-corruption case: an unescaped comma could create an unexpected extra CSV value, which `DictReader` stored under the `None` key while the Pipeline silently generated a truncated Objective description.

`validate_schema()` now rejects these unexpected extra row values with a row-level ERROR.

---

## Batch V1

The genuine Batch use case is bulk modification of `requiredInteractions`.

Example source:

```text
ConfigSource/batch_interaction_updates.csv
```

The normal Demo Batch example is:

```text
cube_sturdy:       3 → 4
power_node:        3 → 2
control_terminal:  2 → 1
```

Workflow:

```text
batch source
→ full-batch validation
→ typed BatchInteractionUpdate objects
→ preview or apply
→ atomic source-file replacement
→ normal Pipeline V2 generation
→ Unity runtime
```

Any invalid Batch entry rejects the logical Batch before source modification.

Day 11 also verified an 8-record Batch against a 20-Interactable Scale Fixture. Exactly the intended eight `requiredInteractions` fields changed, all other records / fields remained unchanged, and all eight values propagated into generated JSON.

---

## Day 11 QA + Scale Test

Reusable fixture:

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
- malformed CSV rows with unexpected extra values;
- fail-safe generated-output preservation.

Two real defects were found through QA:

```text
Active V2 Scene reference coverage gap
→ FAIL
→ targeted fix
→ regression PASS

Malformed CSV silent truncation
→ FAIL
→ targeted fix
→ regression PASS
```

Full reproducible evidence is documented in:

```text
Docs/D11_QA.md
```

### Fail-Safe Evidence

For a missing required value, SHA256 hashes of both generated JSON files were captured before and after the failed generation. Both hashes remained unchanged.

Verified behavior:

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

### AI-Assisted Development Note

No qualifying AI-generated implementation failure occurred during Day 11, so none was fabricated solely to satisfy a checklist.

Day 11 did include genuine AI-assisted debugging on both QA-discovered defects. The issues were reproduced from concrete inputs, diagnosed, fixed with narrow changes, regression-tested, and integrated into `main`.

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
│   ├── Scripts/
│   └── Settings/
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
│   ├── D10_HANDOFF.md
│   ├── D11_QA.md
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

## Development Log

### Day 1–7 — Pipeline V1 Baseline

Built the first Unity prototype, external config chain, Python CSV → JSON tool, validation layer, end-to-end Pipeline V1, and bilingual Week 1 documentation.

### Day 8 — Gameplay Vertical Slice + Content Model V2 Core

- Created `VerticalSlice_01.unity` and preserved `Prototype_01.unity`.
- Added Pickup / Inventory / Device / Gate / Objective gameplay chain.
- Added generic `IInteractable` interaction and a complete graybox mission loop.
- Expanded config-driven gameplay and discovered the missing cross-record reference-validation problem through the `fake_cell` test.

### Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch

- Added `items.csv`, `objectives.csv`, and typed `ContentModel`.
- Added parse-once source handling, legal interaction-type validation, and Item cross-reference validation.
- Added config-driven Objective descriptions.
- Added validated dry-run / atomic Batch V1 and verified runtime propagation.
- Restored the intended gameplay baseline and completed full regression testing.

### Day 10 — Game Presentation + Tool UX + Standalone Delivery

- Replaced the fixed high camera with mouse-controlled third-person camera behavior and player-relative movement.
- Rebuilt the open graybox into an enclosed indoor facility with real room boundaries, ceilings, doorways, turns, and occlusion.
- Measured pacing and intentionally rejected artificial padding toward the old 5–8 minute target.
- Added facility materials, indoor lighting, room identity, and interactable readability.
- Added persistent PowerNode / ControlTerminal / Exit completion-state presentation.
- Polished Objective / Prompt / Feedback / Mission Complete UI.
- Built and manually smoke-tested the Windows standalone demo from launch to completion.
- Added a unified CLI: `generate`, `batch-preview`, and `batch-apply`.
- Evaluated Unity Editor Integration and intentionally skipped it because the unified CLI already solves the demonstrated workflow problem with much lower maintenance cost.

### Day 11 — QA + Scale Test

- Added and verified a reusable 40-record Scale Fixture.
- Verified larger-data generation and 8-record Batch Preview / Apply behavior.
- Exercised required bad-data categories and fail-safe generation.
- Found an active V2 Scene-reference validation coverage gap and fixed it.
- Found malformed-CSV silent data truncation and fixed it.
- Preserved reproducible QA evidence in `Docs/D11_QA.md`.
- Kept optional cycle / unreachable-objective systems out of scope because the real test data did not justify them.

---

## Current Scope / Known Limitations

Current boundaries are explicit rather than hidden:

- the Vertical Slice is intentionally compact; familiar-player timing is about 46 seconds rather than the retired 5–8 minute target;
- final unfamiliar-player timing is still pending later user testing;
- standalone has no pause / quit menu or in-game resolution settings; these are not required for the current portfolio slice;
- no dedicated sound / VFX pass has been added;
- active-Scene config-reference validation targets `VerticalSlice_01.unity` and the known config-driven Interactable component types; it is not a generalized all-Scene / all-Prefab dependency scanner;
- prerequisite-device relationships remain Unity serialized references rather than externalized content IDs;
- Objective progression order remains event-driven in C#; only player-facing Objective content is configuration-driven;
- no Unity Editor GUI was added because no current workflow evidence justifies the extra process / path / maintenance layer.

---

## Next

### Day 12 — Before / After + Pipeline Case Study

The next milestone reuses the same 40-record fixture for equivalent manual and automated workflows.

Day 12 will:

- time the equivalent manual workflow;
- time the Pipeline / Batch workflow;
- record actual manual misses and automatic catches;
- record the measured efficiency / error-risk difference without pre-selecting a target ratio;
- draw the Before / After pipeline;
- explain pain points, automation scope, remaining manual work, validation coverage, risk reduction, and trade-offs;
- produce Pipeline Case Study V1.

No new gameplay system, content framework, dependency visualizer, or Editor GUI is planned for Day 12.

---

## Documentation

- [`Docs/D10_HANDOFF.md`](Docs/D10_HANDOFF.md) — Day 10 completion record and handoff to QA
- [`Docs/D11_QA.md`](Docs/D11_QA.md) — Day 11 Scale / bad-data QA evidence, bugs, fixes, and D12 handoff
- [`Docs/Pipeline_V1.md`](Docs/Pipeline_V1.md) — Pipeline V1 end-to-end flow and boundaries
- [`Docs/Pipeline_V1.zh-CN.md`](Docs/Pipeline_V1.zh-CN.md) — Simplified Chinese Pipeline V1 documentation
- [`STATUS.md`](STATUS.md) — current project state and next focus
- [`TODO.md`](TODO.md) — 14-day sprint execution checklist

---

## Tech

- Unity 6.3 LTS
- C#
- TextMeshPro
- Python
- CSV / JSON
- Git / GitHub
