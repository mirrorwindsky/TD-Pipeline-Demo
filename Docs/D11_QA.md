# D11 QA + Scale Test Record

## Status

**Day 11 is complete.**

Day 11 shifted the project from feature development to reliability evidence. The goal was to verify that Pipeline V2 remains predictable with a larger content set, systematically exercise bad-data paths, preserve fail-safe generation behavior, and fix only real defects exposed by QA.

This record documents the tests actually executed on 2026-09-11.

Final result:

- 40-record valid Scale Fixture completed and preserved;
- Scale generation passed;
- 8-record Batch Preview / Apply passed;
- required bad-data categories were exercised;
- two real validation defects were discovered, reproduced, fixed, and regression-tested;
- both fixes were integrated into `main`;
- optional dependency-cycle / unreachable-objective systems were intentionally skipped because the current architecture did not demonstrate a real need;
- no qualifying AI-generated implementation failure occurred, so none was fabricated solely to satisfy the original checklist;
- two genuine AI-assisted debugging cases were documented through the QA-discovered defects below.

---

## Test Environment

QA was isolated from the stable D10 workspace through a separate Git worktree / branch:

```text
D:\UnityProjects\TD-Pipeline-Demo
→ stable main workspace

D:\UnityProjects\TD-Pipeline-Demo-D11-QA
→ d11-qa worktree
```

This kept the D10 baseline safe while allowing repeated source replacement, malformed input, generation, and restoration.

The QA worktree started from the sealed D10 commit:

```text
4514da2 docs: close Day 10 and hand off to QA
```

Primary commands used:

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

The protected Week 1 Scene was not repurposed for QA. The current V2 runtime Scene remained:

```text
Assets/Scenes/VerticalSlice_01.unity
```

Most Day 11 checks exercised the Python Pipeline directly; Unity did not need to be opened for every malformed-data case.

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

The fixture deliberately preserves real Demo IDs such as:

```text
power_cell
power_node
control_terminal
cube_quick
cube_sturdy
```

while adding valid Items, Pickups, and Devices to exercise lookup, cross-table references, generation, and Batch behavior beyond the original small baseline.

The fixture is not intended to simulate commercial-project scale. Its purpose is to verify that the current parse-once / typed-model / validation / generation behavior does not depend on the source tables containing only a few rows.

### Scale Batch Fixture

The Scale Batch fixture contains 8 updates:

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

---

## Test Summary

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | D10 baseline sanity check in QA worktree | PASS |
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

### QA-00 — Baseline Sanity Check

The untouched D10 baseline reproduced cleanly inside the QA worktree:

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 1 item configs.
Loaded 5 objective configs.
Loaded 5 interactable configs.
```

`git status --short` remained empty after regeneration.

**Result:** PASS

### QA-01 — Valid 40-Record Scale Generation

Input:

```text
8 Items
12 Objectives
20 Interactables
40 total source records
```

Actual result:

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Generated JSON was independently parsed and counted:

```text
generated interactables: 20
generated objectives: 12
```

The 8 Item records are the authoritative Item-ID registry and are not emitted to a separate `items.json`; `20 + 12` generated records therefore matches the current output contract.

**Result:** PASS

### QA-02 — Scale Batch Preview

All eight expected old → new values were reported correctly, ending with:

```text
Validated 8 batch updates. No source files were changed.
```

The active `ConfigSource/interactables.csv` was compared directly against the valid fixture. `git diff --no-index` returned exit code `0`, confirming no content difference.

**Result:** PASS

### QA-03 — Scale Batch Apply + Regeneration

Independent comparison after Batch Apply showed:

```text
baseline records: 20
actual records:   20
field changes:     8
```

Exactly the expected eight `requiredInteractions` values changed and no other fields changed.

Normal generation then passed:

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Generated JSON verification:

```text
PASS cube_sturdy: expected 4, actual 4
PASS power_node: expected 2, actual 2
PASS control_terminal: expected 1, actual 1
PASS aux_power_box: expected 3, actual 3
PASS coolant_pump: expected 4, actual 4
PASS sensor_array: expected 2, actual 2
PASS backup_generator: expected 3, actual 3
PASS maintenance_panel: expected 5, actual 5
overall: PASS
```

**Result:** PASS

---

## Bad-Data Tests That Passed Directly

### QA-04 — Missing Required Value + Fail-Safe Generation

Injected:

```text
aux_power_box.requiredInteractions
2 -> empty
```

Actual result:

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

Generated JSON hashes were captured before and after the failed generation:

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

This directly verifies the fail-safe output-preservation contract.

**Result:** PASS

### QA-05 — Duplicate ID

Injected:

```text
maintenance_panel.id
maintenance_panel -> power_node
```

Actual result:

```text
[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-06 — Invalid Integer Type

Injected:

```text
backup_generator.requiredInteractions
5 -> three
```

Actual result:

```text
[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-07 — Invalid Range

Injected:

```text
sensor_array.requiredInteractions
4 -> 0
```

Actual result:

```text
[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-08 — Broken Cross-Table Item Reference

Injected:

```text
coolant_pump.requiredItemId
coolant_canister -> missing_coolant
```

Actual result:

```text
[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-10 — Missing Required Column

Removed the required `description` column from `objectives.csv`.

Actual result:

```text
[ERROR] objectives.csv: missing required column 'description'.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-11 — Invalid `interactionType`

Injected:

```text
security_console.interactionType
Device -> Terminal
```

Actual result:

```text
[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.
Validation failed. Generated JSON files were not updated.
```

**Result:** PASS

### QA-12 — Empty CSV Input

`items.csv` was truncated to exactly `0` bytes.

Actual result:

```text
[ERROR] items.csv: CSV header is missing.
Validation failed. Generated JSON files were not updated.
```

No traceback occurred.

**Result:** PASS

---

## Bug 1 — Active V2 Scene Reference Coverage Gap

### QA-09 Reproduction

The active Scene contained:

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

Only the source ID was changed:

```text
control_terminal -> control_terminal_renamed
```

The Scene itself was not modified.

### Initial Result — FAIL

Before the fix, generation incorrectly succeeded:

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Independent verification showed:

```text
control_terminal in generated JSON: False
control_terminal_renamed in generated JSON: True
```

while the active Scene still contained:

```text
configId: control_terminal
```

The validator therefore allowed a broken active-Scene runtime dependency to reach Unity.

### Root Cause

The Unity-reference validator was still a V1-era implementation:

```text
SCENE_PATH -> Prototype_01.unity
ConfigurableInteractable.configId only
```

The current V2 Scene uses `PickupInteractable` and `DeviceInteractable` `configId` references.

### Fix

The validator was updated to target:

```text
Assets/Scenes/VerticalSlice_01.unity
```

and use an explicit component whitelist:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same broken source then produced:

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
Validation failed. Generated JSON files were not updated.
```

The valid 40-record fixture was restored and passed generation again.

QA-branch fix commit:

```text
5fbf998 fix: validate active scene config references
```

Equivalent fix in `main`:

```text
97b24be fix: validate active scene config references
```

**Final result:** FAIL → FIXED → PASS

---

## Bug 2 — Malformed CSV Could Silently Truncate Content

### QA-13 Reproduction

Injected row:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

The table header defines only three columns.

### Initial Result — FAIL

Before the fix, `csv.DictReader` parsed the row as:

```text
{
  'id': 'inspect_storage',
  'displayName': 'Inspect Storage',
  'description': 'Objective: Inspect storage',
  None: [' then return.']
}
```

The Pipeline incorrectly reported:

```text
Validation: PASSED
```

and generated:

```text
Objective: Inspect storage
```

instead of the intended full description.

This was a **silent data corruption** bug rather than a crash.

### Fix

`validate_schema()` now detects the `None` key produced by `DictReader` when a row contains unexpected extra values and reports a row-level ERROR.

The same malformed input then produced:

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
Validation failed. Generated JSON files were not updated.
```

The valid 40-record fixture was restored and passed generation again.

QA-branch fix commit:

```text
7d2c058 fix: reject malformed CSV rows with extra columns
```

Equivalent fix in `main`:

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

**Final result:** FAIL → FIXED → PASS

---

## Scope Decisions

Day 11 did **not** add:

- dependency-cycle detection;
- unreachable-objective detection;
- generalized quest validation;
- all-Prefab scanning;
- dependency visualization;
- Unity Editor GUI;
- a larger automated-test framework.

Reason:

The expanded data and QA cases did not demonstrate a concrete need for those systems. Day 11 fixes were restricted to defects that the real test cases reproduced.

---

## AI-Assisted Development Note

No qualifying AI-generated implementation failure occurred during Day 11. An artificial failure was intentionally **not** created solely to satisfy the original checklist.

Day 11 did include genuine AI-assisted debugging work on two real QA-discovered defects:

```text
active V2 Scene-reference coverage gap
→ reproduced
→ root cause identified
→ targeted fix
→ same failing input re-tested
→ valid 40-record regression
→ integrated into main
```

and:

```text
malformed CSV silent truncation
→ silent corruption independently verified
→ validation gap identified
→ targeted fix
→ malformed input re-tested
→ valid 40-record regression
→ integrated into main
```

These cases are suitable for the project's AI-assisted debugging evidence because the underlying failures and fixes are concrete, reproducible, and independently explainable. They are **not** represented as AI-generated bugs.

---

## D12 Handoff

The same valid 40-record fixture should be reused for Day 12 Before / After measurement rather than creating a new synthetic dataset.

Reusable source:

```text
QA/Fixtures/scale_valid/
```

Recommended Day 12 baseline workflow:

```text
same 40 records
→ manual content-update / consistency-check workflow
vs.
same 40 records
→ Pipeline validation / generation / Batch workflow
```

Measure actual time and actual misses / catches. Do not pre-select an expected speedup ratio.

The Day 11 evidence available for the Case Study includes:

- valid 40-record Scale generation;
- verified 8-record Batch Preview / Apply;
- exact Batch source and generated-output checks;
- row / field / value error localization;
- fail-safe generated-output preservation;
- one active-Scene validation coverage bug found and fixed;
- one malformed-CSV silent-corruption bug found and fixed;
- genuine AI-assisted debugging evidence without fabricating an AI-generated failure;
- explicit scope decisions not to add unjustified systems.

The `ConfigSource` / generated JSON baseline should remain the normal playable Demo state outside controlled QA / measurement steps.
