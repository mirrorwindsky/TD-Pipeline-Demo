# Current Status

**Last updated:** 2026-09-07  
**Sprint stage:** Day 8 Gameplay Vertical Slice + Content Model V2 core completed  
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

## Content Model V2 — Initial Single-Table Integration

Expanded `InteractableConfig` beyond the Week 1 four-field model.

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

The Python `InteractableConfig` dataclass and generated JSON now carry the same data.

Current source records include V1 baseline records plus:

- `power_cell`
- `power_node`
- `control_terminal`

`PickupInteractable` and `DeviceInteractable` now retrieve relevant runtime values through:

`InteractableConfigDatabase`

### Source-to-Runtime Verification

Test 1:

Changed only:

`power_node.requiredInteractions: 3 → 5`

Then ran:

`CSV`
`→ Python`
`→ JSON`
`→ Unity`

Verified PowerNode required exactly five interactions.

No manual generated-JSON edit was performed.

No gameplay C# change was required.

Test 2:

Changed only:

`power_node.requiredItemId: power_cell → fake_cell`

The current pipeline generated the invalid dependency successfully.

At runtime, PowerNode could no longer find the required item.

This exposes the next real pipeline limitation:

**source data can now express gameplay dependencies, but invalid cross-record references are not yet validated before runtime.**

After the test, source data was restored to:

- `requiredInteractions = 3`
- `requiredItemId = power_cell`

JSON was regenerated and the complete Vertical Slice was re-tested successfully.

---

## Current Runtime State

Current gameplay chain:

`PowerCell`
`→ PlayerInventory`
`→ PowerNode`
`→ ControlTerminal`
`→ ExitDoor`
`→ EndMarker`
`→ Mission Complete`

Current player-facing layer:

`Objective UI`
`+ Interaction Prompt`
`+ Blocked Feedback`
`+ Progress Feedback`
`+ Completion Feedback`

Current content-data chain:

`ConfigSource/interactables.csv`
`→ Python validation / generation`
`→ Assets/Data/interactables.json`
`→ InteractableConfigDatabase`
`→ Pickup / Device runtime behavior`

Preserved baseline:

`Prototype_01.unity`

Current Vertical Slice development scene:

`VerticalSlice_01.unity`

---

## Current Milestone

Day 8 core milestone completed:

**The project now has a complete graybox gameplay dependency loop with multiple interaction types, Inventory, player-facing HUD, objective progression, and an initial source-config-driven Content Model V2.**

The remaining work has been intentionally moved into the next milestones rather than left as unfinished Day 8 tasks.

### Moved to Day 9

- multi-table source data
- field cleanup based on the real content model
- unified Parse Once architecture
- Typed Intermediate Model
- `interactionType` validation
- cross-record / cross-table reference validation
- catching `requiredItemId = fake_cell` before runtime
- genuine batch processing

### Moved to Day 10

- formal gameplay timing against the 5–8 minute target
- visual presentation beyond graybox
- materials
- lighting
- stronger spatial readability
- UI / feedback polish
- standalone Build verification

---

## Next — Day 9

Main objective:

**Upgrade the current single-table Content Model V2 into Pipeline V2 with unified parsing, stronger source modeling, cross-reference validation, and a genuine batch-processing workflow.**

The first concrete Pipeline V2 failure to solve is:

`requiredItemId = fake_cell`

Expected future behavior:

`invalid source reference`
`→ Python validation ERROR`
`→ generation blocked`
`→ invalid dependency never reaches Unity runtime`

---

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
