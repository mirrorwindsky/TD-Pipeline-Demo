# AGENTS.md

This repository is a **Technical Designer portfolio project** for 2027 graduate recruiting. Its purpose is to demonstrate a connected **Game Content Vertical Slice + Content Pipeline** workflow, not to grow into a commercial-scale game.

## Project Context

Core stack is frozen for the current sprint:

- Unity 6.3 LTS
- C#
- Python
- Git / GitHub

Before starting substantial work, read:

1. `STATUS.md`
2. `TODO.md`
3. `README.md`
4. the current handoff document under `Docs/`, if one exists

These files define the current milestone, scope, and acceptance criteria.

## Protected Baseline

`Assets/Scenes/Prototype_01.unity` is the Week 1 / Pipeline V1 baseline.

Do not modify, rebuild, or repurpose it unless the task explicitly requires that scene.

The active presentation scene is currently:

`Assets/Scenes/VerticalSlice_01.unity`

## Stable Pipeline V2 Boundary

Pipeline V2 is already functional and should not be redesigned unless the task explicitly targets it.

Do not casually refactor or expand:

- `Tools/config_tool.py`
- the existing `ConfigSource` multi-table model
- generated JSON contracts under `Assets/Data`
- the current Inventory / Objective / Gate / interaction architecture

Avoid adding new gameplay systems, generalized quest frameworks, new content tables, dependency visualizers, or GUI tools without a demonstrated content-production or workflow need.

Complexity must come from real project problems, not from feature accumulation.

## Unity Editing Rules

For scene and presentation work:

- Prefer Unity MCP, Unity Editor APIs, normal Inspector operations, or narrowly scoped Editor scripts.
- Avoid large direct edits to `.unity` YAML when normal Unity operations can achieve the same result.
- Preserve existing serialized references whenever possible.
- Explicitly report any serialized-reference risk introduced by scene changes.
- Do not silently replace existing gameplay architecture while solving presentation problems.

## Iteration Rules

Work in small, verifiable steps.

After each structural change:

1. confirm Unity compiles with no new red Console errors;
2. enter Play Mode when the change affects runtime behavior, controls, camera, scene flow, UI, or interactions;
3. verify the affected gameplay path before proceeding to the next structural task.

Do not expand the task scope without reporting why the expansion is necessary.

## Completion Report

When finishing a task, report:

- files changed;
- scene / Inspector changes made through Unity;
- validation and Play Mode results;
- anything not yet verified;
- serialized-reference or regression risks;
- what the user should test manually next.

Anything intended for README, Case Study, video, or resume must remain independently explainable without Codex.