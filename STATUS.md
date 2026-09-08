# Current Status

**Last updated:** 2026-09-08  
**Sprint stage:** Day 9 Multi-Table Pipeline V2 + Cross-Reference + Batch completed
**Repository:** `TD-Pipeline-Demo`

## Current Direction

Primary job target: **Technical Designer**

Current project strategy:

- Unity / C# for a playable game-content Vertical Slice
- Python for validation, conversion, batch processing, and automation
- Git / GitHub for version history
- Codex / AI Coding as an accelerator while keeping all portfolio code explainable

The project is no longer only a standalone gameplay prototype or isolated Python script.

Current direction:

`Game Content Vertical Slice ↔ Content Model ↔ Python Pipeline`

The goal is to let real gameplay-content requirements create real pipeline problems, then solve those problems through tooling and automation.

---

## Completed — Day 1 to Day 6 Baseline

### Day 1 — Minimal Unity Prototype

Completed:

- Unity 6.3 LTS project setup
- CharacterController-based WASD movement
- forward Raycast interaction
- Interactable tag checking
- interaction debugging
- Git / GitHub setup

### Day 2 — Config-Driven Gameplay

Completed:

- serializable C# config data model
- JSON loading through `JsonUtility`
- runtime `List` → `Dictionary<string, InteractableConfig>` lookup
- config-driven interaction behavior
- source config changes altering runtime behavior

### Day 3 — Python Tool V0

Completed:

`ConfigSource/interactables.csv`
`→ Tools/config_tool.py`
`→ Assets/Data/interactables.json`
`→ Unity`
`→ runtime gameplay`

Verified source-only runtime parameter changes.

### Day 4 — Demo V0

Completed the first playable graybox mission loop:

`StartGate`
`→ Config-Driven Objectives`
`→ Exit Unlock`
`→ EndMarker`
`→ Demo Complete`

### Day 5 — Python Tool V1

Added:

- schema validation
- type validation
- range validation
- duplicate-ID validation
- `ERROR` / `WARNING`
- actionable error messages
- Unity Scene reference validation
- fail-safe generation

### Day 6 — Pipeline V1

Verified the complete content-production workflow:

`Designer CSV`
`→ Python Validation`
`→ Generated JSON`
`→ Unity Config Database`
`→ Runtime Config Lookup`
`→ Gameplay`

Verified:

`cube_sturdy.requiredInteractions: 3 → 5`

propagated from source CSV into real runtime behavior without manual JSON edits or gameplay-code changes.

Added:

- `Docs/Pipeline_V1.md`
- Pipeline V1 scope / boundary documentation

---

## Completed — Day 7

### Week 1 Milestone Wrap-up

Completed:

- Demo V1 smoke test
- Tool V1 smoke test
- Unity template / tutorial cleanup
- Build Scene configuration correction
- Python pipeline regression test
- full gameplay-loop regression test
- external-reader / portfolio README restructure
- Simplified Chinese README
- Simplified Chinese Pipeline V1 documentation
- bilingual navigation and documentation synchronization
- sprint-plan V2 redesign

The final Demo video, Resume, and Lilith external feedback were intentionally deferred until after the upgraded Demo V2 / Pipeline V2 milestone.

---

## Completed — Day 8 Core

### Vertical Slice Scene

Created:

`Assets/Scenes/VerticalSlice_01.unity`

Preserved:

`Assets/Scenes/Prototype_01.unity`

as the Pipeline V1 / Week 1 baseline.

Current graybox layout:

`Airlock`
`→ Central Hall`
`→ Storage / Maintenance`
`→ Control`
`→ Exit`

The new scene supports a real gameplay dependency loop rather than the previous two-object test flow.

### Player Foundation Upgrade

Updated the player foundation for a longer playable slice:

- retained CharacterController-based WASD movement
- added gravity
- verified the player falls when leaving valid floor geometry
- added a smooth follow camera using `LateUpdate`

### Generic Interaction Architecture

Introduced:

`IInteractable`

Updated:

`SimpleInteraction`

Current architecture:

`Player`
`→ forward Raycast`
`→ Interactable tag`
`→ IInteractable`
`→ object-specific behavior`

Current implementations include:

- `ConfigurableInteractable` — V1 baseline
- `PickupInteractable` — V2 pickup content
- `DeviceInteractable` — V2 device content

The V1 prototype was regression-tested after the interface refactor and remained functional.

### Inventory / Pickup

Added:

- `PlayerInventory`
- `PickupInteractable`

`PlayerInventory` currently uses:

`HashSet<string>`

for unique item-ID membership.

Verified:

`PowerCell`
`→ PickupInteractable`
`→ PlayerInventory`
`→ power_cell`

The PowerCell disappears after successful pickup.

### Device Interaction

Added reusable:

`DeviceInteractable`

Current device state tracks:

- whether prerequisites are satisfied
- current interaction progress
- completion state

Implemented:

`PowerNode`

Current flow:

`requires power_cell`
`→ consumes power_cell`
`→ 3 interactions`
`→ PowerNode Completed`

Also implemented prerequisite-device behavior.

Current ControlTerminal dependency:

`PowerNode incomplete`
`→ ControlTerminal blocked`

`PowerNode completed`
`→ ControlTerminal usable`

### Gate Flow

Added:

`GateController`

Current event chain:

`ControlTerminal.Completed`
`→ GateController`
`→ ExitDoor unlocked`
`→ Exit path available`

### Player-Facing HUD

Added TextMeshPro HUD:

- `ObjectiveText`
- `FeedbackText`
- `PromptText`

Added:

`PlayerHUD`

Current player-visible feedback includes:

- current objective
- interaction prompt
- missing-requirement feedback
- interaction progress
- completion feedback

The intended gameplay flow can now be completed without depending on Unity Console messages.

### Mission / Objective Flow

Added:

- `VerticalSliceFlowController`
- `VerticalSliceEndTrigger`

Current objective chain:

`Find a Power Cell in Storage`
`→ Repair the Power Node in Maintenance`
`→ Activate the Control Terminal`
`→ Reach the Exit`
`→ Mission Complete`

The mission controller uses gameplay events rather than continuous polling.

### Complete Day 8 Gameplay Chain

Current gameplay dependency chain:

`PowerCell`
`→ PlayerInventory`
`→ PowerNode`
`→ ControlTerminal`
`→ ExitDoor`
`→ EndMarker`
`→ Mission Complete`

This provides:

- Pickup
- Inventory
- Device
- prerequisite Device
- Gate
- UI / Prompt / Feedback
- complete mission ending

---

## Completed — Day 9

### Starting Point: Real Pipeline V2 Failure

Day 8 ended with a real content-production failure rather than a hypothetical feature request.

The source model could already express:

    power_node.requiredItemId = power_cell

but an intentional test changed it to:

    power_node.requiredItemId = fake_cell

The Day 8 tool still generated JSON successfully, and the invalid dependency was only exposed through Unity runtime behavior.

This established the concrete Day 9 problem:

**content dependencies could be authored, but invalid references could not yet be rejected before generation.**

Day 9 upgraded the existing Pipeline V1 / initial Content Model V2 rather than replacing it.

### Multi-Table Source Model

The designer-facing content source is now split into real content domains:

    ConfigSource/
    ├── items.csv
    ├── objectives.csv
    ├── interactables.csv
    └── batch_interaction_updates.csv

Current roles:

- `items.csv` — authoritative Item ID registry
- `objectives.csv` — player-facing objective content
- `interactables.csv` — Pickup / Device interaction content and gameplay parameters
- `batch_interaction_updates.csv` — designer-facing batch modification instructions

The split is intentionally limited to content that currently has real pipeline or runtime value.

No unused quest framework, unlock-target table, dependency graph, or generalized content schema was added.

### Parse Once Architecture

The original tool repeatedly reopened `interactables.csv` for schema, value, duplicate-ID, Unity-reference, and config-loading passes.

Day 9 introduced:

    SourceTable
    ├── path
    ├── fieldnames
    └── rows

Each source CSV is now parsed once into a shared in-memory representation.

Validation and typed-model construction reuse that parsed representation rather than independently re-reading the same source file.

This preserves the original validation behavior while removing repeated source parsing.

### Typed Intermediate Model

The Python pipeline now uses typed content representations:

    ItemConfig
    ObjectiveConfig
    InteractableConfig

combined through:

    ContentModel
    ├── items
    ├── objectives
    └── interactables

The pipeline therefore separates:

    CSV source text
    → SourceTable
    → structural / value validation
    → typed ContentModel
    → semantic / cross-reference validation
    → generated Unity data

This model is shared by generation and semantic validation.

### Preserved Validation

Pipeline V2 preserves the existing Tool V1 validation behavior:

- schema validation
- required-column validation
- required-value validation
- integer type validation
- boolean type validation
- interaction range validation
- unusually high interaction-count warnings
- duplicate-ID validation
- `ERROR` / `WARNING` severity
- fail-safe generation
- existing Unity Scene `ConfigurableInteractable.configId` reference validation

Invalid source data still does not overwrite the previous valid generated runtime data.

### Interaction-Type Validation

Added explicit legal-value validation for:

    interactionType

Current valid runtime-driven values are:

    Pickup
    Device

Values outside the supported set are rejected before generation with file / row / field information.

### Item Registry and Cross-Table Reference Validation

`items.csv` now provides the authoritative Item ID registry.

The tool validates non-empty:

    requiredItemId
    grantedItemId

against real Item IDs before generated data is written.

The original Day 8 failure was re-tested:

    power_node.requiredItemId = fake_cell

Current behavior:

    invalid item reference
    → Python ERROR
    → generation blocked
    → previous valid JSON preserved
    → invalid dependency never reaches Unity runtime

This closes the concrete Pipeline V2 limitation discovered on Day 8.

### Valid Dependency-Change Verification

Cross-reference validation was also tested with a valid dependency rather than only a failure case.

A temporary Item was added:

    backup_cell

Then only the source dependency was changed:

    power_node.requiredItemId
    power_cell → backup_cell

Because `backup_cell` existed in the Item registry:

    validation passed
    → generated data updated
    → Unity loaded the new dependency

The player still acquired only:

    power_cell

so PowerNode correctly remained blocked and displayed the configured missing-item feedback.

The source was then restored to the normal:

    requiredItemId = power_cell

baseline.

This verifies that Cross-Reference Validation does not lock dependencies to fixed values; it permits valid designer-authored dependency changes while rejecting broken references.

### Config-Driven Objective Pipeline

Day 9 also added a real third runtime content table:

    ConfigSource/objectives.csv

Current objective fields:

- `id`
- `displayName`
- `description`

Python now parses and validates objective source data through:

    objectives.csv
    → ObjectiveConfig
    → ContentModel
    → objectives.json

Unity now includes:

- `ObjectiveConfig`
- `ObjectiveConfigCollection`
- `ObjectiveConfigDatabase`

`VerticalSliceFlowController` retains control over when objective progression occurs, but player-facing objective descriptions are now resolved through Objective IDs rather than hard-coded HUD strings.

Current flow:

    gameplay event
    → objective ID
    → ObjectiveConfigDatabase
    → ObjectiveConfig.description
    → PlayerHUD

Source-only verification changed the first objective description in `objectives.csv`, regenerated data, and confirmed the Unity HUD displayed the new text without any C# modification.

The source text was then restored and the normal mission flow was re-tested successfully.

### Generated Runtime Data

The Pipeline currently generates:

    Assets/Data/
    ├── interactables.json
    └── objectives.json

The existing `interactables.json` contract was preserved rather than replaced with a new generalized output format.

Current runtime consumers include:

    InteractableConfigDatabase
    ├── ConfigurableInteractable
    ├── PickupInteractable
    └── DeviceInteractable

and:

    ObjectiveConfigDatabase
    └── VerticalSliceFlowController
        └── PlayerHUD

Generated JSON is never manually edited as part of the normal content workflow.

### Genuine Batch Processing — Batch V1

Day 9 added a real batch-modification workflow for interaction-count tuning.

Designer-facing batch source:

    ConfigSource/batch_interaction_updates.csv

Example batch:

    cube_sturdy.requiredInteractions:      3 → 4
    power_node.requiredInteractions:       3 → 2
    control_terminal.requiredInteractions: 2 → 1

The initial dry-run implementation exposed a usability issue: valid preview lines could be printed before a later invalid row was discovered.

The batch workflow was therefore refined into:

    parse batch source
    → validate entire batch
    → prepare typed BatchInteractionUpdate objects
    → reject whole batch on any ERROR
    → preview only after full validation
    → apply only after full validation

Batch targets and values are checked before application.

Duplicate batch target IDs are also rejected to avoid ambiguous updates.

### Atomic Batch Apply

Valid prepared updates are applied to the parsed `interactables.csv` representation in memory.

The source file is then written through:

    interactables.csv.tmp
    → complete temporary write
    → atomic replace of interactables.csv

The workflow therefore provides two layers of all-or-nothing behavior:

1. any invalid batch entry prevents all logical updates;
2. the original source file is not incrementally overwritten during file writing.

Verified invalid-batch behavior:

    valid row
    + invalid fake_device row
    + valid row
    → ERROR
    → zero source modifications

Verified valid-batch behavior:

    three valid updates
    → all three source values changed
    → normal Pipeline generation
    → interactables.json updated
    → Unity runtime behavior changed

Unity verified:

    PowerNode:       3 interactions → 2
    ControlTerminal: 2 interactions → 1

The project was then restored to the normal gameplay baseline:

    cube_sturdy       = 3
    power_node        = 3
    control_terminal  = 2

while retaining the Batch V1 implementation and example batch source.

### Day 9 Regression Verification

After all Pipeline V2 work, the project was restored to the intended baseline and the complete Vertical Slice was played from beginning to end.

Verified final gameplay chain:

    PowerCell
    → PlayerInventory
    → PowerNode
    → ControlTerminal
    → ExitDoor
    → EndMarker
    → Mission Complete

Verified player-facing flow:

    Find Power Cell
    → Repair Power Node
    → Activate Control Terminal
    → Reach Exit
    → Mission Complete

Confirmed:

- PowerCell pickup works
- PowerNode requires `power_cell`
- PowerNode completes after 3 interactions
- ControlTerminal prerequisite behavior still works
- ControlTerminal completes after 2 interactions
- ExitDoor unlocks correctly
- Objective UI progresses through config-driven objective descriptions
- Prompt / blocked / progress / completion feedback remains functional
- EndMarker completes the mission
- no Console dependency is required to understand the intended flow
- Pipeline V1 baseline scene remains preserved

Day 9 coding warm-up was also completed with LeetCode 994 — Rotting Oranges using BFS.

---

## Current Runtime State

Current gameplay dependency chain:

    PowerCell
    → PlayerInventory
    → PowerNode
    → ControlTerminal
    → ExitDoor
    → EndMarker
    → Mission Complete

Current player-facing layer:

    Config-Driven Objective UI
    + Interaction Prompt
    + Blocked Feedback
    + Progress Feedback
    + Completion Feedback

Current content pipeline:

    items.csv
    + objectives.csv
    + interactables.csv
            ↓
    Parse Once SourceTables
            ↓
    Schema / Type / Range / Duplicate Validation
            ↓
    Typed ContentModel
            ↓
    interactionType / Cross-Table Reference / Unity Reference Validation
            ↓
    ERROR Gate
            ↓
    interactables.json + objectives.json
            ↓
    Unity Config Databases
            ↓
    Runtime Gameplay / HUD

Current optional batch workflow:

    batch_interaction_updates.csv
            ↓
    Full-Batch Validation
            ↓
    Prepared BatchInteractionUpdate objects
            ↓
    Dry-Run Preview or Atomic Apply
            ↓
    interactables.csv
            ↓
    Normal Pipeline V2

Preserved Week 1 baseline:

    Assets/Scenes/Prototype_01.unity

Current Vertical Slice development scene:

    Assets/Scenes/VerticalSlice_01.unity

---

## Current Milestone

Day 9 milestone completed:

**The project now has a real multi-table Content Pipeline V2 that parses source data once, builds a typed intermediate content model, validates gameplay references before runtime, drives both interaction and objective content in Unity, and supports a verified atomic batch-modification workflow.**

The most important V1 → V2 iteration is now complete:

    Day 8:
    requiredItemId = fake_cell
    → generation succeeds
    → failure reaches Unity runtime

    Day 9:
    requiredItemId = fake_cell
    → Cross-Reference ERROR
    → generation blocked
    → invalid dependency never reaches Unity

Pipeline complexity continues to come from real gameplay-content needs rather than standalone tooling features.

---

## Next — Day 10

Main objective:

**Turn the current technically complete graybox Vertical Slice + Pipeline V2 into a presentation-ready Demo V2 without expanding the core gameplay scope.**

Day 10 priorities:

- formally time the complete gameplay loop
- tune pacing toward the approximate 5–8 minute target
- improve room / route readability
- add basic materials and visual differentiation
- improve lighting
- make interactable content visually identifiable
- add visible interaction / completion state changes where useful
- polish Objective / Prompt / Feedback presentation
- produce and test a standalone Build
- confirm Pipeline V2 still drives the final runtime Demo
- improve CLI validation summary / error readability only where it shortens the real workflow
- only add Unity Editor integration if it genuinely reduces designer operation cost

Explicitly avoid:

- new gameplay systems
- generalized quest frameworks
- unnecessary new content tables
- dependency visualization
- Editor GUI work without demonstrated workflow value
- large art-production scope

## Current Blockers

None.

---

## Important Constraints

- Do not replace the existing project with a second portfolio project.
- Keep Unity 6.3 LTS + C# + Python + Git as the main sprint stack.
- Do not expand into a large game.
- D8–D10 are one continuous Build Sprint.
- Pipeline complexity should come from real gameplay-content requirements.
- Editor Tool / GUI work is optional unless it shortens a real designer workflow.
- D11–D14 must shift from feature expansion into QA, measurement, Case Study, Resume, video, external feedback, and applications.
- Any implementation entering portfolio materials must be independently explainable without Codex.
