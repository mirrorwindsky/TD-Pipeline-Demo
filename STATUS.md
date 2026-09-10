# Current Status

**Last updated:** 2026-09-10  
**Sprint stage:** Day 10 completed; Day 11 QA + Scale Test is next  
**Repository:** `TD-Pipeline-Demo`

## Current Direction

Primary job target: **Technical Designer**

Current project strategy:

- Unity / C# for a playable game-content Vertical Slice;
- Python for validation, conversion, batch processing, and automation;
- Git / GitHub for version history;
- Codex / AI Coding as an accelerator while keeping all portfolio content explainable.

Current project relationship:

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Pipeline / Validation / Batch Tool
```

The project is intentionally using real gameplay-content needs to create real pipeline problems, then solving those problems with the smallest justified tooling changes.

---

## Current Milestone — Day 10 Complete ✅

Day 10 completed the presentation, delivery, and Tool UX pass on top of the stable Day 9 Pipeline V2.

Current stable gameplay chain:

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

Current designer-facing data flow:

```text
ConfigSource/items.csv
+ ConfigSource/objectives.csv
+ ConfigSource/interactables.csv
        ↓
Tools/config_tool.py
        ↓
Parse Once SourceTables
        ↓
Schema / Type / Range / Duplicate Validation
        ↓
Typed ContentModel
        ↓
interactionType / Item Cross-Reference / current Unity-reference Validation
        ↓
ERROR Gate
        ↓
Assets/Data/interactables.json
+ Assets/Data/objectives.json
        ↓
Unity Config Databases
        ↓
Runtime Gameplay + HUD
        ↓
Windows standalone demo
```

---

## Completed — Day 8 Gameplay Vertical Slice Core

Day 8 established the V2 gameplay slice:

- preserved `Assets/Scenes/Prototype_01.unity` as the V1 baseline;
- created `Assets/Scenes/VerticalSlice_01.unity`;
- introduced `IInteractable` while preserving V1 compatibility;
- added `PlayerInventory`, `PickupInteractable`, and reusable `DeviceInteractable`;
- added Item requirement and prerequisite-device behavior;
- added event-driven `GateController`;
- added Objective / Prompt / Feedback HUD and complete mission flow;
- connected PowerCell / PowerNode behavior to generated config;
- discovered the missing cross-record validation problem through an intentional `fake_cell` dependency test.

---

## Completed — Day 9 Pipeline V2

### Multi-table content model

Current designer-facing sources:

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

Current typed model:

```text
ContentModel
├── items: list[ItemConfig]
├── objectives: list[ObjectiveConfig]
└── interactables: list[InteractableConfig]
```

### Validation / generation

Completed:

- parse-once `SourceTable` architecture;
- schema / type / range / duplicate-ID validation;
- `ERROR` / `WARNING` severity;
- legal `interactionType` validation;
- Item ID registry;
- cross-table `requiredItemId` / `grantedItemId` validation;
- existing V1 scene `ConfigurableInteractable.configId` validation;
- fail-safe generation;
- config-driven Objective descriptions;
- `interactables.json` + `objectives.json` generation.

Verified real failure chain:

```text
requiredItemId = fake_cell
→ Python ERROR
→ generation blocked
→ previous valid generated data preserved
→ invalid dependency never reaches runtime
```

Verified valid dependency changes still propagate correctly through the same pipeline.

### Batch V1

Completed and verified:

```text
batch_interaction_updates.csv
→ full-batch validation
→ prepared BatchInteractionUpdate objects
→ preview or atomic apply
→ interactables.csv
→ normal Pipeline V2 generation
→ Unity runtime
```

A valid batch changed real PowerNode / ControlTerminal interaction counts, then the project was restored to the normal `3 / 3 / 2` baseline.

---

## Completed — Day 10 Presentation + Delivery

### Task 1 — Third-Person Camera + Movement

Completed and user-accepted:

- mouse yaw / pitch with clamping;
- third-person follow camera with collision shortening;
- player-relative W/S movement + A/D strafe in V2;
- V1 movement behavior preserved through an opt-in mode;
- existing forward-Ray `E` interaction preserved.

### Task 2 — Indoor Spatial Restructure

The previous open graybox is now an enclosed facility with:

- ceilings;
- real room boundaries;
- door openings;
- turns / returns;
- occlusion between task stages;
- distinct Storage / Maintenance / Control / Exit spaces.

User manually accepted the new structure and camera behavior.

### Task 3 — Timing / Pacing Decision

Measured familiar-player route:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The old 5–8 minute target was intentionally retired. The project will not add slower movement, long empty corridors, inflated interaction counts, arbitrary searching, or new gameplay systems merely to increase duration.

Final unfamiliar-player timing is deferred to the later user-test stage.

### Task 4 — Materials / Lighting / Readability

Completed and user-accepted:

- restrained industrial-facility URP material language;
- separate floor / wall / ceiling / structural roles;
- Storage / Maintenance / Control / Exit visual differentiation;
- seven local indoor lights;
- interactable readability for PowerCell / PowerNode / ControlTerminal / Exit;
- original Directional Light retained but disabled.

Materials live under:

```text
Assets/Materials/D10Facility/
```

### Task 5A — Visible Completion States

Added:

```text
Assets/Scripts/CompletionVisualFeedback.cs
```

It is presentation-only and subscribes to existing `DeviceInteractable.Completed` events.

Accepted state feedback:

- PowerNode: warm amber → powered cyan;
- ControlTerminal: cyan → success green;
- Exit: Gate opens through the existing `GateController` while the frame / header retains a brighter unlocked-green cue.

Gameplay architecture and interaction counts were not changed.

### Task 5B — HUD / Prompt / Feedback Polish

Completed and user-accepted:

- top-left config-driven Objective card;
- bottom-center `[E] Interact` Prompt;
- transient Feedback card;
- distinct persistent Mission Complete card;
- Canvas Scaler configured for 1920×1080 reference resolution.

Objective content remains config-driven. No UI framework, quest log, inventory UI, results menu, restart flow, or scene transition was introduced.

### Task 6 — Standalone Build + Smoke Test

Windows x86-64 standalone build succeeded.

Final build configuration:

- `VerticalSlice_01.unity` is the sole enabled startup scene;
- `Prototype_01.unity` remains preserved and unchanged;
- Build output is local under `Builds/` and ignored by Git;
- Pipeline V2 was regenerated before the final build;
- generated JSON was confirmed in the standalone build;
- user manually played the executable from launch to Mission Complete with no gameplay / presentation blocker.

Known non-blocking standalone limits:

- no pause / quit menu;
- no in-game resolution settings;
- no restart / results flow.

These are intentionally outside the current portfolio-slice scope.

### Task 7 — Tool UX Decision / CLI Pass

Completed manually on 2026-09-10.

Added a thin `argparse` command layer without rewriting Pipeline business logic.

Current commands:

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Verified:

- no-argument command remains backward-compatible with normal generation;
- `generate` runs the same validation / generation path;
- successful generation prints a concise validation summary;
- `batch-preview` prints validated updates and explicitly states that source files were not changed;
- `batch-apply` still performs real source modification;
- after apply verification, `interactables.csv` was restored and the normal baseline was regenerated;
- final working tree contained only the intended CLI source change before commit.

Unity Editor Integration was evaluated and intentionally skipped. The unified CLI solves the demonstrated workflow problem without introducing Python-process launching, path configuration, output capture, and Editor-only maintenance complexity.

---

## Current Stable Runtime / Tool State

### Runtime

```text
PowerCell pickup
→ inventory `power_cell`
→ PowerNode 3 interactions
→ PowerNode completion state
→ ControlTerminal 2 interactions
→ Terminal completion state
→ Exit Gate opens
→ persistent Exit unlocked cue
→ EndMarker
→ Mission Complete
```

### HUD

```text
Config-Driven Objective
+ [E] Interact Prompt
+ Transient Feedback
+ Mission Complete Presentation
```

### CLI

```text
generate
batch-preview
batch-apply
```

### Protected baseline

```text
Assets/Scenes/Prototype_01.unity
```

---

## Coding Practice Progress

- Day 9: LeetCode 994 — Rotting Oranges — completed.
- Day 10: LeetCode 206 — Reverse Linked List — completed.
- Day 10: LeetCode 141 — Linked List Cycle — completed.
- Day 11: LeetCode 2265 — Count Nodes Equal to Average of Subtree — completed.

---

## Next — Day 11 QA + Scale Test

The project now shifts away from feature expansion.

Next project work:

1. prepare roughly 30–50 content records;
2. verify the Pipeline processes the full test set;
3. systematically test missing fields, duplicate IDs, invalid types / ranges, broken references, empty input, and malformed input;
4. record reproducible QA cases;
5. fix only real bugs revealed by testing;
6. preserve at least one useful AI-generated-code failure / debugging case;
7. prepare stable evidence for Day 12 Before / After measurement and the Pipeline Case Study.

Day 11 coding practice is already complete; the remaining Day 11 work is project QA / scale evidence.

---

## Current Scope Boundaries

- No new gameplay system is planned for D11–D14 unless QA reveals a real blocker.
- No generalized quest framework is planned.
- No dependency visualization is planned without a concrete need.
- No Unity Editor GUI is planned unless later user testing demonstrates a real workflow benefit.
- V1 Unity scene reference validation remains specific to `ConfigurableInteractable.configId`.
- Prerequisite-device relationships remain Unity serialized references.
- Objective progression timing remains event-driven in C#; only player-facing content is data-driven.
- Sound / VFX remain optional and currently deferred.
- The next priority is **QA, measurement, Case Study, external feedback, resume evidence, video, and applications**, not feature count.
