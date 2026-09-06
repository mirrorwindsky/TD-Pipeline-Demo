# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

A work-in-progress Technical Designer portfolio project exploring **data-driven gameplay, content validation, tooling, and content-pipeline automation** with Unity, C#, and Python.

## Overview

`TD-Pipeline-Demo` combines a small playable Unity prototype with a designer-facing configuration pipeline.

Instead of treating gameplay implementation and tooling as separate exercises, the project connects them into one real workflow:

```text
Designer-facing CSV
        +
Unity Scene references
        ↓
Python preflight validation
        ↓
Validated configuration conversion
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

* Gameplay / content implementation
* Data-driven design
* Python tooling and automation
* Pre-runtime content validation
* Cross-file configuration reference checking
* End-to-end content-pipeline understanding
* Debugging and iteration
* Explainable AI-assisted development

## Current Milestone

**Pipeline V1 is complete and verified end-to-end.**

The current project contains:

* A playable Unity graybox mission loop
* External configuration driving runtime interaction parameters
* Designer-facing CSV source data
* Automatic CSV → JSON conversion
* Schema, type, range, duplicate-ID, and Unity Scene reference validation
* `ERROR` / `WARNING` severity handling
* Fail-safe generation that preserves the previous valid JSON when validation fails
* Runtime configuration lookup through `Dictionary<string, InteractableConfig>`
* A documented and verified source-data-to-runtime pipeline

A real end-to-end verification changed only:

```text
cube_sturdy.requiredInteractions
3 → 5
```

The value propagated through:

```text
CSV
→ Python validation
→ generated JSON
→ Unity config loading
→ runtime gameplay
```

without manually editing generated JSON or modifying gameplay C# code.

The complete playable flow still worked after the data change:

```text
StartGate
→ Config-Driven Objectives
→ Objective Completion
→ Exit Unlock
→ EndMarker
→ Demo Complete
```

## Quick Start

### Requirements

* Unity 6.3 LTS
* Python 3

### 1. Generate Validated Configuration Data

The designer-facing source configuration is:

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

If any `ERROR` is detected:

* JSON generation is stopped
* actionable validation messages are printed
* the previous valid generated JSON is preserved

`WARNING` messages are reported but do not block generation.

### 2. Run the Unity Demo

1. Open the project with Unity 6.3 LTS.
2. Open `Assets/Scenes/Prototype_01.unity`.
3. Enter Play Mode.
4. Walk through `StartGate`.
5. Complete both configurable interaction objectives.
6. After both objectives are complete, the exit opens.
7. Reach `EndMarker` to complete the current demo loop.

Current gameplay flow:

```text
StartGate
→ Config-Driven Objectives
→ Completed Events
→ Exit Unlock
→ EndMarker
→ Demo Complete
```

## Core Pipeline

### Designer-Facing Source

Gameplay configuration is authored in:

```text
ConfigSource/interactables.csv
```

Current fields include:

* `id`
* `displayName`
* `requiredInteractions`
* `deactivateOnComplete`

The CSV is treated as the editable source of truth.

Generated JSON is not intended to be manually edited during the normal workflow.

### Python Tool

The pipeline tool is:

```text
Tools/config_tool.py
```

It currently performs:

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

### Validation

Current validation includes:

* Missing CSV headers
* Missing required columns
* Empty required values
* Invalid integer values
* Invalid boolean values
* Invalid interaction ranges
* Suspicious interaction values
* Duplicate configuration IDs
* Broken Unity Scene `configId` references

Example broken-reference case:

```text
CSV:
cube_sturdy → renamed to cube_sturdy_v2

Unity Scene:
configId = cube_sturdy
```

The Python tool detects that the Scene still references an ID that no longer exists and blocks JSON generation before the invalid configuration reaches Unity runtime.

### Generated Data

Validated source data is converted into:

```text
Assets/Data/interactables.json
```

The transformation is:

```text
CSV strings
↓
Python type conversion
↓
InteractableConfig dataclass
↓
Dictionary representation
↓
JSON
```

### Unity Loading

Unity consumes the generated JSON through `InteractableConfigDatabase`.

```text
interactables.json
↓
TextAsset
↓
InteractableConfigDatabase.Awake()
↓
JsonUtility.FromJson
↓
InteractableConfigCollection
↓
List<InteractableConfig>
↓
Dictionary<string, InteractableConfig>
```

Each `ConfigurableInteractable` contains a serialized `configId` and retrieves its corresponding runtime configuration through the dictionary.

For example:

```text
SturdyCube
↓
configId = cube_sturdy
↓
Dictionary lookup
↓
requiredInteractions = 3
↓
Runtime interaction behavior
```

## Documentation

* [`Docs/Pipeline_V1.md`](Docs/Pipeline_V1.md) — Detailed end-to-end pipeline, validation stages, Unity loading path, runtime flow, verification procedure, and current scope boundaries.
* [`Docs/Pipeline_V1.zh-CN.md`](Docs/Pipeline_V1.zh-CN.md) — Simplified Chinese version.
* [`STATUS.md`](STATUS.md) — Current project status and milestone handoff context.
* [`TODO.md`](TODO.md) — Sprint execution checklist and upcoming work.

## Project Structure

Key project areas:

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   └── interactables.json
│   ├── Prefabs/
│   ├── Scenes/
│   │   └── Prototype_01.unity
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

Python validation, conversion, and pipeline tooling.

### `Assets/Data`

Generated configuration consumed by Unity.

### `Assets/Scripts`

Current gameplay and configuration systems, including:

* Player movement
* Raycast interaction
* Configuration data classes
* Configuration database
* Config-driven interactable behavior
* Mission / objective flow

### `Assets/Scenes`

Contains the active prototype scene:

```text
Prototype_01.unity
```

### `Docs`

Technical and pipeline documentation intended to describe the project itself rather than sprint-management state.

## Current Runtime Behavior

### Player Movement

```text
WASD input
→ movement vector
→ normalization
→ CharacterController.Move()
→ player movement
```

### Interaction

```text
E input
→ forward Physics.Raycast
→ Interactable tag check
→ ConfigurableInteractable.Interact()
```

### Config-Driven Objective

```text
ConfigurableInteractable
→ configId lookup
→ requiredInteractions
→ interaction progress
→ Completed event
```

### Mission Flow

```text
StartTrigger
→ Mission Start
→ Complete 2 Objectives
→ Completed Events
→ DemoFlowController
→ ExitDoor Opens
→ EndTrigger
→ Demo Complete
```

## Tech

* Unity 6.3 LTS
* C#
* Python
* CSV / JSON
* Git / GitHub

## Development Log

### Day 1 — Minimal Unity Prototype

* Set up the Unity 6.3 LTS project
* Created the initial graybox scene
* Implemented WASD movement using `CharacterController`
* Normalized movement input to avoid faster diagonal movement
* Made the player face the movement direction
* Implemented E-key interaction using `Physics.Raycast`
* Added `Interactable` tag checking
* Used Console logging and `Debug.DrawRay` to debug the interaction chain

Verified:

```text
Input
→ Raycast
→ Tag Check
→ Interaction
```

### Day 2 — First Config-Driven Gameplay Chain

* Added external JSON configuration
* Added serializable C# configuration classes
* Loaded JSON using `JsonUtility`
* Stored configuration entries in `List<InteractableConfig>`
* Built `Dictionary<string, InteractableConfig>` for runtime ID lookup
* Added `ConfigurableInteractable`
* Allowed GameObjects to select configuration through `configId`
* Verified configuration values change runtime behavior without rewriting gameplay logic

Initial configuration chain:

```text
interactables.json
→ JsonUtility
→ List<InteractableConfig>
→ Dictionary lookup
→ ConfigurableInteractable
→ Runtime behavior
```

### Day 3 — Python Tool V0

* Added `ConfigSource/interactables.csv`
* Added `Tools/config_tool.py`
* Used `pathlib` for project-relative paths
* Used `csv.DictReader` to read source data
* Added a Python `InteractableConfig` dataclass
* Converted CSV strings into typed values
* Generated Unity-consumable JSON using `json.dump`
* Verified CSV changes propagate through Python and JSON into Unity runtime

First designer-facing pipeline:

```text
CSV Source Data
→ Python Config Tool
→ Generated JSON
→ Unity Config Database
→ Runtime Gameplay
```

### Day 4 — Demo V0

* Built a complete graybox gameplay loop
* Created a reusable `StartGate` Prefab
* Added trigger-based mission start
* Added `Completed` events to configurable interactables
* Added `DemoFlowController`
* Reused QuickCube and SturdyCube as config-driven objectives
* Opened `ExitDoor` after both objectives were completed
* Added `EndTrigger`
* Verified objective completion works in either order
* Verified re-entering StartGate does not restart the mission

Gameplay loop:

```text
Start Trigger
→ Mission Start
→ Complete 2 Config-Driven Objectives
→ Completed Events
→ Exit Unlock
→ End Trigger
→ Demo Complete
```

### Day 5 — Python Tool V1

Upgraded the Python conversion script into a validation-aware content tool.

Added:

* Schema / missing-field validation
* Type validation
* Range validation
* Duplicate-ID validation
* `ERROR` / `WARNING` separation
* Actionable file / row / field error messages
* Unity Scene `configId` reference validation
* Fail-safe generation
* Input normalization before JSON generation

Verified detection of:

* Missing values
* Missing required columns
* Invalid integers
* Invalid ranges
* Invalid booleans
* Duplicate IDs
* Broken Scene references
* Multiple independent validation problems in a single run

### Day 6 — Pipeline V1

Re-verified the complete source-data-to-runtime workflow.

Test:

```text
cube_sturdy.requiredInteractions
3 → 5
```

Procedure:

1. Modified only the designer-facing CSV.
2. Ran `Tools/config_tool.py`.
3. Validation passed.
4. JSON was regenerated automatically.
5. Unity loaded the new configuration.
6. SturdyCube required exactly 5 interactions.
7. Objective completion and exit unlocking still worked.
8. The demo reached `Demo Complete`.
9. Restored the source value to 3 and regenerated the valid baseline.

Added:

```text
Docs/Pipeline_V1.md
```

to document the complete pipeline and its current scope.

### Day 7 — Milestone 1 Wrap-up

Current wrap-up work includes:

* Re-tested Demo V1 and Tool V1 with no blocking errors
* Cleaned Unity template / tutorial assets that were not part of the project
* Updated the Unity Build Scene List to use `Prototype_01.unity`
* Re-ran the Python pipeline successfully after cleanup
* Re-ran the complete Unity gameplay loop successfully after cleanup
* Reorganized project documentation toward an external-reader / portfolio structure

## Current Scope

The current implementation is intentionally small and focused on proving the complete content-production chain.

Known limitations include:

* Scene reference validation currently targets the current prototype scene rather than all Scenes and Prefabs
* Missing or completely malformed source files are not yet handled comprehensively
* Unity-side configuration robustness is still minimal
* The current Python tool is CLI-based
* The gameplay demo is intentionally graybox and mechanically simple
* Validation functions currently read the CSV separately rather than sharing a single parsed intermediate representation

These limitations are treated as future iteration opportunities rather than hidden behind broader claims about the current implementation.

## Next

The first complete Pipeline V1 milestone is now available.

The immediate focus is to finish the Week 1 wrap-up and then reassess the scope and depth of the remaining sprint work before continuing the next implementation phase.
