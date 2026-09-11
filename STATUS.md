# Current Status

**Last updated:** 2026-09-11  
**Sprint stage:** Core project, QA, measurement, and Case Study complete; resume / application packaging is next  
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

The project intentionally uses real gameplay-content needs to create real Pipeline problems, then solves only the problems demonstrated by implementation, QA, or workflow evidence.

---

## Current Milestone — Technical Project Core Complete ✅

The project has moved through gameplay implementation, Pipeline V2, presentation, QA, Scale Test, and measured workflow comparison.

Current completed evidence includes:

- playable indoor Unity Vertical Slice;
- Windows standalone build smoke-tested from launch to Mission Complete;
- multi-table Content Pipeline V2;
- parse-once `SourceTable` architecture;
- typed `ContentModel`;
- schema / malformed-row / type / range / duplicate validation;
- legal `interactionType` validation;
- Item cross-table reference validation;
- active `VerticalSlice_01.unity` `configId` validation for supported Interactable components;
- fail-safe generation that preserves previous valid JSON on ERROR;
- validated Batch Preview / atomic Apply;
- reusable 40-record Scale Fixture;
- systematic bad-data QA with two real bugs found and fixed;
- controlled manual-vs-automated execution benchmark;
- portfolio-ready Pipeline Case Study.

The next priority is **resume, final README packaging, project explanation, and applications**, not more feature development.

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

Current active presentation / build Scene:

```text
Assets/Scenes/VerticalSlice_01.unity
```

Protected Week 1 baseline:

```text
Assets/Scenes/Prototype_01.unity
```

The normal playable source / generated-data baseline should remain restored outside controlled QA / measurement work.

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

Verified guarantees:

- invalid source data blocks generation;
- previous valid generated JSON remains preserved after validation failure;
- successful generation uses the same typed model used by validation;
- Batch Preview performs no source modification;
- Batch Apply writes `interactables.csv` atomically after logical validation;
- active-Scene config references are checked for the current supported Interactable types;
- malformed CSV rows with unexpected extra columns are rejected instead of silently truncating data.

---

## QA + Scale Evidence

Reusable fixture:

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

Day 11 results:

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | Baseline sanity check | PASS |
| QA-01 | Valid 40-record Scale Generation | PASS |
| QA-02 | 8-record Scale Batch Preview | PASS |
| QA-03 | 8-record Batch Apply + Regeneration | PASS |
| QA-04 | Missing required value + fail-safe preservation | PASS |
| QA-05 | Duplicate ID | PASS |
| QA-06 | Invalid integer type | PASS |
| QA-07 | Invalid range | PASS |
| QA-08 | Broken cross-table Item reference | PASS |
| QA-09 | Broken active V2 Scene `configId` | FAIL → FIXED → PASS |
| QA-10 | Missing required column | PASS |
| QA-11 | Invalid `interactionType` | PASS |
| QA-12 | Empty CSV input | PASS |
| QA-13 | Malformed CSV / extra column | FAIL → FIXED → PASS |

Full reproducible QA evidence:

```text
Docs/D11_QA.md
```

### Real Bug Fix 1 — Active Scene Reference Coverage

The pre-D11 validator still targeted the V1 `Prototype_01.unity` / `ConfigurableInteractable` boundary. QA reproduced a stale `control_terminal` `configId` in the active V2 Scene that incorrectly passed generation.

The validator was updated to target `VerticalSlice_01.unity` and the current config-driven Interactable component whitelist.

Main fix:

```text
97b24be fix: validate active scene config references
```

### Real Bug Fix 2 — Malformed CSV Silent Truncation

An unescaped comma could create an extra CSV value stored by `DictReader` under the `None` key. Before the fix, the Pipeline silently generated a truncated Objective description while reporting success.

`validate_schema()` now rejects unexpected extra values with a row-level ERROR.

Main fix:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

### Fail-Safe Evidence

QA-04 compared SHA256 hashes for both generated JSON files before and after invalid source input. Both hashes remained unchanged after validation failed.

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

---

## Before / After Measurement ✅

A controlled execution-stage benchmark reused the same 40-record fixture and the same 8 intended `requiredInteractions` updates.

### Manual Equivalent-Output Workflow

Manual work included:

- locate 8 target IDs in `ConfigSource/interactables.csv`;
- edit the 8 source values;
- locate corresponding records in generated `Assets/Data/interactables.json`;
- manually apply the same 8 values;
- check and save both files.

Measured time:

```text
192.000 s
```

Independent verification:

```text
CSV records: 20
JSON records: 20
overall: PASS
0 unintended CSV field changes detected
```

### Automated Workflow

```text
batch-preview
→ batch-apply
→ generate
```

Measured execution time:

```text
0.2865603 s
```

Independent verification also passed.

### Measurement Result

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

This is explicitly an **execution-stage benchmark**. It excludes authoring the Batch request and is not presented as a claim that the entire content-production process is 670× faster.

The benchmark sample produced 0 manual errors and 0 automated errors, so error-risk reduction is supported separately by the QA evidence rather than inferred from this timing sample.

Full Case Study:

```text
Docs/Pipeline_Case_Study.md
```

---

## Current Portfolio Evidence

The repository now contains:

```text
Docs/D11_QA.md
→ reproducible QA / bug-fix evidence

Docs/Pipeline_Case_Study.md
→ Problem / Pipeline Design / QA / Before-After / Trade-offs / Outcome

QA/Fixtures/scale_valid/
→ reusable 40-record Scale / benchmark fixture
```

The English README currently reflects the Day 11 technical milestone and should receive one final small packaging pass to surface the new Case Study and benchmark before applications.

The Simplified Chinese README remains intentionally frozen at an earlier milestone with a visible notice pointing readers to the English README. Full bilingual synchronization is a follow-up task, not a blocker for producing the resume.

---

## AI-Assisted Development Note

No qualifying AI-generated implementation failure occurred during Day 11, so none was fabricated solely to satisfy a checklist.

Day 11 did include genuine AI-assisted debugging on two real QA-discovered defects. Both were reproduced from concrete inputs, diagnosed, fixed with narrow changes, regression-tested, and integrated into `main`.

Anything used in README, Case Study, video, or resume must remain independently explainable without Codex.

---

## Current Scope Boundaries

- No new gameplay system is planned unless later application / interview feedback reveals a real blocker.
- No generalized quest framework is planned.
- No dependency visualization is planned without demonstrated need.
- No Unity Editor GUI is planned unless later user feedback demonstrates a workflow benefit.
- Active-Scene reference validation is not a generalized all-Scene / all-Prefab dependency scanner.
- Prerequisite-device relationships remain Unity serialized references.
- Objective progression timing remains event-driven in C#; only player-facing Objective content is data-driven.
- Sound / VFX remain optional and deferred.
- External user testing is currently unavailable and is not treated as an application blocker.
- Lilith TD feedback is opportunistic rather than a prerequisite for applications.

---

## Next — Final Packaging + Resume

Immediate next work:

1. update the English README to surface the final Case Study and measured benchmark;
2. run one final `main` Pipeline regression and confirm clean Git state;
3. prepare concise, truthful resume project bullets;
4. prepare a short interview explanation that can be delivered without Codex;
5. add the stable GitHub repository link to the resume;
6. start / expand applications.

Optional follow-up after the resume is usable:

- synchronize the Chinese README;
- record a short final demo video;
- collect external TD / user feedback if available.