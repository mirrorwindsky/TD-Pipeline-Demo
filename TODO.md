# TD Pipeline Demo — 14-Day Sprint Record

> Goal: build one portfolio-ready Technical Designer project combining a playable Unity Vertical Slice with a real content-production Pipeline, validation tooling, automation, QA evidence, and measurable workflow improvement.
>
> Core stack: **Unity 6.3 LTS + C# + Python + Git**.

This file is preserved as a **project-development record**. It documents the implementation sequence and major acceptance decisions; current portfolio documentation lives in `README.md`, `Docs/Pipeline_Case_Study*.md`, and `Docs/D11_QA*.md`.

---

## Day 1–7 — Pipeline V1 Baseline ✅

- [x] Minimal Unity prototype
- [x] Config-driven runtime chain
- [x] Python CSV → JSON Tool V0
- [x] Demo V0
- [x] Validation-aware Tool V1
- [x] End-to-end Pipeline V1 verification
- [x] Week 1 stabilization and bilingual V1 documentation

---

## Day 8 — Gameplay Vertical Slice + Content Model V2 Core ✅

- [x] Preserve `Prototype_01.unity`
- [x] Create `VerticalSlice_01.unity`
- [x] Build complete PowerCell → PowerNode → ControlTerminal → Exit mission flow
- [x] Add Pickup / Device / Gate content types
- [x] Add minimal Inventory / Player State
- [x] Add generic `IInteractable` interaction
- [x] Add Objective / Prompt / Feedback HUD
- [x] Add config-driven Pickup / Device behavior
- [x] Reproduce the `fake_cell` dependency failure that motivated cross-table validation
- [x] Restore valid source data and complete regression

Acceptance result: complete graybox mission loop, multiple content types, a real cross-object dependency, and one concrete Pipeline V2 limitation discovered through testing.

---

## Day 9 — Multi-Table Pipeline V2 + Cross-Reference + Batch ✅

### Content Model

- [x] Add `items.csv`, `objectives.csv`, and retain `interactables.csv`
- [x] Parse each source table once into `SourceTable`
- [x] Build typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`
- [x] Generate `interactables.json` and `objectives.json`
- [x] Drive Objective descriptions from configuration

### Validation

- [x] Schema / type / range / duplicate-ID validation
- [x] legal `interactionType` validation
- [x] Item-ID registry
- [x] `requiredItemId` / `grantedItemId` cross-reference validation
- [x] fail-safe generation preserving previous valid JSON on ERROR

### Batch

- [x] Real Batch modification of `requiredInteractions`
- [x] dry-run Preview
- [x] full-batch validation
- [x] duplicate / invalid target rejection
- [x] atomic source-file replacement
- [x] invalid Batch causes zero source changes
- [x] valid Batch propagates into generated data and Runtime
- [x] restore normal gameplay baseline after verification

---

## Day 10 — Presentation + Tool UX + Standalone Delivery ✅

### Gameplay / Presentation

- [x] Measure full mission timing
- [x] Retire the old 5–8 minute target instead of padding the slice with filler
- [x] Add mouse-controlled third-person camera
- [x] Add player-relative movement
- [x] Improve room structure / occlusion / spatial readability
- [x] Add materials, lighting, interactable readability, and persistent completion-state feedback
- [x] Polish Objective / Prompt / Feedback / Mission Complete presentation

### Tool UX

- [x] Unified `argparse` CLI
- [x] `generate`
- [x] `batch-preview`
- [x] `batch-apply`
- [x] actionable validation errors
- [x] concise successful-generation summary
- [x] evaluate and intentionally skip Unity Editor GUI because the CLI already solves the demonstrated workflow need

### Build

- [x] `VerticalSlice_01.unity` configured as Build Scene
- [x] Windows x86-64 standalone Build
- [x] Build artifacts excluded from Git history
- [x] standalone manually tested from launch to Mission Complete

---

## Day 11 — QA + Scale Test ✅

- [x] Create reusable 40-record Scale Fixture
- [x] Validate 8 Items + 12 Objectives + 20 Interactables
- [x] Verify 8-record Batch Preview / Apply
- [x] Test missing values / columns
- [x] Test duplicate IDs
- [x] Test invalid type / range / `interactionType`
- [x] Test broken cross-table references
- [x] Test broken active-Scene config references
- [x] Test empty / malformed CSV input
- [x] Verify fail-safe output preservation with SHA256 hashes
- [x] Find and fix active V2 Scene reference coverage gap
- [x] Find and fix malformed-CSV silent truncation
- [x] Preserve reproducible evidence in `Docs/D11_QA.md`
- [x] intentionally skip cycle / unreachable-objective systems because no current architecture need was demonstrated

Main fixes:

```text
97b24be fix: validate active scene config references
bb088b3 fix: reject malformed CSV rows with extra columns
```

---

## Day 12 — Before / After + Pipeline Case Study ✅

The same 40-record fixture and same 8 intended updates were used for a controlled equivalent-output execution benchmark.

- [x] Manual workflow measured: `192.000 s`
- [x] Automated `batch-preview → batch-apply → generate`: `0.2865603 s`
- [x] Both outputs independently verified: PASS
- [x] Measured execution-stage speedup: approximately `670×`
- [x] Measured execution-time reduction: approximately `99.85%`
- [x] Keep benchmark scope explicit: Batch-request authoring time is excluded
- [x] Do not infer error reduction from the timing sample; use QA evidence separately
- [x] Produce bilingual Pipeline Case Study

---

## Day 13 — Documentation Consolidation ✅

- [x] Consolidate current technical evidence
- [x] Separate current portfolio docs from historical milestone records
- [x] Produce English / Simplified Chinese QA record
- [x] Produce English / Simplified Chinese Pipeline Case Study
- [x] Keep V1 / D10 documents as historical snapshots rather than rewriting history
- [x] Avoid speculative Tool / Pipeline V3 work without new evidence

External user testing was not included in this release; the technical release is based on internal regression, standalone smoke testing, reproducible QA, and independent output checks.

---

## Day 14 — Final Packaging + Release ✅

- [x] Final normal Pipeline regression
- [x] clean stable `main` branch
- [x] English / Simplified Chinese README synchronized
- [x] bilingual Case Study and QA evidence linked from README
- [x] documentation index under `Docs/README.md`
- [x] Windowed 1280×720 standalone configuration
- [x] resizable Windows player
- [x] project version set to `1.0.0`
- [x] final Windows x86-64 Build tested from launch to Mission Complete
- [x] GitHub Release `v1.0.0` published
- [x] playable Build download linked from README

Release:

[TD Pipeline Demo — Windows x64 Portfolio Build v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

---

## Final Acceptance — V2 ✅

### Unity Vertical Slice

- [x] complete beginning → middle → ending mission flow
- [x] Pickup / Device / Gate content types
- [x] Prompt / Objective / Feedback without Console dependency
- [x] materials, lighting, environment structure, and persistent state feedback
- [x] Windows standalone Build verified

### Content Model / Pipeline

- [x] real multi-table source data
- [x] typed `ContentModel`
- [x] source-driven gameplay / Objective content
- [x] schema / malformed-row / type / range / duplicate validation
- [x] cross-table Item-reference validation
- [x] active-Scene config-reference validation
- [x] genuine Batch Preview / Apply
- [x] atomic source replacement
- [x] generated JSON treated as derived output

### Verification / Evidence

- [x] 40-record Scale Test
- [x] systematic bad-data QA
- [x] two real validation defects found and fixed
- [x] fail-safe preservation verified by hash comparison
- [x] Before / After workflow documented
- [x] execution-stage efficiency measured
- [x] bilingual technical documentation
- [x] stable GitHub repository and downloadable v1.0.0 Build

---

## Scope Rules Preserved Through Release

- Do not add features only to increase feature count.
- New complexity must solve a demonstrated gameplay, QA, or workflow problem.
- Keep the project explainable end-to-end.
- Preserve historical milestone documents instead of rewriting them to match later architecture.
- Treat generated data as Pipeline output, not a second hand-maintained source of truth.
