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

## Day 8 — Gameplay Vertical Slice + Content Model V2 Core ✅

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

---

## Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch ✅

### Source Model / Architecture

- [x] Introduce `items.csv`, `objectives.csv`, and retain `interactables.csv`
- [x] Keep only fields with real runtime / pipeline value
- [x] Read the real source tables through one unified pipeline
- [x] Parse each source table once into `SourceTable`
- [x] Build typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`
- [x] Reuse parsed / typed representations across validation and generation
- [x] Preserve `interactables.json` while adding `objectives.json`

### Validation

- [x] Preserve schema / type / range / duplicate-ID validation
- [x] Preserve `ERROR` / `WARNING` and fail-safe generation
- [x] Preserve current Unity scene-reference validation boundary
- [x] Validate legal `interactionType` values
- [x] Add Item ID registry
- [x] Validate `requiredItemId` and `grantedItemId`
- [x] Reject `requiredItemId = fake_cell` before JSON generation
- [x] Produce clear file / row / field / reference errors

### Objective Content Pipeline

- [x] Parse and validate `objectives.csv`
- [x] Add typed `ObjectiveConfig`
- [x] Generate `Assets/Data/objectives.json`
- [x] Add Unity `ObjectiveConfigDatabase`
- [x] Replace hard-coded HUD descriptions with ID-based runtime lookup
- [x] Verify a source-only Objective edit changes the HUD without C# changes
- [x] Keep progression timing event-driven instead of building a generalized quest system

### Batch Processing

- [x] Implement genuine batch modification of `requiredInteractions`
- [x] Add dry-run preview
- [x] Validate the entire batch before successful preview / apply
- [x] Reject duplicate or invalid targets
- [x] Add typed prepared batch updates
- [x] Apply valid batches with all-or-nothing behavior
- [x] Write source CSV through temporary file + atomic replace
- [x] Verify invalid batch input causes zero source modifications
- [x] Verify valid batch changes multiple real gameplay parameters
- [x] Restore the normal `3 / 3 / 2` baseline after verification

### Day 9 Acceptance

- [x] Multi-table source data generates Unity-consumable output
- [x] Cross-reference errors are blocked before runtime
- [x] Valid source dependency edits alter real gameplay
- [x] Source-only Objective edits alter real HUD content
- [x] Generated data requires no manual editing
- [x] Batch V1 reaches Unity Runtime
- [x] Full Vertical Slice regression passes after restoring baseline
- [x] Solve 1 DFS / BFS problem — LeetCode 994, Rotting Oranges

---

## Day 10 — Game Presentation + Tool UX / Optional Editor Integration ✅

### Gameplay Timing / Presentation

- [x] Time the current full gameplay loop — familiar-player run measured `0:46`
- [x] Diagnose pacing and document the decision **not** to force the old 5–8 minute target through filler
- [x] Replace the fixed high camera with mouse-controlled third-person camera behavior
- [x] Add player-relative movement while preserving the V1 baseline mode
- [x] Improve scene layout / spatial readability with enclosed rooms, ceilings, doorways, turns, and occlusion
- [x] Add basic materials / visual differentiation
- [x] Improve indoor lighting
- [x] Make interactable objects visually identifiable
- [x] Add visible state changes for PowerNode / ControlTerminal / Exit
- [x] Polish Objective / Prompt / Feedback / Mission Complete presentation
- [x] Evaluate sound / VFX and intentionally defer them because core presentation is already sufficient for the current slice

### Tool UX

- [x] Add a concise successful validation / generation summary
- [x] Confirm existing validation errors already provide actionable file / row / field / value context
- [x] Add discoverable `argparse` CLI commands
- [x] Keep the no-argument command backward-compatible with normal generation
- [x] Replace `py -c` Batch entry points with `batch-preview` / `batch-apply`
- [x] Make Preview explicitly state that no source files were changed
- [x] Verify `batch-apply` still performs real source updates, then restore the baseline and regenerate

Current CLI:

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

### Optional Unity Editor Integration

- [x] Evaluate whether Editor Integration genuinely shortens the current workflow
- [x] Intentionally skip Editor GUI integration: the unified CLI solves the demonstrated problem with much lower process / path / maintenance cost

### Build Verification

- [x] Update Build Scene configuration to `VerticalSlice_01.unity`
- [x] Produce a Windows x86-64 standalone Build
- [x] Keep Build artifacts ignored by Git
- [x] Play the standalone executable from beginning to end
- [x] Confirm no Unity Console dependency
- [x] Confirm Pipeline V2 generated data is included in and drives the real standalone Demo
- [x] Confirm `Prototype_01.unity` remains unchanged

### D10 Acceptance

- [x] Duration was measured and the old 5–8 minute target was explicitly retired rather than padded artificially
- [x] Demo visibly resembles a small game rather than a default Unity test scene
- [x] At least 3 content types participate
- [x] At least 1 config-driven dependency exists
- [x] Invalid references are detected before runtime
- [x] Generated data is not manually edited
- [x] Scene has materials, lighting, spatial structure, UI, prompts, feedback, and persistent world-state changes
- [x] Standalone Demo runs from launch to Mission Complete
- [x] Current state is visually strong enough for the later final demo-video pass
- [x] Solve linked-list / tree practice — LeetCode 206 Reverse Linked List + 141 Linked List Cycle

---

## Day 11 — QA + Scale Test ✅

- [x] Prepare roughly 30–50 content records — completed with a reusable 40-record fixture
- [x] Verify the Pipeline processes the full test set
- [x] Test missing fields / duplicate IDs / invalid types / invalid ranges
- [x] Test broken cross-table and active Unity references
- [x] Test empty / malformed input
- [x] Fix real bugs discovered by QA
- [x] Record reproducible test cases in `Docs/D11_QA.md`
- [x] Evaluate optional dependency-cycle / unreachable-objective detection and intentionally skip it because the current architecture did not demonstrate a real need
- [x] Solve 1 basic coding problem — LeetCode 2265, Count Nodes Equal to Average of Subtree

### AI-Assisted Development Note

No qualifying AI-generated implementation failure occurred during Day 11, so no artificial failure case was created solely to satisfy the original checklist.

Day 11 did include genuine AI-assisted debugging work on two QA-discovered defects:

- active `VerticalSlice_01.unity` config-reference validation coverage;
- malformed CSV rows causing silent data truncation.

Both defects were reproduced, diagnosed, fixed, regression-tested, and integrated into `main`.

---

## Day 12 — Before / After + Pipeline Case Study ✅

The original D12 scope was compressed into a single controlled benchmark plus a portfolio-ready Case Study.

- [x] Reuse the same 40-record fixture from D11
- [x] Time an equivalent manual output workflow — `192.000 s`
- [x] Time the automated `batch-preview → batch-apply → generate` execution path — `0.2865603 s`
- [x] Independently verify both outputs — both PASS
- [x] Record actual execution-stage improvement — approximately `670×` speedup / `99.85%` time reduction
- [x] Keep measurement scope explicit: Batch-request authoring time is excluded
- [x] Do not fabricate manual errors; the manual sample completed with 0 detected errors
- [x] Use D11 QA separately as error-risk evidence
- [x] Document Before / After workflow and design trade-offs
- [x] Produce `Docs/Pipeline_Case_Study.md`

---

## Day 13 — External Feedback + Resume — Compressed

The original external-feedback plan was reduced so it does not block applications.

### Scope Decisions

- External user test: **skipped for now** because no suitable tester is currently available.
- Lilith TD feedback: **opportunistic**, not a blocker; project / resume can be sent when the senior has time to review.
- Tool / Pipeline V3: only if later feedback reveals a concrete issue; no speculative expansion now.

### Remaining Deliverables

- [ ] Produce / update Resume V1 / V2
- [ ] Add truthful, verifiable project bullets
- [ ] Prepare a concise interview explanation of the project

---

## Day 14 — Final Wrap-up + Applications — Compressed

> **Do not start new technology or expand feature scope.**

### Project Packaging

- [ ] Run one final `main` Pipeline regression and confirm clean Git state
- [x] Pipeline Case Study exists in `Docs/Pipeline_Case_Study.md`
- [x] Reusable 40-record QA fixture exists in `QA/Fixtures/scale_valid/`
- [x] D11 QA evidence exists in `Docs/D11_QA.md`
- [x] Stable portfolio repository is the GitHub `main` branch
- [x] English README surfaces the final Case Study / benchmark
- Chinese README / bilingual final synchronization: optional follow-up after the resume is usable; not an application blocker
- Final demo video: optional follow-up; not a blocker for producing the resume today

### Applications

- [ ] Produce Resume V2
- [ ] Add stable GitHub project link to resume
- [ ] Start / expand formal applications
- Lilith referral timing: decide independently of whether external feedback arrives

---

## Final Acceptance Checklist — V2

### Unity Vertical Slice

- [x] Compact end-to-end Demo is playable; measured familiar-player duration and scope decision are documented
- [x] Demo looks like a small game rather than a test scene
- [x] Clear objective and complete beginning → middle → ending flow
- [x] At least 3 different content-object types
- [x] Prompt / Objective UI / Feedback work without Console
- [x] Basic materials, lighting, environment layout, and state feedback
- [x] Windows standalone build passes manual smoke test

### Content Model / Pipeline

- [x] Pipeline processes real multi-table content data
- [x] At least one cross-object / cross-table dependency exists
- [x] Source config changes dependency / gameplay conditions
- [x] Objective content is source-config-driven through the Pipeline
- [x] Schema / type / range / duplicate / cross-reference / current Unity-reference errors are detected
- [x] At least one genuine batch operation exists
- [x] Generated Unity data is not manually edited
- [x] Designer-facing CLI exposes generate / preview / apply without internal Python imports

### Verification / Iteration

- [x] 40 records used for Scale Test
- [x] Real V1 → problem → V2 iteration exists
- [x] At least one efficiency improvement measured
- [x] Before / After Pipeline documented
- [x] At least one AI-assisted debugging case documented
- External user feedback is currently unavailable and is not treated as a blocker

### Portfolio / Applications

- [x] README clearly explains the current portfolio state
- [x] Dedicated Pipeline Case Study documents the final technical flow and measured benchmark
- [x] English README surfaces the final Case Study / benchmark
- [ ] Resume V2 contains truthful, verifiable project bullets
- [x] Stable GitHub portfolio repository exists
- [ ] Formal applications started / expanded
- [ ] Without Codex, the full data flow, modules, core logic, tool value, and trade-offs can be explained

---

## Sprint Rules — V2

- Keep **Unity 6.3 LTS + C# + Python + Git** as the main stack through final packaging.
- Do not start a second portfolio project before the current project is usable for applications.
- Do not add low-value features merely because implementation is going smoothly.
- New complexity must solve a demonstrated gameplay, QA, or workflow problem.
- Anything entering README / Case Study / Resume / video must remain independently explainable without Codex.
- From this point, **resume and applications outrank further feature work**.