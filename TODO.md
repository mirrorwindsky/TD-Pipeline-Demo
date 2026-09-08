# TD Pipeline Demo — 14-Day Sprint TODO

> Goal: build one portfolio-ready Technical Designer flagship student case combining a game-like Unity Vertical Slice with a real content-production Pipeline, validation tooling, automation, and measurable workflow improvement.
>
> Core stack for this sprint is frozen: **Unity 6.3 LTS + C# + Python + Git**.

## Day 1–7 — Completed Baseline ✅

- [x] D1 Minimal Unity prototype
- [x] D2 Config-driven runtime chain
- [x] D3 Python CSV → JSON Tool V0
- [x] D4 Demo V0
- [x] D5 Validation-aware Tool V1
- [x] D6 Pipeline V1 end-to-end verification
- [x] D7 Week 1 stabilization + bilingual documentation + V2 plan

---

## Day 8 — Gameplay Vertical Slice + Content Model V2 Core

### Gameplay

- [x] Choose a clear scene theme and player objective
- [x] Build a complete playable graybox mission loop
- [x] Implement Pickup / Device / Gate content types
- [x] Add a cross-object dependency chain
- [x] Add minimal Inventory / Player State
- [x] Add Interaction Prompt
- [x] Add Objective UI
- [x] Add blocked / progress / completion feedback
- [x] Add a final mission-completion trigger
- [x] Ensure the intended flow works without Console dependency

### Player / Scene Foundation

- [x] Preserve `Prototype_01.unity`
- [x] Create `VerticalSlice_01.unity`
- [x] Build a multi-room graybox layout
- [x] Add CharacterController gravity
- [x] Add a smooth follow camera

### Gameplay Architecture

- [x] Introduce `IInteractable`
- [x] Preserve V1 compatibility
- [x] Add `PlayerInventory`
- [x] Add `PickupInteractable`
- [x] Add reusable `DeviceInteractable`
- [x] Add prerequisite-device logic
- [x] Add event-driven `GateController`
- [x] Add event-driven mission / objective flow

### Content Model V2 — Initial Integration

- [x] Expand `InteractableConfig`
- [x] Expand the Python dataclass / JSON output
- [x] Make Pickup and Device behavior load values from config
- [x] Express at least one dependency through source config
- [x] Verify `requiredInteractions: 3 → 5`
- [x] Intentionally test `requiredItemId: power_cell → fake_cell`
- [x] Restore valid source data and re-test the complete flow

### Day 8 Acceptance

- [x] Complete graybox loop works from start to finish
- [x] At least 3 content-object types participate
- [x] At least 1 cross-object dependency exists
- [x] Objective / Prompt / Feedback works
- [x] At least 1 gameplay dependency is source-config-driven
- [x] A real Pipeline V2 limitation was discovered from testing
- [x] DFS / BFS practice covered by previous day's extra problems

> The final timing target, visual presentation, multi-table source model, field cleanup, `interactionType` validation, and cross-reference validation are intentionally moved to D9–D10.

---

## Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch ✅

### Source Model / Architecture

- [x] Decide the minimum useful multi-table split
- [x] Introduce `items.csv`
- [x] Introduce `objectives.csv`
- [x] Keep `interactables.csv` for interaction content
- [x] Keep the content model limited to fields with real runtime / pipeline value
- [x] Read the real source tables through one unified pipeline
- [x] Parse each source table once
- [x] Build a Typed Intermediate Model with `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`
- [x] Make validation and generation reuse parsed / typed representations instead of re-reading source CSV files
- [x] Preserve the existing `interactables.json` runtime contract while adding `objectives.json`

Current designer-facing source model:

    ConfigSource/
    ├── items.csv
    ├── objectives.csv
    ├── interactables.csv
    └── batch_interaction_updates.csv

Current typed content model:

    ContentModel
    ├── items: list[ItemConfig]
    ├── objectives: list[ObjectiveConfig]
    └── interactables: list[InteractableConfig]

### Preserve Existing Validation

- [x] Preserve schema validation
- [x] Preserve type validation
- [x] Preserve range validation
- [x] Preserve duplicate-ID validation
- [x] Preserve `ERROR` / `WARNING`
- [x] Preserve fail-safe generation
- [x] Preserve current Unity scene reference validation until a broader replacement exists

### New Validation

- [x] Validate legal `interactionType` values
- [x] Add a real Item ID registry through `items.csv`
- [x] Reject `requiredItemId = fake_cell` before JSON generation
- [x] Add cross-record / cross-table item-reference validation
- [x] Validate `requiredItemId`
- [x] Validate `grantedItemId`
- [x] Produce clear file / row / field / reference errors

Scope notes:

- prerequisite-device dependency remains a Unity serialized `DeviceInteractable` reference and was not externalized on D9
- Objective IDs are consumed by `VerticalSliceFlowController` through `ObjectiveConfigDatabase`; no `objectiveId` field was added to `interactables.csv`
- unlock-target IDs were not introduced because the current ExitDoor flow is already handled by the existing event-driven `GateController`

### Objective Content Pipeline

- [x] Parse and validate `objectives.csv`
- [x] Add typed `ObjectiveConfig`
- [x] Include objectives in the shared `ContentModel`
- [x] Generate `Assets/Data/objectives.json`
- [x] Add Unity `ObjectiveConfigDatabase`
- [x] Replace hard-coded HUD objective descriptions with ID-based runtime lookup
- [x] Verify a source-only objective text edit changes the Unity HUD without C# changes
- [x] Keep objective progression timing event-driven in C# rather than over-expanding into a data-driven quest system

Verified runtime chain:

    objectives.csv
    → Python parse / validation
    → ObjectiveConfig / ContentModel
    → objectives.json
    → ObjectiveConfigDatabase
    → VerticalSliceFlowController
    → PlayerHUD

### Runtime / Config Integration

- [x] Make multi-table generated data Unity-consumable
- [x] Keep the existing Vertical Slice chain working
- [x] Verify source-only dependency edits change real gameplay behavior
- [x] Verify source-only objective text edits change real HUD content
- [x] Verify invalid references are blocked before runtime
- [x] Complete a full Vertical Slice regression test after restoring the normal baseline

Cross-reference verification:

- `requiredItemId = fake_cell`
  - rejected by Python cross-reference validation
  - JSON generation blocked
  - previous valid generated data preserved

Valid dependency-change verification:

- temporarily added valid Item ID `backup_cell`
- changed `power_node.requiredItemId` from `power_cell` to `backup_cell`
- Python validation succeeded because the reference was valid
- Unity correctly blocked PowerNode after the player picked up only `power_cell`
- restored the normal `power_cell` dependency afterward

Objective source-only verification:

- changed only the `find_power_cell` description in `objectives.csv`
- regenerated configuration data
- Unity HUD displayed the changed objective text
- no gameplay C# modification was required
- restored the normal objective text afterward

### Batch Processing

- [x] Choose one genuine batch-processing use case
- [x] Implement batch modification of `requiredInteractions`
- [x] Add dry-run batch preview
- [x] Convert validated source rows into prepared typed batch updates
- [x] Validate the entire batch before displaying successful preview results
- [x] Reject duplicate or invalid batch targets before application
- [x] Apply valid batches with all-or-nothing behavior
- [x] Write source CSV changes through a temporary file and atomic replace
- [x] Verify one invalid batch entry causes zero source modifications
- [x] Verify one valid batch updates multiple real gameplay parameters
- [x] Propagate batch changes through the normal Pipeline into Unity Runtime

Real Batch V1 verification:

    cube_sturdy.requiredInteractions:      3 → 4
    power_node.requiredInteractions:       3 → 2
    control_terminal.requiredInteractions: 2 → 1

Verified pipeline:

    batch_interaction_updates.csv
    → full-batch validation
    → prepared BatchInteractionUpdate objects
    → atomic update of interactables.csv
    → normal Pipeline V2 validation / generation
    → interactables.json
    → Unity runtime

Unity verified that PowerNode changed from 3 interactions to 2 and ControlTerminal changed from 2 interactions to 1.

The project was then restored to the normal `3 / 3 / 2` gameplay baseline while retaining the Batch V1 workflow and example batch source.

### Day 9 Acceptance

- [x] Multi-table source data generates Unity-consumable output
- [x] `items.csv`, `objectives.csv`, and `interactables.csv` all participate in the real content pipeline
- [x] Cross-reference errors are blocked before runtime
- [x] `requiredItemId = fake_cell` is caught before runtime
- [x] Valid source-config dependency changes alter real gameplay behavior
- [x] Source-only objective edits alter real HUD content
- [x] Generated structured data does not require manual editing
- [x] Batch V1 works on real project data and reaches Unity Runtime
- [x] Full Vertical Slice regression test passes after restoring the baseline
- [x] Solve 1 DFS / BFS problem — LeetCode 994, Rotting Oranges

---

## Day 10 — Game Presentation + Tool UX / Optional Editor Integration

### Gameplay Timing / Presentation

- [ ] Time the current full gameplay loop
- [ ] Adjust pacing toward the approximate 5–8 minute target
- [ ] Improve scene layout / spatial readability
- [ ] Add basic materials / visual differentiation
- [ ] Improve lighting
- [ ] Make interactable objects visually identifiable
- [ ] Add visible state changes
- [ ] Polish Prompt / Objective / Feedback
- [ ] Add sound / VFX only if core work is complete

### Tool UX

- [ ] Improve validation summary
- [ ] Improve error readability / information hierarchy
- [ ] Make the normal designer workflow obvious
- [ ] Reduce unnecessary manual steps

### Optional Unity Editor Integration

- [ ] Only implement if it genuinely shortens the workflow

### Build Verification

- [ ] Update Build Scene configuration to the Vertical Slice
- [ ] Produce a standalone Build
- [ ] Play it from beginning to end
- [ ] Confirm no Console dependency
- [ ] Confirm Pipeline V2 still drives the real Demo

### D10 Hard Acceptance

- [ ] Demo is approximately 5–8 minutes
- [ ] Demo visibly resembles a small game
- [ ] At least 3 content types participate
- [ ] At least 1 config-driven dependency exists
- [ ] Invalid references are detected before runtime
- [ ] Generated data is not manually edited
- [ ] Scene has materials, lighting, spatial structure, UI, prompts, and feedback
- [ ] Current state is visually strong enough for the final demo video
- [ ] Solve 1 basic linked-list / tree problem

---

## Day 11 — QA + Scale Test

- [ ] Prepare roughly 30–50 content records
- [ ] Verify the Pipeline processes the full test set
- [ ] Test missing fields / duplicate IDs / invalid types / invalid ranges
- [ ] Test broken cross-table and Unity references
- [ ] Test empty / malformed input
- [ ] Fix real bugs discovered by QA
- [ ] Record reproducible test cases
- [ ] Preserve and document at least one AI-generated-code failure case
- [ ] Optional: dependency-cycle / unreachable-objective detection
- [ ] Solve 1 basic coding problem

---

## Day 12 — Before / After + Pipeline Case Study

- [ ] Use the same 30–50 records for both workflows
- [ ] Time the equivalent manual workflow
- [ ] Time the automated workflow
- [ ] Record manual misses and automatic catches
- [ ] Record actual efficiency difference
- [ ] Draw Before / After pipeline
- [ ] Explain pain points, automation, remaining manual work, validation, efficiency, bug risk, and trade-offs
- [ ] Produce Pipeline Case Study V1

---

## Day 13 — User Test + TD External Feedback + Resume

- [ ] Ask 1–2 people to use the workflow without live teaching
- [ ] Record confusion / misoperations / unclear wording
- [ ] Iterate based on real feedback
- [ ] Produce Tool / Pipeline V3 if justified
- [ ] Send project material to the Lilith referral senior
- [ ] Ask whether the direction resembles real TD pipeline/tooling work
- [ ] Ask which parts still look student-like / low-value
- [ ] Ask about hiring / HC timing and referral timing
- [ ] Produce or update Resume V1 / V2
- [ ] Add truthful, verifiable project bullets

---

## Day 14 — Final Wrap-up + Formal Applications

> **Do not start new technology or expand feature scope today.**

- [ ] Standalone Demo runs end-to-end
- [ ] Python Pipeline runs end-to-end
- [ ] Full source → validation → generation → Unity → gameplay chain works
- [ ] Clean Git repository
- [ ] Finish English / Chinese README
- [ ] Finish English / Chinese Pipeline documentation
- [ ] Finish Case Study and bilingual version if appropriate
- [ ] Record final 2–4 minute demo video
- [ ] Show both gameplay and Pipeline
- [ ] Show a config-driven gameplay change
- [ ] Show a validation failure before runtime
- [ ] Produce Resume V2
- [ ] Prepare stable portfolio link
- [ ] Finish game-experience materials
- [ ] Expand formal applications
- [ ] Decide Lilith referral timing

---

## Final Acceptance Checklist — V2

### Unity Vertical Slice

- [ ] Demo is approximately 5–8 minutes
- [ ] Demo looks like a small game rather than a test scene
- [ ] Clear objective and complete beginning → middle → ending flow
- [ ] At least 3 different content-object types
- [ ] Prompt / Objective UI / Feedback work without Console
- [ ] Basic materials, lighting, environment layout, and state feedback

### Content Model / Pipeline

- [x] Pipeline processes real multi-table content data
- [x] At least one cross-object / cross-table dependency exists
- [x] Source config changes dependency / gameplay conditions
- [x] Objective content is source-config-driven through the Pipeline
- [x] Schema / type / range / duplicate / cross-reference / Unity-reference errors are detected
- [x] At least one genuine batch operation exists
- [x] Generated Unity data is not manually edited

### Verification / Iteration

- [ ] 30–50 records used for Scale Test
- [x] Real V1 → problem → V2/V3 iteration exists
- [ ] At least one efficiency or error-risk improvement measured
- [ ] Before / After Pipeline documented
- [ ] At least one AI-assisted debugging case documented
- [ ] At least one external feedback cycle completed

### Portfolio / Applications

- [ ] README clearly explains the project
- [ ] Pipeline documentation clearly explains the technical flow
- [ ] Case Study explains problem, solution, validation, and results
- [ ] Core external docs have Chinese / English versions where appropriate
- [ ] Final video shows gameplay and Pipeline
- [ ] Resume V2 contains truthful, verifiable project bullets
- [ ] Stable portfolio link exists
- [ ] Formal applications started / expanded
- [ ] Without Codex, the full data flow, modules, core logic, tool value, and trade-offs can be explained

---

## Sprint Rules — V2

- Keep **Unity 6.3 LTS + C# + Python + Git** as the main stack through D14.
- Do not start a second portfolio project.
- D8–D10 are one continuous Build Sprint.
- Build one small but complete Vertical Slice, not a large game.
- Complexity must come from real content-production needs.
- Editor Tool / GUI / dependency visualization are optional unless they shorten a real workflow.
- D11–D14 must shift from feature expansion to QA, measurement, Case Study, Resume, video, feedback, and applications.
- Finishing early is allowed; do not add low-value features merely to fill time.
- Anything entering README / Case Study / Resume / video must be independently explainable without Codex.
