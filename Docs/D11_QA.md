# D11 QA + Scale Test Record

English | [简体中文](D11_QA.zh-CN.md)

## Status

Day 11 shifted the project from feature development to reliability evidence. The goal was to verify that Pipeline V2 remains predictable with a larger content set, systematically exercise bad-data paths, preserve fail-safe generation behavior, and fix only defects reproduced by QA.

This record documents tests executed on 2026-09-11.

Final result:

- reusable 40-record Scale Fixture created and preserved;
- Scale Generation passed;
- 8-record Batch Preview / Apply passed;
- major bad-data categories were exercised;
- two real validation defects were discovered, reproduced, fixed, and regression-tested;
- both fixes were integrated into `main`;
- optional systems without demonstrated need were intentionally left out of scope.

---

## Test Environment

Destructive QA was isolated from the stable workspace through a separate Git worktree / branch so source replacement, malformed input, generation, and restoration could be repeated safely.

QA started from the sealed D10 commit:

```text
4514da2 docs: close Day 10 and hand off to QA
```

Primary commands:

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

The active V2 runtime Scene remained:

```text
Assets/Scenes/VerticalSlice_01.unity
```

Most malformed-data checks exercised the Python Pipeline directly; Unity did not need to be opened for every failure case.

---

## Scale Fixture

Reusable valid fixture:

```text
QA/Fixtures/scale_valid/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

Fixture size:

```text
items.csv           8 records
objectives.csv     12 records
interactables.csv  20 records
-----------------------------
total              40 records
```

Scale Batch updates:

```text
cube_sturdy          3 -> 4
power_node           3 -> 2
control_terminal     2 -> 1
aux_power_box        2 -> 3
coolant_pump         3 -> 4
sensor_array         4 -> 2
backup_generator     5 -> 3
maintenance_panel    4 -> 5
```

The fixture is not presented as commercial-project scale. Its purpose is to verify that parse-once, typed-model, validation, generation, and Batch behavior do not depend on source tables containing only a few rows.

---

## Test Summary

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | D10 baseline sanity check | PASS |
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

---

## Scale / Batch Evidence

### QA-01 — Valid 40-Record Generation

Input:

```text
8 Items
12 Objectives
20 Interactables
40 total source records
```

Result:

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Independent generated-output count:

```text
generated interactables: 20
generated objectives: 12
```

The 8 Item records are the authoritative Item-ID registry and are not emitted to a separate `items.json`; the output counts therefore match the current generation contract.

### QA-02 — Scale Batch Preview

All eight expected changes were reported, ending with:

```text
Validated 8 batch updates. No source files were changed.
```

A direct file comparison returned no content difference, confirming Preview did not modify the source.

### QA-03 — Scale Batch Apply + Regeneration

Independent comparison after Apply:

```text
baseline records: 20
actual records:   20
field changes:     8
```

Exactly the intended eight `requiredInteractions` fields changed; no other source fields changed.

Regeneration then passed with 8 / 12 / 20 loaded records, and all eight expected values were independently verified in generated JSON.

---

## Bad-Data Coverage

### QA-04 — Missing Required Value + Fail-Safe Generation

Injected:

```text
aux_power_box.requiredInteractions
2 -> empty
```

Result:

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

SHA256 before / after failed generation:

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

This directly verifies the fail-safe output-preservation contract.

### QA-05 — Duplicate ID

```text
maintenance_panel -> power_node
```

Result:

```text
[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.
```

### QA-06 — Invalid Integer Type

```text
backup_generator.requiredInteractions
5 -> three
```

Result:

```text
[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.
```

### QA-07 — Invalid Range

```text
sensor_array.requiredInteractions
4 -> 0
```

Result:

```text
[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.
```

### QA-08 — Broken Cross-Table Item Reference

```text
coolant_pump.requiredItemId
coolant_canister -> missing_coolant
```

Result:

```text
[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.
```

### QA-10 — Missing Required Column

Removing the required `description` column from `objectives.csv` produced:

```text
[ERROR] objectives.csv: missing required column 'description'.
```

### QA-11 — Invalid `interactionType`

```text
security_console.interactionType
Device -> Terminal
```

Result:

```text
[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.
```

### QA-12 — Empty CSV Input

A zero-byte `items.csv` produced:

```text
[ERROR] items.csv: CSV header is missing.
```

No traceback occurred.

---

## Bug 1 — Active V2 Scene Reference Coverage Gap

### QA-09 Reproduction

Active Scene:

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

Source-only rename:

```text
control_terminal -> control_terminal_renamed
```

Before the fix, generation incorrectly passed. Independent verification showed the generated JSON contained only `control_terminal_renamed`, while the Scene still referenced `control_terminal`.

### Root Cause

The Unity-reference validator was still a V1-era implementation:

```text
SCENE_PATH -> Prototype_01.unity
ConfigurableInteractable.configId only
```

The current V2 Scene uses `PickupInteractable` and `DeviceInteractable` config references.

### Fix

Validation now targets:

```text
Assets/Scenes/VerticalSlice_01.unity
```

with an explicit component whitelist:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same broken source now produces:

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
```

Valid 40-record regression then passed.

Main fix:

```text
97b24be fix: validate active scene config references
```

**Final result:** FAIL → FIXED → PASS

---

## Bug 2 — Malformed CSV Silent Truncation

### QA-13 Reproduction

Injected row:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

With a three-column header, `csv.DictReader` parsed the overflow under the `None` key. Before the fix, the Pipeline reported success and generated a truncated Objective description.

This was a **silent data corruption** bug rather than a crash.

### Fix

`validate_schema()` now rejects unexpected extra row values. The same input produces:

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
```

Valid 40-record regression then passed.

Main fix:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

**Final result:** FAIL → FIXED → PASS

---

## Scope Decisions

QA did not justify adding the following systems:

- dependency-cycle detection;
- unreachable-objective detection;
- generalized quest validation;
- all-Prefab scanning;
- dependency visualization;
- Unity Editor GUI;
- a large automated-test framework.

The QA pass therefore restricted implementation changes to defects reproduced by real test cases.

---

## AI-Assisted Debugging

AI / Codex was used as a development accelerator during diagnosis and implementation. The two QA-discovered defects above were reproduced from concrete inputs, independently verified, fixed with narrow changes, regression-tested, and integrated into `main`.

The defects are documented as real QA findings; they are not represented as AI-generated bugs.

---

## Follow-up Measurement

The same 40-record fixture was later reused for the controlled Before / After benchmark documented in the Pipeline Case Study:

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

This is explicitly an execution-stage measurement and excludes authoring the Batch request itself.

Full analysis:

- [`Pipeline_Case_Study.md`](Pipeline_Case_Study.md)
- [`Pipeline_Case_Study.zh-CN.md`](Pipeline_Case_Study.zh-CN.md)
