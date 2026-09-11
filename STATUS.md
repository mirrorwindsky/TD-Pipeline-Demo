# Current Status

**Last updated:** 2026-09-11  
**Sprint stage:** Day 11 QA + Scale Test completed; Day 12 Before / After + Pipeline Case Study is next  
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

The project intentionally uses real gameplay-content needs to create real pipeline problems, then solves only the problems demonstrated by implementation, QA, or workflow evidence.

---

## Current Milestone — Day 11 Complete ✅

Day 11 moved the project from feature development to reliability evidence.

Completed outcomes:

- preserved the stable D10 playable / buildable baseline;
- created an isolated `d11-qa` worktree for destructive QA;
- added and preserved a reusable 40-record Scale Fixture;
- verified full-scale generation with 8 Items, 12 Objectives, and 20 Interactables;
- verified an 8-record Batch Preview against the larger Interactable set;
- verified an 8-record Batch Apply changed exactly the intended fields and propagated into generated JSON;
- systematically tested missing values / columns, duplicate IDs, invalid type / range / enum values, broken cross-table references, broken active-scene references, empty input, and malformed CSV rows;
- directly verified fail-safe generation by comparing generated JSON hashes before / after an invalid input;
- found and fixed two real validation defects;
- documented the reproducible QA evidence in `Docs/D11_QA.md`;
- intentionally skipped dependency-cycle / unreachable-objective tooling because the expanded content did not demonstrate a real need.

Reusable Day 11 fixture:

```text
QA/Fixtures/scale_valid/
├── items.csv                    8 records
├── objectives.csv              12 records
├── interactables.csv           20 records
└── batch_interaction_updates.csv 8 updates
```

Total content records used for Scale Test:

```text
40
```

---

## Stable Gameplay Chain

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

Stable configured interaction counts:

```text
power_node        = 3
control_terminal  = 2
```

The normal playable source / generated-data baseline remains restored outside controlled QA work.

---

## Current Designer-Facing Pipeline

```text
ConfigSource/items.csv
+ ConfigSource/objectives.csv
+ ConfigSource/interactables.csv
        ↓
Tools/config_tool.py
        ↓
Parse Once SourceTables
        ↓
Schema / malformed-row / Type / Range / Duplicate Validation
        ↓
Typed ContentModel
        ↓
interactionType / Item Cross-Reference / active Scene configId Validation
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

Current CLI:

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Current normal-generation guarantees verified through QA:

- invalid source data blocks generation;
- previous valid generated JSON remains preserved after validation failure;
- successful generation uses the same typed model used by validation;
- Batch Preview performs no source modification;
- Batch Apply writes the source CSV atomically after full logical validation;
- current active-scene `configId` references are checked before generation for supported Interactable components;
- malformed CSV rows with unexpected extra columns are rejected instead of silently truncating data.

---

## Day 11 QA Summary

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | D10 baseline sanity check in QA worktree | PASS |
| QA-01 | Valid 40-record Scale Generation | PASS |
| QA-02 | 8-record Scale Batch Preview | PASS |
| QA-03 | 8-record Scale Batch Apply + Regeneration | PASS |
| QA-04 | Missing required value + fail-safe output preservation | PASS |
| QA-05 | Duplicate interactable ID | PASS |
| QA-06 | Invalid integer type | PASS |
| QA-07 | Invalid numeric range | PASS |
| QA-08 | Broken cross-table Item reference | PASS |
| QA-09 | Broken active V2 Scene `configId` reference | FAIL → FIXED → PASS |
| QA-10 | Missing required column | PASS |
| QA-11 | Invalid `interactionType` | PASS |
| QA-12 | Empty CSV input | PASS |
| QA-13 | Malformed CSV / unexpected extra column | FAIL → FIXED → PASS |

Full evidence:

```text
Docs/D11_QA.md
```

---

## Real Bug Fix 1 — Active V2 Scene Reference Coverage

### Failure

The pre-D11 validator still scanned the V1 baseline Scene and only recognized `ConfigurableInteractable.configId`.

A real V2 failure was reproduced:

```text
VerticalSlice_01.unity
configId = control_terminal

ConfigSource/interactables.csv
control_terminal -> control_terminal_renamed
```

Before the fix, generation incorrectly reported `Validation: PASSED` and produced JSON without `control_terminal` while the active Scene still referenced the old ID.

### Fix

Unity-reference validation now targets:

```text
Assets/Scenes/VerticalSlice_01.unity
```

and recognizes the current config-driven Interactable component set:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same broken dependency is now rejected before generation.

QA-branch commit:

```text
5fbf998 fix: validate active scene config references
```

Main equivalent:

```text
97b24be fix: validate active scene config references
```

---

## Real Bug Fix 2 — Malformed CSV Silent Truncation

### Failure

A malformed CSV row containing an unescaped comma could be parsed by `csv.DictReader` with unexpected overflow values under the `None` key.

Before the fix, the Pipeline ignored the overflow, reported `Validation: PASSED`, and silently generated a truncated Objective description.

### Fix

`validate_schema()` now detects unexpected extra row values and reports a row-level ERROR with guidance to check for an unescaped comma or mismatched column count.

QA-branch commit:

```text
7d2c058 fix: reject malformed CSV rows with extra columns
```

Main equivalent:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

---

## Day 11 Fail-Safe Evidence

QA-04 captured SHA256 hashes for both generated JSON files before introducing an invalid required value.

After validation failed, both hashes were unchanged.

Verified behavior:

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

This is direct evidence that the Pipeline protects the last known-good generated output instead of partially overwriting it with invalid content.

---

## AI-Assisted Development Note

No qualifying AI-generated implementation failure occurred during Day 11, so none was fabricated solely to satisfy the original checklist.

Day 11 did include genuine AI-assisted debugging on the two QA-discovered defects above. Both were reproduced from concrete inputs, diagnosed, fixed with narrow changes, regression-tested on the 40-record fixture, and integrated into `main`.

Anything used in the README, Case Study, video, or resume must remain independently explainable without Codex.

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

Day 9 established the stable multi-table Pipeline V2:

- `items.csv + objectives.csv + interactables.csv` source model;
- parse-once `SourceTable` architecture;
- typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`;
- schema / type / range / duplicate-ID validation;
- `interactionType` validation;
- Item ID registry and `requiredItemId` / `grantedItemId` cross-reference validation;
- fail-safe generation;
- config-driven Objective descriptions;
- `interactables.json + objectives.json` generation;
- validated Batch Preview / atomic Apply.

The real Day 8 `fake_cell` failure remains the V1 → V2 cross-table validation case.

---

## Completed — Day 10 Presentation + Delivery

Day 10 completed:

- mouse-controlled third-person camera and player-relative movement;
- enclosed indoor facility structure;
- materials, lighting, room differentiation, and interactable readability;
- persistent PowerNode / ControlTerminal / Exit completion-state feedback;
- polished Objective / Prompt / Feedback / Mission Complete HUD;
- familiar-player timing measurement at approximately `0:46`;
- explicit decision not to pad the slice toward the retired 5–8 minute target;
- Windows x86-64 standalone build and manual smoke test;
- unified designer-facing CLI;
- explicit decision not to add unjustified Unity Editor GUI integration.

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

### Protected baseline

```text
Assets/Scenes/Prototype_01.unity
```

### Active presentation / build scene

```text
Assets/Scenes/VerticalSlice_01.unity
```

---

## Coding Practice Progress

- Day 9: LeetCode 994 — Rotting Oranges — completed.
- Day 10: LeetCode 206 — Reverse Linked List — completed.
- Day 10: LeetCode 141 — Linked List Cycle — completed.
- Day 11: LeetCode 2265 — Count Nodes Equal to Average of Subtree — completed.

---

## Next — Day 12 Before / After + Pipeline Case Study

Day 12 should reuse the same 40-record fixture rather than create a new dataset.

Primary next work:

1. define equivalent manual and automated workflows against the same content set;
2. time the real manual workflow;
3. time the Pipeline / Batch workflow;
4. record actual manual misses and automatic catches;
5. record the measured efficiency / error-risk difference without pre-selecting a target ratio;
6. draw the Before / After pipeline;
7. explain pain points, automated steps, remaining manual work, validation coverage, risk reduction, and trade-offs;
8. produce Pipeline Case Study V1.

Reusable fixture:

```text
QA/Fixtures/scale_valid/
```

---

## Current Scope Boundaries

- No new gameplay system is planned for D12–D14 unless later evidence reveals a real blocker.
- No generalized quest framework is planned.
- No dependency visualization is planned without a concrete need.
- No Unity Editor GUI is planned unless later user testing demonstrates a real workflow benefit.
- Unity config-reference validation currently targets the active `VerticalSlice_01.unity` Scene and the known config-driven Interactable component types; it is not a generalized all-Scene / all-Prefab dependency scanner.
- Prerequisite-device relationships remain Unity serialized references.
- Objective progression timing remains event-driven in C#; only player-facing Objective content is data-driven.
- Sound / VFX remain optional and deferred.
- The next priority is **measurement, Case Study, external feedback, resume evidence, video, and applications**, not feature count.
