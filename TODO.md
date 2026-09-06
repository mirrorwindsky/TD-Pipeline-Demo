# TD Pipeline Demo — 14-Day Sprint TODO

> Goal: build one portfolio-ready Technical Designer flagship student case combining a game-like Unity Vertical Slice with a real content-production Pipeline, validation tooling, automation, and measurable workflow improvement.
>
> Core stack for this sprint is frozen: **Unity 6.3 LTS + C# + Python + Git**.
> Do not start a second project or switch to UE5 / frontend / RAG during this sprint.

## Day 1 — Environment + Minimal Unity Prototype ✅

- [x] Install and launch Unity 6.3 LTS
- [x] Create `TD-Pipeline-Demo`
- [x] Create project folders: `Scripts`, `Prefabs`, `Data`
- [x] Save `Prototype_01.unity`
- [x] Create a basic graybox scene
- [x] Create `Player` with `CharacterController`
- [x] Implement WASD movement in C#
- [x] Normalize movement vector to avoid faster diagonal movement
- [x] Make Player face movement direction
- [x] Create `InteractableCube`
- [x] Implement E-key raycast interaction
- [x] Add `Interactable` tag
- [x] Add `Debug.DrawRay` and Console logs for interaction debugging
- [x] Verify the full interaction chain: input → raycast hit → tag check → action
- [x] Initialize/connect GitHub repository
- [x] Commit and push project changes
- [x] Create and push `README.md`
- [x] LeetCode #1 Two Sum: brute-force O(n²)
- [x] Rewrite Two Sum using Python `dict` / hash table to average O(n)
- [x] Understand that Python `dict` lookup is average O(1), with extra O(n) space

## Day 2 — First Config → Game Data Chain ✅

- [x] Learn C# `class`
- [x] Learn `List`
- [x] Learn `Dictionary`
- [x] Understand basic serialization
- [x] Define first external config for an enemy or interactable object
- [x] Load external configuration into Unity
- [x] Make configuration values actually change game object behavior
- [x] Confirm config edits can change behavior without rewriting gameplay logic
- [x] Update README with Day 2 progress
- [x] Solve 1 Easy array / HashMap problem

## Day 3 — Python Tool V0 ✅

- [x] Learn `pathlib`
- [x] Learn `csv`
- [x] Learn `json`
- [x] Learn `dataclass`
- [x] Create `config_tool.py`
- [x] Read source CSV data
- [x] Convert CSV into JSON / structured config
- [x] Output generated config to a deterministic path
- [x] Make Unity consume generated data
- [x] Solve 1 Easy HashMap / string problem

## Day 4 — Demo V0 ✅

- [x] Learn basic Prefab workflow
- [x] Learn Trigger / Event basics
- [x] Build a small graybox level
- [x] Implement "enter area"
- [x] Implement a clear objective
- [x] Implement interaction / minimal combat or equivalent action
- [x] Implement completion condition
- [x] Implement visible completion feedback / door opening / ending
- [x] Play the whole demo from start to finish
- [x] Solve 2 leetcode problem

## Day 5 — Python Tool V1

- [x] Add schema / missing-field validation
- [x] Add duplicate-ID validation
- [x] Add invalid-range validation
- [x] Add resource / ID reference validation
- [x] Separate `ERROR` and `WARNING`
- [x] Produce actionable error messages
- [x] Intentionally feed invalid data and verify detection
- [x] Draft first resume bullets for the project
- [x] Solve 1 basic binary-search problem

## Day 6 — Pipeline V1

- [x] Connect the full pipeline:
  - [x] Designer-facing CSV / config
  - [x] Python validator
  - [x] Automatic conversion
  - [x] JSON / structured output
  - [x] Unity import/load
  - [x] Runtime game content
- [x] Verify editing the source config changes real game content
- [x] Fix obvious pipeline bugs
- [x] Draw the first pipeline diagram
- [x] Solve 1 introductory DFS / BFS problem

## Day 7 — Week 1 Milestone Wrap-up ✅

- [x] Re-test Demo V1 for obvious blocking issues
- [x] Re-test Tool V1 for obvious blocking issues
- [x] Clean Unity template / tutorial assets not used by the project
- [x] Update Unity Build Scene List to use `Prototype_01.unity`
- [x] Re-run Python pipeline after cleanup
- [x] Re-run complete Unity gameplay loop after cleanup
- [x] Finalize Pipeline V1 documentation
- [x] Reorganize README into an external-reader / portfolio structure
- [x] Add Simplified Chinese README
- [x] Add Simplified Chinese Pipeline V1 documentation
- [x] Add bilingual navigation and synchronize documentation structure

> Demo video, Resume, and Lilith external feedback were intentionally deferred to D13–D14 after the upgraded Demo V2 is complete.

---

## Day 8 — Gameplay Vertical Slice + Content Model V2

### Gameplay

- [ ] Choose a clear scene theme and player objective
- [ ] Build a 5–8 minute playable content loop
- [ ] Implement at least 3 genuinely different content-object types:
  - [ ] Pickup
  - [ ] Interactable / Device
  - [ ] Gate / Door
- [ ] Add at least one cross-object dependency chain
- [ ] Add minimal Inventory / Player State needed by the dependency chain
- [ ] Add Interaction Prompt
- [ ] Add Objective UI
- [ ] Add insufficient-condition feedback
- [ ] Add completion feedback
- [ ] Ensure the player can understand the whole flow without reading the Unity Console

### Content Model V2

- [ ] Expand the content model beyond the current single-parameter interactable config
- [ ] Introduce multiple content tables where useful:
  - [ ] `items.csv`
  - [ ] `objectives.csv`
  - [ ] `interactables.csv`
- [ ] Add real ID-based relationships between content records
- [ ] Keep only fields that are actually used by the game
- [ ] Ensure at least one gameplay dependency is expressed through source configuration rather than hard-coded logic

### Day 8 Acceptance

- [ ] Complete loop works from start to finish
- [ ] At least 3 content-object types participate in gameplay
- [ ] At least 1 cross-object dependency exists
- [ ] Player-visible objective and interaction feedback works
- [ ] Demo begins to look like a game rather than a test scene
- [ ] Solve 1 DFS / BFS problem

---

## Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch

### Pipeline Architecture

- [ ] Read all source tables through one unified pipeline
- [ ] Parse source data once
- [ ] Build a Typed Intermediate Model
- [ ] Make validation and generation consume the same parsed representation
- [ ] Preserve existing validation:
  - [ ] Schema validation
  - [ ] Type validation
  - [ ] Range validation
  - [ ] Duplicate-ID validation
  - [ ] `ERROR` / `WARNING` separation
  - [ ] Unity Scene reference validation

### New Validation

- [ ] Validate `interactionType` or equivalent enum / legal values
- [ ] Add cross-table reference validation
- [ ] Validate real references such as:
  - [ ] `requiredItemId`
  - [ ] `grantedItemId`
  - [ ] `unlockTargetId`
  - [ ] `objectiveId`
- [ ] Produce clear file / row / field / reference error messages

### Batch Processing

- [ ] Implement at least one genuine batch operation:
  - [ ] Batch validation
  - [ ] Batch modification
  - [ ] Batch export
- [ ] Ensure the batch operation solves a real content-production task

### Intentional Failure Tests

- [ ] Detect a missing item reference
- [ ] Detect a missing objective reference
- [ ] Detect a missing unlock-target reference
- [ ] Detect a duplicate ID
- [ ] Detect an illegal interaction type

### Day 9 Acceptance

- [ ] Multi-table source data generates Unity-consumable output
- [ ] Cross-table errors are blocked before Unity runtime
- [ ] Source-config changes alter real gameplay dependencies
- [ ] Generated structured data does not require manual editing
- [ ] Batch V1 works on real project data
- [ ] Solve 1 DFS / BFS problem

---

## Day 10 — Game Presentation + Tool UX / Optional Editor Integration

### Game Presentation

- [ ] Improve scene layout and spatial readability
- [ ] Add basic materials / visual differentiation
- [ ] Improve lighting
- [ ] Make important interactable objects visually identifiable
- [ ] Add visible state changes for interactable content
- [ ] Polish Interaction Prompt
- [ ] Polish Objective UI
- [ ] Polish feedback text / state feedback
- [ ] Add sound / VFX only if core work is already complete

### Tool UX

- [ ] Improve validation summary
- [ ] Improve error readability and information hierarchy
- [ ] Make the normal designer workflow obvious
- [ ] Reduce unnecessary manual steps

### Optional Unity Editor Integration

Only implement this if it genuinely shortens the content-production workflow.

- [ ] Show Config / Item / Objective counts
- [ ] Show Error / Warning summary
- [ ] Add `Run Validation`
- [ ] Add `Regenerate Data`
- [ ] Optional: search / locate by ID

### Build Verification

- [ ] Produce a standalone Build
- [ ] Play the Build from beginning to end
- [ ] Confirm the player does not need Unity Console to understand game state
- [ ] Confirm Pipeline V2 still drives the real Demo

### D10 Hard Acceptance

- [ ] Demo is approximately 5–8 minutes and visibly resembles a small game
- [ ] At least 3 different content-object types participate in the loop
- [ ] At least 1 cross-object dependency is configuration-driven
- [ ] Editing source configuration changes a real task condition, dependency, or runtime behavior
- [ ] Invalid Item / Objective / UnlockTarget references are detected before Unity runtime
- [ ] Generated data is never manually edited during the normal workflow
- [ ] Scene has basic materials, lighting, spatial structure, UI, prompts, and feedback
- [ ] Current state is visually strong enough to justify recording a final demo later
- [ ] Solve 1 basic linked-list / tree problem

---

## Day 11 — QA + Scale Test

- [ ] Prepare roughly 30–50 content records
- [ ] Verify the Pipeline processes the full test set
- [ ] Test missing fields
- [ ] Test duplicate IDs
- [ ] Test invalid types
- [ ] Test invalid ranges
- [ ] Test broken cross-table references
- [ ] Test broken Unity references
- [ ] Test empty input
- [ ] Test malformed input
- [ ] Fix real bugs discovered by QA
- [ ] Record reproducible test cases
- [ ] Preserve at least one case where AI-generated code was incomplete or wrong
- [ ] Document:
  - [ ] What the AI output missed
  - [ ] How the problem was detected
  - [ ] How it was fixed
  - [ ] How the fix was verified
- [ ] Optional: dependency-cycle detection
- [ ] Optional: unreachable-objective detection
- [ ] Solve 1 basic coding problem

---

## Day 12 — Before / After + Pipeline Case Study

### Quantitative Test

- [ ] Use the same 30–50 content records for both workflows
- [ ] Manually perform the equivalent content-processing task and time it
- [ ] Run the automated workflow and time it
- [ ] Record errors missed during the manual workflow
- [ ] Record errors automatically detected before Unity / runtime
- [ ] Record the actual efficiency difference without inventing a target multiplier

### Case Study

- [ ] Draw the Before pipeline
- [ ] Draw the After pipeline
- [ ] Write the original workflow pain points
- [ ] Explain why tooling was needed
- [ ] Explain what is automated
- [ ] Explain what remains manual
- [ ] Explain the data model and dependency structure
- [ ] Explain validation strategy
- [ ] Explain efficiency change
- [ ] Explain bug-risk change
- [ ] Explain important design trade-offs
- [ ] Produce Pipeline Case Study V1

---

## Day 13 — User Test + TD External Feedback + Resume

### User Test

- [ ] Ask 1–2 people to use the workflow
- [ ] Give each tester a concrete task
- [ ] Do not teach the interface / workflow live
- [ ] Observe where they get stuck
- [ ] Record misoperations
- [ ] Record unclear wording / feedback
- [ ] Modify the tool or workflow based on real feedback
- [ ] Produce Tool / Pipeline V3 if the feedback justifies changes
- [ ] Update the Case Study with the iteration

### TD External Feedback

- [ ] Prepare a concise project summary for the Lilith referral senior
- [ ] Send current project / portfolio material
- [ ] Ask whether the project direction resembles real TD pipeline / tooling work
- [ ] Ask which parts are still too student-like or low-value
- [ ] Ask about current hiring / HC timing
- [ ] Ask whether the referral should be submitted immediately or after one more iteration

### Resume

- [ ] Produce or update Resume V1 / V2
- [ ] Add truthful and verifiable project bullets
- [ ] Include real QA / Batch / quantified results
- [ ] Avoid unsupported efficiency claims
- [ ] Prepare a stable project link

---

## Day 14 — Final Wrap-up + Formal Applications

> **Do not start new technology or expand the feature scope today.**

### Final Project

- [ ] Standalone Demo runs end-to-end
- [ ] Python Pipeline runs end-to-end
- [ ] Full source-data → validation → generation → Unity → gameplay chain runs end-to-end
- [ ] Clean Git repository
- [ ] Finish English README
- [ ] Finish Simplified Chinese README
- [ ] Finish English Pipeline documentation
- [ ] Finish Simplified Chinese Pipeline documentation
- [ ] Finish Case Study
- [ ] Add bilingual Case Study if appropriate
- [ ] Prepare stable portfolio link

### Presentation

- [ ] Record final 2–4 minute demo video
- [ ] Show both:
  - [ ] Game-like Vertical Slice
  - [ ] Tool / Pipeline workflow
- [ ] Show at least one configuration-driven gameplay change
- [ ] Show at least one validation failure before runtime

### Job Search

- [ ] Produce Resume V2
- [ ] Finish personal game-experience table
- [ ] Prepare notes for 3 core / favorite games
- [ ] Finish at least 2 short game / system analyses
- [ ] Expand formal applications
- [ ] Decide Lilith referral timing using D13 feedback

---

## Final Acceptance Checklist — V2

### Unity Vertical Slice

- [ ] Demo is approximately 5–8 minutes
- [ ] Demo visibly resembles a small game rather than a test scene
- [ ] Demo has a clear objective and complete beginning → middle → ending flow
- [ ] At least 3 genuinely different content-object types exist
- [ ] Interaction Prompt / Objective UI / Feedback work without Console dependency
- [ ] Basic materials, lighting, environment layout, and object-state feedback exist

### Content Model / Pipeline

- [ ] Python Pipeline processes the Demo's real multi-table content data
- [ ] At least one real cross-object / cross-table dependency exists
- [ ] Source configuration can change that dependency or gameplay condition
- [ ] Schema errors are detected
- [ ] Type / range errors are detected
- [ ] Duplicate IDs are detected
- [ ] Cross-table reference errors are detected
- [ ] Unity reference errors are detected
- [ ] At least one genuine batch operation exists
- [ ] Generated Unity data is not manually edited in the normal workflow

### Verification / Iteration

- [ ] 30–50 content records have been used for a Scale Test
- [ ] At least one real V1 → problem → V2/V3 iteration exists
- [ ] At least one efficiency or error-risk improvement is measured
- [ ] Before / After Pipeline is documented
- [ ] At least one real AI-assisted debugging case is documented
- [ ] At least one external user or TD feedback cycle is completed

### Portfolio / Applications

- [ ] README clearly explains the project
- [ ] Pipeline documentation clearly explains the technical flow
- [ ] Case Study explains the production problem, solution, validation, and results
- [ ] Core external documentation has Chinese / English versions where appropriate
- [ ] Final 2–4 minute video shows both gameplay and Pipeline
- [ ] Resume V2 contains truthful, verifiable project bullets
- [ ] Stable portfolio link exists
- [ ] Formal applications have started / expanded
- [ ] Without Codex, the complete data flow, major modules, core code logic, tool value, and design trade-offs can be explained

---

## Sprint Rules — V2

- Do not rebuild the project because of a new JD; only adjust feature priority.
- Keep **Unity 6.3 LTS + C# + Python + Git** as the main stack through D14.
- Do not start a second portfolio project during this sprint.
- D8–D10 are one continuous high-intensity Build Sprint rather than isolated tutorial days.
- Do not build a large game; build one small but complete Vertical Slice.
- Complexity must come from real content-production needs rather than architecture for its own sake.
- Editor Tool / GUI / dependency visualization are optional unless they shorten a real workflow.
- D11–D14 must shift from feature expansion to QA, measurement, Case Study, Resume, video, feedback, and applications.
- Finishing early is allowed; do not add low-value features merely to fill time.
- Any implementation entering README / Case Study / Resume / video must be independently explainable without Codex.
