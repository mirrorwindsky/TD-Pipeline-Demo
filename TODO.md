# TD Pipeline Demo — 14-Day Sprint TODO

> Goal: build one portfolio-ready Technical Designer project that demonstrates gameplay/content implementation, tooling, pipeline automation, debugging, and iteration.
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

## Day 4 — Demo V0

- [ ] Learn basic Prefab workflow
- [ ] Learn Trigger / Event basics
- [ ] Build a small graybox level
- [ ] Implement "enter area"
- [ ] Implement a clear objective
- [ ] Implement interaction / minimal combat or equivalent action
- [ ] Implement completion condition
- [ ] Implement visible completion feedback / door opening / ending
- [ ] Play the whole demo from start to finish
- [ ] Solve 1 basic stack / queue problem

## Day 5 — Python Tool V1

- [ ] Add schema / missing-field validation
- [ ] Add duplicate-ID validation
- [ ] Add invalid-range validation
- [ ] Add resource / ID reference validation
- [ ] Separate `ERROR` and `WARNING`
- [ ] Produce actionable error messages
- [ ] Intentionally feed invalid data and verify detection
- [ ] Draft first resume bullets for the project
- [ ] Solve 1 basic binary-search problem

## Day 6 — Pipeline V1

- [ ] Connect the full pipeline:
  - [ ] Designer-facing CSV / config
  - [ ] Python validator
  - [ ] Automatic conversion
  - [ ] JSON / structured output
  - [ ] Unity import/load
  - [ ] Runtime game content
- [ ] Verify editing the source config changes real game content
- [ ] Fix obvious pipeline bugs
- [ ] Draw the first pipeline diagram
- [ ] Solve 1 introductory DFS / BFS problem

## Day 7 — Milestone 1: Mandatory Wrap-up

> **Do not learn new technology today.**

- [ ] Fix obvious Demo V1 bugs
- [ ] Fix obvious Tool V1 bugs
- [ ] Clean project structure
- [ ] Update README
- [ ] Record a 1–2 minute Demo V1 video
- [ ] Finalize Pipeline V1 diagram
- [ ] Produce Resume V1
- [ ] Send current project direction / resume to Lilith referral senior
- [ ] Ask whether the project direction matches real TD work
- [ ] Ask whether current hiring progress requires earlier referral submission
- [ ] Decide whether to submit Lilith around D7

## Day 8 — Unity Editor Tool V0

- [ ] Learn minimal Unity Editor scripting
- [ ] Build a simple data viewer / config entry point
- [ ] View current gameplay config inside the editor
- [ ] Edit at least one meaningful config value
- [ ] Ensure the editor tool is connected to the real demo pipeline
- [ ] Solve 1 DFS / BFS problem

## Day 9 — Batch Processing

- [ ] Choose one real batch-processing use case
- [ ] Implement at least one:
  - [ ] Batch validation
  - [ ] Batch modification
  - [ ] Batch export
- [ ] Prepare roughly 30–50 test records
- [ ] Verify batch processing works on the test set
- [ ] Record the equivalent manual workflow
- [ ] Solve 1 DFS / BFS problem

## Day 10 — Tool V2 / Basic UI & UX

- [ ] Improve default values
- [ ] Improve error messages
- [ ] Improve information hierarchy
- [ ] Add search / filtering or another workflow-shortening feature
- [ ] Ask: can a non-programmer designer use this without touching code?
- [ ] Record the reasons for V1 → V2 changes
- [ ] Solve 1 basic linked-list / tree problem

## Day 11 — Edge Cases + QA

- [ ] Test missing fields
- [ ] Test duplicate IDs
- [ ] Test invalid ranges
- [ ] Test broken references
- [ ] Test empty / malformed input
- [ ] Fix discovered bugs
- [ ] Record at least one case where AI-generated code was incomplete/wrong
- [ ] Document how the issue was identified, corrected, and verified
- [ ] Solve 1 basic coding problem

## Day 12 — Pipeline Case Study

- [ ] Manually process 30–50 records and time it
- [ ] Run the automated workflow on the same data and time it
- [ ] Record errors missed / found in the manual workflow
- [ ] Record errors caught automatically before Unity/runtime
- [ ] Draw "before" pipeline
- [ ] Draw "after" pipeline
- [ ] Write:
  - [ ] Original workflow pain points
  - [ ] Why a tool was needed
  - [ ] What the tool automates
  - [ ] Efficiency change
  - [ ] Bug-risk change

## Day 13 — User Test

- [ ] Ask 1–2 people to use the tool
- [ ] Do not teach the interface live
- [ ] Give each tester a concrete task
- [ ] Observe where they get stuck
- [ ] Record misoperations
- [ ] Record unclear wording / feedback
- [ ] Modify the tool based on real feedback
- [ ] Produce Tool V3
- [ ] Update Case Study

## Day 14 — Final Wrap-up + Formal Applications

> **Do not learn new technology today.**

- [ ] Demo runs end-to-end
- [ ] Python tool runs end-to-end
- [ ] Full pipeline runs end-to-end
- [ ] Finish README
- [ ] Finish Case Study
- [ ] Record final 2–4 minute demo video
- [ ] Clean Git repository
- [ ] Produce Resume V2
- [ ] Prepare stable portfolio link
- [ ] Finish personal game-experience table
- [ ] Prepare notes for 3 "core/favorite" games
- [ ] Finish at least 2 short analyses
- [ ] Expand formal applications

## Final Acceptance Checklist

- [ ] Unity Demo can be played from beginning to end
- [ ] Python tool processes the Demo's real data
- [ ] At least one genuine batch operation exists
- [ ] At least three categories of config errors are automatically detected
- [ ] There is a real V1 → problem → V2/V3 iteration
- [ ] At least one efficiency / error-risk improvement is quantified
- [ ] A 2–4 minute demo video exists
- [ ] README / Case Study clearly explains the project
- [ ] Resume contains truthful, verifiable project bullets
- [ ] Real applications have started
- [ ] Without Codex, the full data flow, major modules, core code logic, and design trade-offs can be explained

## Sprint Rules

- Do not rebuild the project because of a new JD; only adjust feature priority.
- Keep **Unity + C# + Python** as the main stack for this sprint.
- Do not start a second portfolio project before this one reaches the final acceptance checklist.
- Progress is measured by code, working Demo, tools, documentation, video, and applications — not hours of tutorials watched.
- D7 and D14 are mandatory wrap-up days.
- Any feature that does not strengthen evidence of **content implementation, tooling, automation, workflow understanding, or engineering execution** is lower priority.
- Finish one complete loop before pursuing more advanced technology.