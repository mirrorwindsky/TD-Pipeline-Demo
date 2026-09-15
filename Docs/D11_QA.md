# Day 11 QA and Scale Test Record

English | [简体中文](D11_QA.zh-CN.md)

> Historical test record: **2026-09-11, Pipeline V2**. Inputs, console output, hashes, and results below belong to that run. Tool V3 retains these cases with a new implementation and output format; see the V3 note at the end and the [current case study](Pipeline_Case_Study.md).

## Purpose and environment

Day 11 checked larger inputs, bad-data handling, and preservation of valid output after failed generation. The work produced a reusable 40-record fixture, passed scale generation and eight batch updates, and found two defects. Both were reproduced, fixed, regression-tested, and merged into `main`.

Tests that replaced source files or injected malformed input ran in a separate Git worktree/branch. They started from `4514da2` (`docs: close Day 10 and hand off to QA`), used `Assets/Scenes/VerticalSlice_01.unity`, and ran:

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Most bad-data cases exercised Python directly, without opening Unity for each case. Implementation changes were limited to reproduced defects.

## Scale fixture

The preserved files are in `QA/Fixtures/scale_valid/`:

| File | Records |
| --- | --- |
| items.csv | 8 |
| objectives.csv | 12 |
| interactables.csv | 20 |
| **Content total** | **40** |
| batch_interaction_updates.csv | 8 updates to existing records |

The fixture checked parse-once loading, typed models, validation, generation, and Batch beyond the initial few rows. It provided no commercial-scale performance measurement.

Requested updates:

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

## Test summary

| ID | Test | Result |
| --- | --- | --- |
| QA-00 | D10 baseline sanity check | PASS |
| QA-01 | Valid 40-record scale generation | PASS |
| QA-02 | 8-record batch preview | PASS |
| QA-03 | 8-record batch apply and regeneration | PASS |
| QA-04 | Missing required value and output preservation | PASS |
| QA-05 | Duplicate interactable ID | PASS |
| QA-06 | Invalid integer type | PASS |
| QA-07 | Invalid numeric range | PASS |
| QA-08 | Broken cross-table item reference | PASS |
| QA-09 | Broken active-scene configId reference | FAIL → FIXED → PASS |
| QA-10 | Missing required column | PASS |
| QA-11 | Invalid interactionType | PASS |
| QA-12 | Empty CSV input | PASS |
| QA-13 | Malformed CSV with extra columns | FAIL → FIXED → PASS |

## Scale and Batch results

### QA-01 — Generation

Input was 8 items, 12 objectives, and 20 interactables. Recorded output:

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Independent output counts were 20 generated interactables and 12 generated objectives. The 8 item records served as the Item-ID registry; no separate `items.json` was emitted, consistent with the generation contract.

### QA-02 — Preview

All eight expected changes appeared, ending with:

```text
Validated 8 batch updates. No source files were changed.
```

Direct file comparison found no source content changes.

### QA-03 — Apply and regenerate

Independent comparison after Apply:

```text
baseline records: 20
actual records:   20
field changes:     8
```

Exactly the eight requested `requiredInteractions` values changed; every other source field was unchanged. Regeneration passed with 8 / 12 / 20 loaded records, and all eight values were independently checked in JSON.

## Bad-data results

### QA-04 — Missing required value and output preservation

Injected `aux_power_box.requiredInteractions: 2 → empty`. The run returned:

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

Both SHA256 hashes were unchanged before and after the failed generation:

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

### Other rejected inputs

| ID | Injected change | Recorded error |
| --- | --- | --- |
| QA-05 | `maintenance_panel → power_node` | `[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.` |
| QA-06 | `backup_generator.requiredInteractions: 5 → three` | `[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.` |
| QA-07 | `sensor_array.requiredInteractions: 4 → 0` | `[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.` |
| QA-08 | `coolant_pump.requiredItemId: coolant_canister → missing_coolant` | `[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.` |
| QA-10 | Remove `description` from `objectives.csv` | `[ERROR] objectives.csv: missing required column 'description'.` |
| QA-11 | `security_console.interactionType: Device → Terminal` | `[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.` |
| QA-12 | Zero-byte `items.csv` | `[ERROR] items.csv: CSV header is missing.` |

QA-12 returned the error without a Python traceback. QA-09 and QA-13 required fixes, described below.

## QA-09 — Active-scene reference coverage gap

The scene held this reference:

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

Only the source ID was changed: `control_terminal → control_terminal_renamed`. Generation initially passed. Independent inspection found the renamed ID in JSON while the scene retained the old ID.

The validator still used the V1 scope: `SCENE_PATH → Prototype_01.unity`, with only `ConfigurableInteractable.configId` recognized. The V2 scene also used `PickupInteractable` and `DeviceInteractable`.

Commit `97b24be` (`fix: validate active scene config references`) targeted `VerticalSlice_01.unity` and all three config-driven component types:

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

The same bad source then produced:

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
```

The restored 40-record fixture passed regression. **Result: FAIL → FIXED → PASS.**

## QA-13 — Malformed CSV silent truncation

Injected into the three-column Objective table:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` put the extra value under the `None` key. The pipeline ignored it, reported success, and generated a shortened Objective description: a silent content corruption failure.

Commit `bb088b3` (`fix: reject malformed CSV rows with extra columns`) made the then-current `validate_schema()` reject extra values. The same input returned:

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
```

The restored 40-record fixture passed regression. **Result: FAIL → FIXED → PASS.**

## Scope and debugging

This QA pass added no dependency-cycle checks, unreachable-objective checks, generalized quest validation, all-prefab scanning, dependency visualization, Unity Editor GUI, or large test framework. The changes addressed the two reproduced failures.

AI/Codex assisted diagnosis and implementation. Both defects came from concrete QA inputs and were independently checked, fixed with narrow changes, regression-tested, and integrated into `main`.

## Follow-up benchmark

The fixture was subsequently reused for a controlled comparison of the same eight changes:

| Measurement | Recorded value |
| --- | --- |
| Manual execution | 192.000 s |
| Automated execution | 0.287 s |
| Execution speedup | ~670× |
| Execution-time reduction | ~99.85% |

The measurement excludes batch-request authoring and covers execution only. It predates V3. Full method, exact timing, and verification: [English case study](Pipeline_Case_Study.md) / [中文](Pipeline_Case_Study.zh-CN.md).

## Reusing these cases with V3

V3 commit `22c992e` moved project standards into `ConfigSource/validation_rules.json` and shared validation across CLI, GUI, and Batch. The scene rule retains the three component types above; extra-column rejection now belongs to `pipeline_core.parse_csv_table()`. Batch validates the entire staged dataset before writing.

`Tools/tests/` reuses the scale fixture in temporary project copies and adds tests for rule configuration, drafts, GUI, AI providers, credentials, and project discovery:

```powershell
py -m unittest discover -s Tools/tests
```

AI HTTP responses are mocked. GUI tests need tkinter and a desktop; native Windows credential storage has a separate opt-in test. Use these tests for current regression without replacing the working project's CSV files. The historical logs and hashes above remain evidence for the 2026-09-11 run.
