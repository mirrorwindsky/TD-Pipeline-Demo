# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

A work-in-progress Technical Designer portfolio project exploring **gameplay/content implementation, data-driven design, validation tooling, automation, and content-production pipelines** with Unity, C#, and Python.

## Overview

`TD-Pipeline-Demo` combines a playable Unity gameplay slice with a designer-facing configuration pipeline.

The project is intentionally built as one connected workflow rather than as separate gameplay and tooling exercises:

```text
Designer-facing CSV
        ↓
Python validation / generation
        ↓
Generated JSON
        ↓
Unity configuration loading
        ↓
Runtime config lookup
        ↓
Config-driven gameplay
```

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

**Day 8 core is complete: the project now contains a playable graybox Vertical Slice and the first runtime-integrated Content Model V2.**

The original Week 1 prototype is preserved in:

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
- CSV-driven runtime parameters for pickup/device content

A real source-data verification changed only:

```text
power_node.requiredInteractions
3 → 5
```

Then ran:

```text
CSV
→ Python
→ JSON
→ Unity
```

and verified that the PowerNode required exactly five runtime interactions without manually editing generated JSON or changing gameplay C# code.

A second intentional test changed:

```text
power_node.requiredItemId
power_cell → fake_cell
```

The invalid dependency was accepted by the current generator and only became visible through runtime behavior.

This exposes the next real pipeline problem:

> **Content dependencies can now be expressed in source data, but invalid cross-record references are not yet validated before runtime.**

That limitation is the concrete starting point for Pipeline V2.

---

## Quick Start

### Requirements

- Unity 6.3 LTS
- Python 3

### 1. Generate Configuration Data

The current designer-facing source configuration is:

```text
ConfigSource/interactables.csv
```

From the project root, run:

```powershell
py Tools/config_tool.py
```

If validation succeeds, the tool generates:

```text
Assets/Data/interactables.json
```

Current generation behavior:

- `ERROR` blocks generation
- `WARNING` is reported but does not block generation
- invalid source data does not overwrite the previous valid generated JSON

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

The current player-facing objective sequence is:

```text
Find a Power Cell in Storage
→ Repair the Power Node in Maintenance
→ Activate the Control Terminal
→ Reach the Exit
→ Mission Complete
```

The HUD provides:

- current objective
- interaction prompt
- blocked-condition feedback
- interaction progress feedback
- completion feedback

The intended flow can be understood without reading the Unity Console.

---

## Content Model

The current source file is:

```text
ConfigSource/interactables.csv
```

Current fields include:

- `id`
- `displayName`
- `interactionType`
- `requiredInteractions`
- `requiredItemId`
- `grantedItemId`
- `blockedMessage`
- `completionMessage`
- `deactivateOnComplete`

The current V2 model is still **single-table**.

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

Runtime content retrieves configuration through:

```text
configId
↓
InteractableConfigDatabase
↓
InteractableConfig
```

The same database now supports multiple runtime consumers:

```text
InteractableConfigDatabase
├── ConfigurableInteractable
├── PickupInteractable
└── DeviceInteractable
```

The next Pipeline V2 milestone will introduce stronger source modeling and reference validation rather than continuing to expand the single-table format indefinitely.

---

## Python Tool

The current pipeline tool is:

```text
Tools/config_tool.py
```

The Week 1 validation flow is:

```text
CSV / Unity Scene
↓
Schema Validation
↓
Value / Range Validation
↓
Duplicate-ID Validation
↓
Scene Reference Validation
↓
ERROR / WARNING Gate
↓
Typed Configuration
↓
JSON Generation
```

Current validation includes:

- Missing CSV headers
- Missing required columns
- Missing required field values
- Invalid integer values
- Invalid boolean values
- Invalid interaction ranges
- Suspicious interaction values
- Duplicate IDs
- V1 Unity Scene `configId` references

The current tool does **not yet** validate relationships such as:

```text
requiredItemId = fake_cell
```

against a real item/content registry.

That is a deliberate Pipeline V2 target.

---

## Project Structure

Key project areas:

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   └── interactables.json
│   ├── Prefabs/
│   ├── Scenes/
│   │   ├── Prototype_01.unity
│   │   └── VerticalSlice_01.unity
│   ├── Scripts/
│   └── Settings/
│
├── ConfigSource/
│   └── interactables.csv
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

---

## Current Scope

Known limitations include:

- The current Vertical Slice is still visually graybox
- The final 5–8 minute target has not yet been formally timed
- The current Content Model V2 is still stored in one CSV
- Cross-record references such as `requiredItemId` are not yet validated before runtime
- `interactionType` is stored but not yet validated as a legal enum / value
- V1 Unity reference validation is still specific to the existing `ConfigurableInteractable.configId` structure
- Validation still reads source CSV data in multiple passes instead of using one shared parsed intermediate model
- The Python tool remains CLI-based

These are active iteration targets rather than hidden claims about the current implementation.

---

## Next

### Day 9 — Pipeline V2

The next milestone is to upgrade the current single-table Content Model V2 into a stronger content pipeline.

Planned work includes:

- introduce multi-table source data where it has real value
- parse source data once into a Typed Intermediate Model
- make validation and generation consume the same parsed model
- validate legal `interactionType` values
- add cross-record / cross-table reference validation
- reject invalid IDs such as `requiredItemId = fake_cell` before runtime
- preserve existing schema, type, range, duplicate-ID, and Unity-reference validation
- add at least one genuine batch-processing workflow
