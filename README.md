# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

A Technical Designer portfolio project combining a **playable Unity Vertical Slice** with a **designer-facing content pipeline, validation tooling, batch automation, and config-driven runtime behavior**.

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
Cross-reference / semantic validation
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

The pipeline also includes a validated batch-modification workflow for designer-facing interaction tuning.

The project is intended to demonstrate:

- gameplay / content implementation;
- data-driven design;
- Python tooling and automation;
- pre-runtime content validation;
- runtime content dependencies;
- end-to-end content-pipeline understanding;
- debugging and iteration;
- scope / trade-off decisions;
- explainable AI-assisted development.

---

## Current Milestone

**Day 10 is complete.** The project now combines a presentation-ready indoor Vertical Slice, Content Pipeline V2, unified CLI workflow, and a verified Windows standalone build.

The original Week 1 prototype remains preserved in:

```text
Assets/Scenes/Prototype_01.unity
```

The current gameplay slice is:

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

### D10 presentation / delivery result

The first open-graybox timing was `0:27`. After the camera and spatial restructure, the familiar-player timing was measured at `0:46`:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The earlier 5–8 minute target was intentionally **not** forced. The measured result showed that the current dependency loop is inherently compact; extending it through slower movement, long empty corridors, inflated interaction counts, or arbitrary searching would add filler rather than portfolio value. Final unfamiliar-player timing is deferred to the later user-test stage.

The final Windows x86-64 standalone build was also completed and manually smoke-tested from launch to Mission Complete. Build artifacts are local and ignored by Git; the repository stores the build configuration, not the binaries.

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

Dry-run batch preview:

```powershell
py Tools/config_tool.py batch-preview
```

Apply a validated batch to designer-facing source data:

```powershell
py Tools/config_tool.py batch-apply
```

After a batch apply, run normal generation again to validate and propagate the changed source into Unity data.

If validation succeeds, the pipeline writes:

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
- batch preview explicitly confirms that source files were not modified.

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

It is the authoritative registry for item IDs referenced by interaction content.

### `objectives.csv`

Fields:

- `id`
- `displayName`
- `description`

Objective descriptions are generated into `objectives.json` and loaded by `ObjectiveConfigDatabase`.

Current IDs:

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

The Python pipeline converts source tables into typed intermediate data:

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

- missing CSV headers;
- missing required columns / values;
- invalid integer / boolean values;
- invalid or suspicious interaction ranges;
- duplicate IDs;
- illegal `interactionType` values;
- unknown `requiredItemId` / `grantedItemId` references;
- existing V1 `ConfigurableInteractable.configId` scene references;
- fail-safe generation behavior.

The concrete V1 → V2 iteration came from a real failure:

```text
power_node.requiredItemId
power_cell → fake_cell
```

Before cross-reference validation, this invalid dependency could reach Unity runtime. Pipeline V2 now produces:

```text
unknown item reference
→ Python ERROR
→ generation blocked
→ previous valid generated data preserved
→ invalid dependency never reaches runtime
```

A separate valid `backup_cell` test confirmed that the validator still permits valid designer-authored dependency changes.

### Batch V1

The genuine batch use case is bulk modification of `requiredInteractions`.

Example source:

```text
ConfigSource/batch_interaction_updates.csv
```

Verified example:

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

Any invalid batch entry rejects the logical batch before source modification. A valid batch was verified to change real runtime interaction counts, after which the project was restored to the normal `3 / 3 / 2` baseline.

Day 10 added a thin `argparse` command layer so designers no longer need to know Python module internals or use `py -c` to reach Batch functions. Existing business logic was retained.

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
├── Docs/
│   ├── D10_HANDOFF.md
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

- Built the first Unity prototype, external config chain, Python CSV → JSON tool, validation layer, end-to-end Pipeline V1, and bilingual Week 1 documentation.

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
- Reconfirmed Pipeline V2 generation and standalone inclusion of generated data.
- Added a unified CLI: `generate`, `batch-preview`, and `batch-apply`.
- Evaluated Unity Editor Integration and intentionally skipped it because the unified CLI already solves the demonstrated workflow problem with much lower maintenance cost.

---

## Current Scope / Known Limitations

Current boundaries are explicit rather than hidden:

- the Vertical Slice is intentionally compact; familiar-player timing is about 46 seconds rather than the retired 5–8 minute target;
- final unfamiliar-player timing is still pending later user testing;
- standalone has no pause / quit menu or in-game resolution settings; these are not required for the current portfolio slice;
- no dedicated sound / VFX pass has been added;
- V1 Unity scene reference validation remains specific to `ConfigurableInteractable.configId`;
- prerequisite-device relationships remain Unity serialized references rather than externalized content IDs;
- Objective progression order remains event-driven in C#; only player-facing Objective content is configuration-driven;
- the Pipeline has not yet undergone the Day 11 30–50-record scale / QA test;
- no Unity Editor GUI was added because no current workflow evidence justifies the extra process / path / maintenance layer.

---

## Next

### Day 11 — QA + Scale Test

The next milestone shifts away from feature expansion and toward evidence:

- prepare roughly 30–50 content records;
- verify the Pipeline on the larger test set;
- systematically test malformed / missing / duplicate / invalid / broken-reference cases;
- record reproducible QA cases and fix only real bugs;
- preserve at least one useful AI-assisted failure / debugging case;
- prepare the evidence needed for Day 12 Before / After measurement and Case Study work.

No new gameplay system, content framework, or Editor GUI is planned unless QA produces a concrete need.

---

## Documentation

- [`Docs/D10_HANDOFF.md`](Docs/D10_HANDOFF.md) — Day 10 completion record, decisions, and handoff to QA
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
