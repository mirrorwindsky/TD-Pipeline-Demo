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
- [ ] Solve 1 DFS / BFS problem

> The final timing target, visual presentation, multi-table source model, field cleanup, `interactionType` validation, and cross-reference validation are intentionally moved to D9–D10.

---

## Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch

### Source Model / Architecture

- [ ] Decide the minimum useful multi-table split
- [ ] Introduce `items.csv`
- [ ] Introduce `objectives.csv`
- [ ] Keep `interactables.csv` for interaction content
- [ ] Remove or defer fields that are not actually used
- [ ] Read all source tables through one unified pipeline
- [ ] Parse source data once
- [ ] Build a Typed Intermediate Model
- [ ] Make validation and generation consume the same parsed representation

### Preserve Existing Validation

- [ ] Preserve schema validation
- [ ] Preserve type validation
- [ ] Preserve range validation
- [ ] Preserve duplicate-ID validation
- [ ] Preserve `ERROR` / `WARNING`
- [ ] Preserve fail-safe generation
- [ ] Preserve current Unity reference validation until a broader replacement exists

### New Validation

- [ ] Validate legal `interactionType` values
- [ ] Add item/content ID registry validation
- [ ] Reject `requiredItemId = fake_cell` before JSON generation
- [ ] Add cross-record / cross-table reference validation
- [ ] Validate real references such as:
  - [ ] `requiredItemId`
  - [ ] `grantedItemId`
  - [ ] prerequisite-device references if externalized
  - [ ] `objectiveId` if introduced
  - [ ] unlock-target references if introduced
- [ ] Produce clear file / row / field / reference errors

### Runtime / Config Integration

- [ ] Make multi-table output Unity-consumable
- [ ] Keep the existing Vertical Slice chain working
- [ ] Verify source-only dependency edits change real gameplay
- [ ] Verify invalid references are blocked before runtime

### Batch Processing

- [ ] Choose one genuine batch use case
- [ ] Implement at least one:
  - [ ] Batch validation
  - [ ] Batch modification
  - [ ] Batch export
- [ ] Ensure it solves a real content-production task

### Day 9 Acceptance

- [ ] Multi-table source data generates Unity-consumable output
- [ ] Cross-reference errors are blocked before runtime
- [ ] `requiredItemId = fake_cell` is caught before runtime
- [ ] Source-config changes alter real gameplay dependencies
- [ ] Generated structured data does not require manual editing
- [ ] Batch V1 works on real project data
- [ ] Solve 1 DFS / BFS problem

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

- [ ] Pipeline processes real multi-table content data
- [ ] At least one cross-object / cross-table dependency exists
- [ ] Source config changes dependency / gameplay conditions
- [ ] Schema / type / range / duplicate / cross-reference / Unity-reference errors are detected
- [ ] At least one genuine batch operation exists
- [ ] Generated Unity data is not manually edited

### Verification / Iteration

- [ ] 30–50 records used for Scale Test
- [ ] Real V1 → problem → V2/V3 iteration exists
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
