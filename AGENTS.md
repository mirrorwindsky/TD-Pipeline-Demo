# AGENTS.md

This repository is a **Technical Designer portfolio project** demonstrating a connected **Game Content Vertical Slice + Content Pipeline** workflow. It is intentionally scoped as a compact, explainable project rather than a commercial-scale game.

## Project Context

Core stack:

- Unity 6.3 LTS
- C#
- Python
- Git / GitHub

Before substantial work, read:

1. `STATUS.md`
2. `TODO.md`
3. `README.md`
4. the relevant document under `Docs/`

These files define the current architecture, scope, verification evidence, and historical milestones.

## Protected Baseline

`Assets/Scenes/Prototype_01.unity` is the Week 1 / Pipeline V1 baseline.

Do not modify, rebuild, or repurpose it unless a task explicitly requires that historical scene.

The active presentation / build scene is:

`Assets/Scenes/VerticalSlice_01.unity`

## Stable Pipeline V2 Boundary

Pipeline V2 is functional and verified. Do not redesign it without a concrete task or reproduced problem.

Avoid casual refactors or speculative expansion of:

- `Tools/config_tool.py`
- the existing `ConfigSource` multi-table model
- generated JSON contracts under `Assets/Data`
- the current Inventory / Objective / Gate / interaction architecture

Do not add generalized quest frameworks, new content tables, dependency visualizers, GUI tools, or other new systems without a demonstrated gameplay, content-production, QA, or workflow need.

Complexity must come from real project problems, not feature accumulation.

## Unity Editing Rules

For scene and presentation work:

- Prefer normal Unity Editor operations, Unity APIs, or narrowly scoped Editor scripts.
- Avoid large direct edits to `.unity` YAML when normal Unity operations can achieve the same result.
- Preserve existing serialized references whenever possible.
- Explicitly report serialized-reference risk introduced by scene changes.
- Do not silently replace existing gameplay architecture while solving presentation problems.

## Iteration Rules

Work in small, verifiable steps.

After each structural change:

1. confirm Unity compiles with no new red Console errors;
2. enter Play Mode when the change affects runtime behavior, controls, camera, scene flow, UI, or interactions;
3. verify the affected gameplay path before proceeding;
4. run the relevant Python Pipeline command when source / generated-data contracts are affected.

Do not expand task scope without a demonstrated reason.

## Verification Expectations

When finishing a task, report:

- files changed;
- scene / Inspector changes;
- Pipeline validation results;
- Play Mode / standalone results when relevant;
- anything not yet verified;
- serialized-reference or regression risks.

Claims in public project documentation must remain independently explainable and backed by repository history, reproducible QA, measured results, or manual verification.
