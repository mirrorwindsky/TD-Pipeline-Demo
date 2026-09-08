# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

A work-in-progress Technical Designer portfolio project exploring **gameplay/content implementation, data-driven design, validation tooling, automation, and content-production pipelines** with Unity, C#, and Python.

## Overview

`TD-Pipeline-Demo` combines a playable Unity gameplay slice with a designer-facing configuration pipeline.

The project is intentionally built as one connected workflow rather than as separate gameplay and tooling exercises:

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
Cross-reference / semantic validation
        ↓
Generated Unity JSON
├── interactables.json
└── objectives.json
        ↓
Unity configuration databases
        ↓
Config-driven gameplay + HUD
```

The pipeline also includes a separate validated batch-modification workflow for designer-facing interaction tuning.

The project is intended to demonstrate:

- Gameplay / content implementation
- Data-driven design
- Python tooling and automation
- Pre-runtime content validation
- Runtime content dependencies
- End-to-end content-pipeline understanding
- Debugging and iteration
- Explainable AI-assisted development

---

## Current Milestone

**Day 9 is complete: the project now combines a playable graybox Vertical Slice with a real multi-table Content Pipeline V2.**

The original Week 1 prototype remains preserved in:

```text
Assets/Scenes/Prototype_01.unity
```

The current gameplay slice is developed in:

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

- A multi-room graybox facility layout
- CharacterController-based movement with gravity
- A smooth follow camera
- Generic interaction through `IInteractable`
- Pickup, Device, and Gate gameplay types
- Minimal ID-based inventory state
- Required-item and prerequisite-device dependencies
- Event-driven gate unlocking
- Interaction Prompt, Objective UI, and Feedback
- Event-driven objective progression
- A complete start-to-end mission loop
- CSV-driven interaction parameters and item dependencies
- CSV-driven player-facing objective descriptions

Pipeline V2 now includes:

- `items.csv`, `objectives.csv`, and `interactables.csv`
- Parse-once source-table loading
- Typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`
- Schema / type / range / duplicate-ID validation
- Legal `interactionType` validation
- Item-ID registry and cross-table reference validation
- Existing Unity scene `configId` reference validation
- Fail-safe generation
- A validated batch-modification workflow with dry-run preview and atomic source-file replacement

The concrete V1 → V2 iteration came from a real Day 8 failure.

An intentional source edit changed:

```text
power_node.requiredItemId
power_cell → fake_cell
```

On Day 8, the invalid dependency reached Unity runtime.

Pipeline V2 now produces:

```text
unknown item reference
→ Python ERROR
→ generation blocked
→ previous valid generated data preserved
→ invalid dependency never reaches runtime
```

A separate valid-reference test introduced a temporary `backup_cell` item and changed only the PowerNode dependency. Validation succeeded and Unity correctly used the new dependency, proving that the pipeline permits valid designer-authored relationship changes while rejecting broken ones.

The Objective pipeline was also verified through a source-only description edit:

```text
objectives.csv
→ Python
→ objectives.json
→ ObjectiveConfigDatabase
→ VerticalSliceFlowController
→ PlayerHUD
```

The changed HUD text appeared in Unity without modifying gameplay C#.

---

## Quick Start

### Requirements

- Unity 6.3 LTS
- Python 3

### 1. Generate Configuration Data

Current designer-facing content sources are:

```text
ConfigSource/
├── items.csv
├── objectives.csv
└── interactables.csv
```

From the project root, run:

```powershell
py Tools/config_tool.py
```

If validation succeeds, the tool generates:

```text
Assets/Data/
├── interactables.json
└── objectives.json
```

Current generation behavior:

- `ERROR` blocks generation
- `WARNING` is reported but does not block generation
- invalid source data does not overwrite the previous valid generated data
- generated JSON is not manually edited as part of the normal workflow

Optional Batch V1 source:

```text
ConfigSource/batch_interaction_updates.csv
```

Dry-run preview:

```powershell
py -c "from Tools.config_tool import run_batch_preview; run_batch_preview()"
```

Apply a validated batch:

```powershell
py -c "from Tools.config_tool import run_batch_apply; run_batch_apply()"
```

Batch application modifies designer-facing `interactables.csv`; the normal generation command is then run to validate and propagate those source changes into Unity data.

### 2. Run the Current Vertical Slice

1. Open the project with Unity 6.3 LTS.
2. Open `Assets/Scenes/VerticalSlice_01.unity`.
3. Enter Play Mode.
4. Follow the on-screen objective.
5. Find and pick up the Power Cell in Storage.
6. Use it to repair the Power Node in Maintenance.
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

The previous `Prototype_01.unity` scene remains available as the Pipeline V1 / Week 1 baseline.

---

## Gameplay Architecture

### Player Movement

```text
WASD
→ movement vector
→ normalization
→ CharacterController.Move()
→ gravity
→ player movement
```

The player rotates toward movement direction.

### Follow Camera

A simple follow camera updates after player movement in `LateUpdate`.

This keeps the player visible while moving through the larger Vertical Slice layout.

### Generic Interaction

The player no longer depends directly on one concrete interaction component.

```text
E / forward Raycast
→ Interactable tag
→ IInteractable
→ object-specific behavior
```

Current implementations include:

```text
IInteractable
├── ConfigurableInteractable   (V1 baseline)
├── PickupInteractable         (V2 pickup)
└── DeviceInteractable         (V2 device)
```

This allows the player interaction code to remain unchanged when new interaction types are added.

### Inventory / Pickup

```text
PowerCell
→ PickupInteractable
→ PlayerInventory
→ grantedItemId = power_cell
```

`PlayerInventory` currently uses a `HashSet<string>` because the current slice only needs unique item-ID membership checks.

### Device State

`DeviceInteractable` currently tracks:

```text
Requirement satisfied?
        ↓
Interaction progress
        ↓
Completed?
```

A device can currently depend on:

- an item ID
- another `DeviceInteractable`
- a configured number of interactions

Current example:

```text
PlayerInventory has power_cell
→ PowerNode becomes usable
→ power_cell is consumed
→ PowerNode interaction progress
→ PowerNode Completed
```

### Device Dependency

The ControlTerminal currently depends on PowerNode completion:

```text
PowerNode incomplete
→ ControlTerminal blocked

PowerNode completed
→ ControlTerminal usable
```

### Gate Flow

`GateController` listens for the ControlTerminal completion event:

```text
ControlTerminal.Completed
→ GateController
→ ExitDoor unlocked
```

### Mission / Objective Flow

Gameplay events still determine when mission progression occurs:

```text
PowerCell picked up
→ PowerNode completed
→ ControlTerminal completed
→ Exit reached
```

Player-facing objective content is now resolved through configuration:

```text
gameplay event
→ objective ID
→ ObjectiveConfigDatabase
→ ObjectiveConfig.description
→ PlayerHUD
```

Current objective IDs / sequence represent:

```text
Find a Power Cell in Storage
→ Repair the Power Node in Maintenance
→ Activate the Control Terminal
→ Reach the Exit
→ Mission Complete
```

This keeps gameplay progression logic simple and event-driven while moving player-facing objective content out of hard-coded C# strings.

The HUD provides:

- current config-driven objective
- interaction prompt
- blocked-condition feedback
- interaction progress feedback
- completion feedback

The intended flow can be understood without reading the Unity Console.

## Content Model

Pipeline V2 uses three real designer-facing content tables:

```text
ConfigSource/
├── items.csv
├── objectives.csv
└── interactables.csv
```

### Items

`items.csv` currently contains:

- `id`
- `displayName`

It acts as the authoritative registry for item IDs referenced by interaction content.

Current example:

```text
power_cell
```

### Objectives

`objectives.csv` currently contains:

- `id`
- `displayName`
- `description`

Objective descriptions are generated into `objectives.json` and loaded by `ObjectiveConfigDatabase`.

Current IDs include:

- `find_power_cell`
- `repair_power_node`
- `activate_control_terminal`
- `reach_exit`
- `mission_complete`

### Interactables

`interactables.csv` currently contains:

- `id`
- `displayName`
- `interactionType`
- `requiredInteractions`
- `requiredItemId`
- `grantedItemId`
- `blockedMessage`
- `completionMessage`
- `deactivateOnComplete`

Current example relationships include:

```text
power_cell
grantedItemId = power_cell
```

and:

```text
power_node
requiredItemId = power_cell
requiredInteractions = 3
```

The Python pipeline converts the source tables into typed intermediate data:

```text
SourceTable
→ ItemConfig / ObjectiveConfig / InteractableConfig
→ ContentModel
```

Runtime interaction content retrieves configuration through:

```text
configId
↓
InteractableConfigDatabase
↓
InteractableConfig
```

Current consumers:

```text
InteractableConfigDatabase
├── ConfigurableInteractable
├── PickupInteractable
└── DeviceInteractable
```

Objective content uses:

```text
objective ID
↓
ObjectiveConfigDatabase
↓
ObjectiveConfig
↓
VerticalSliceFlowController
↓
PlayerHUD
```

The current model intentionally stops short of a generalized quest framework. Prerequisite-device relationships and ExitDoor control remain handled by the existing Unity gameplay architecture where that is currently simpler and more appropriate.

## Python Tool

The current pipeline tool is:

```text
Tools/config_tool.py
```

Pipeline V2 separates raw source parsing, validation, typed content representation, semantic validation, generation, and batch operations.

Current normal-generation flow:

```text
items.csv
+ objectives.csv
+ interactables.csv
        ↓
Parse each source table once
        ↓
SourceTable
        ↓
Schema / type / range / duplicate validation
        ↓
Typed ContentModel
        ↓
interactionType / item-reference / Unity-reference validation
        ↓
ERROR / WARNING gate
        ↓
interactables.json + objectives.json
```

Current validation includes:

- Missing CSV headers
- Missing required columns
- Missing required field values
- Invalid integer values
- Invalid boolean values
- Invalid interaction ranges
- Suspiciously high interaction values
- Duplicate IDs
- Illegal `interactionType` values
- Unknown `requiredItemId` references
- Unknown `grantedItemId` references
- Existing V1 Unity Scene `ConfigurableInteractable.configId` references
- Fail-safe generation behavior

The original Day 8 failure:

```text
requiredItemId = fake_cell
```

is now rejected before generated data reaches Unity.

### Batch V1

The current genuine batch use case is bulk modification of `requiredInteractions`.

Designer-facing batch source:

```text
ConfigSource/batch_interaction_updates.csv
```

Verified example:

```text
cube_sturdy:       3 → 4
power_node:        3 → 2
control_terminal:  2 → 1
```

Batch workflow:

```text
batch source
→ full-batch validation
→ typed BatchInteractionUpdate objects
→ dry-run preview or apply
→ in-memory source update
→ temporary CSV write
→ atomic replace
→ normal Pipeline V2 generation
→ Unity runtime
```

Any invalid batch entry rejects the entire logical batch before source modification.

A valid batch was verified to change multiple real runtime interaction counts, after which the project was restored to the normal `3 / 3 / 2` gameplay baseline.

## Project Structure

Key project areas:

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   ├── interactables.json
│   │   └── objectives.json
│   ├── Prefabs/
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
├── Docs/
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

### `ConfigSource`

Designer-facing source configuration.

### `Tools`

Python validation, conversion, and content-pipeline tooling.

### `Assets/Data`

Generated runtime configuration consumed by Unity.

### `Assets/Scripts`

Gameplay and pipeline integration code, including:

- player movement / gravity
- camera follow
- generic raycast interaction
- inventory
- pickup behavior
- device behavior
- configuration data classes
- configuration database
- gate control
- HUD
- objective / mission flow
- objective configuration data / database
- config-driven objective HUD integration

### `Assets/Scenes`

- `Prototype_01.unity` — Pipeline V1 / Week 1 baseline
- `VerticalSlice_01.unity` — current gameplay Vertical Slice scene

### `Docs`

Technical documentation for the project itself.

---

## Documentation

- [`Docs/Pipeline_V1.md`](Docs/Pipeline_V1.md) — Pipeline V1 end-to-end flow, validation, Unity loading, verification, and current boundaries
- [`Docs/Pipeline_V1.zh-CN.md`](Docs/Pipeline_V1.zh-CN.md) — Simplified Chinese version
- [`STATUS.md`](STATUS.md) — current project state and handoff context
- [`TODO.md`](TODO.md) — current V2 sprint execution checklist

Pipeline V2 documentation will be added after the D9 architecture and validation model are stable.

---

## Tech

- Unity 6.3 LTS
- C#
- TextMeshPro
- Python
- CSV / JSON
- Git / GitHub

---

## Development Log

### Day 1 — Minimal Unity Prototype

- Set up Unity 6.3 LTS, movement, raycast interaction, debugging, and Git.

### Day 2 — First Config-Driven Gameplay Chain

- Added external JSON configuration and runtime dictionary lookup.

### Day 3 — Python Tool V0

- Added designer-facing CSV and CSV → Python → JSON → Unity generation.

### Day 4 — Demo V0

- Built the first complete graybox mission loop.

### Day 5 — Python Tool V1

- Added schema, type, range, duplicate-ID, severity, reference, and fail-safe validation behavior.

### Day 6 — Pipeline V1

- Verified complete source → validation → JSON → Unity → runtime propagation.
- Added `Docs/Pipeline_V1.md`.

### Day 7 — Week 1 Wrap-up

- Stabilized the Week 1 milestone.
- Added bilingual portfolio documentation.
- Rebuilt D8–D14 around Vertical Slice + Pipeline V2.

### Day 8 — Gameplay Vertical Slice + Content Model V2 Core

- Created `VerticalSlice_01.unity`
- Preserved `Prototype_01.unity` as the V1 baseline
- Built a multi-room facility graybox
- Added CharacterController gravity
- Added a smooth follow camera
- Introduced `IInteractable`
- Preserved compatibility with V1 `ConfigurableInteractable`
- Added `PlayerInventory`
- Added `PickupInteractable`
- Added reusable `DeviceInteractable`
- Added item requirements and prerequisite-device logic
- Added event-driven `GateController`
- Added TextMeshPro Objective / Feedback / Prompt HUD
- Added event-driven Vertical Slice objective progression
- Added final mission completion trigger
- Expanded the configuration model with interaction / item / feedback fields
- Connected PowerCell and PowerNode behavior back to CSV-generated data
- Verified `requiredInteractions: 3 → 5` propagates into runtime gameplay
- Intentionally tested `requiredItemId = fake_cell`
- Identified missing cross-record reference validation as the next Pipeline V2 problem

Current Day 8 gameplay chain:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

### Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch

- Split the source model into real Item, Objective, and Interactable content tables
- Reworked CSV handling into parse-once `SourceTable` representations
- Added typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and shared `ContentModel`
- Preserved existing schema, type, range, duplicate-ID, severity, fail-safe, and Unity-reference validation
- Added legal `interactionType` validation
- Added a real Item ID registry
- Added cross-table validation for `requiredItemId` and `grantedItemId`
- Re-tested the Day 8 `fake_cell` failure and confirmed it is now blocked before generation
- Verified a valid temporary `backup_cell` dependency propagates into real gameplay
- Added config-driven objective descriptions through `objectives.csv`, `objectives.json`, and `ObjectiveConfigDatabase`
- Verified source-only Objective text changes appear in the Unity HUD without C# changes
- Added dry-run batch interaction updates
- Refined Batch V1 to validate the entire batch before preview or application
- Added typed prepared batch updates
- Added all-or-nothing batch behavior and temporary-file atomic source replacement
- Verified invalid batch input causes zero source modifications
- Verified a valid three-record batch propagates through the normal Pipeline into Unity runtime
- Restored the intended gameplay baseline and completed a full Vertical Slice regression test

---

## Current Scope

Known limitations / remaining work include:

- The current Vertical Slice is still visually graybox
- The final 5–8 minute gameplay target has not yet been formally timed
- Scene materials, lighting, spatial readability, and visible interaction-state feedback still need D10 presentation work
- V1 Unity Scene reference validation is still specific to `ConfigurableInteractable.configId`
- prerequisite-device relationships remain Unity serialized references rather than externalized content IDs
- Objective progression order remains event-driven in C#; only player-facing objective content is configuration-driven
- Batch operations currently use explicit Python import commands rather than a polished CLI mode
- Validation output is functional but does not yet provide a richer summary / report hierarchy
- The Pipeline has not yet undergone the D11 30–50-record scale test
- No Unity Editor integration has been added because it has not yet demonstrated enough workflow value

These are active scope boundaries rather than hidden claims about the current implementation.

---

## Next

### Day 10 — Game Presentation + Tool UX

The Pipeline V2 core is now complete.

The next milestone is to turn the technically complete graybox Vertical Slice into a presentation-ready Demo V2 without expanding the core gameplay scope.

Planned work includes:

- formally time the full gameplay loop
- tune pacing toward the approximate 5–8 minute target
- improve scene layout and route readability
- add basic materials and visual differentiation
- improve lighting
- make interactable objects visually identifiable
- add useful visible state changes
- polish Objective / Prompt / Feedback presentation
- improve validation summary / error readability where it shortens the real workflow
- produce and test a standalone Build
- confirm Pipeline V2 still drives the final runtime Demo
- only add Unity Editor integration if it genuinely reduces designer operation cost

No new major gameplay system or generalized content framework is planned for Day 10.
