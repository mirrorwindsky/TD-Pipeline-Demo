# Pipeline Case Study — TD Pipeline Demo

English | [简体中文](Pipeline_Case_Study.zh-CN.md)

**Playable build:** [Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

## Project and design evolution

`TD-Pipeline-Demo` connects a Unity slice to CSV authoring, Python validation, and generated JSON. This Technical Designer portfolio project uses Unity 6.3 LTS, C#, Python, CSV / JSON, and Git / GitHub.

The playable flow—`PowerCell → PlayerInventory → PowerNode → ControlTerminal → ExitDoor → Mission Complete`—supplied the dependencies used to develop and test the pipeline.

| Stage | Main work |
| --- | --- |
| V1, Week 1 | One Interactable table, pre-runtime validation, and a source-data-to-gameplay test |
| V2, Day 11 | Parse-once multi-table model, item and scene references, batch tuning, scale QA, and a controlled benchmark |
| Tool V3 | Standalone bilingual GUI/EXE, external rules, draft editing, AI rule proposals, and shared validation across all entry points |

V3 is in commit `22c992e`. QA and benchmark results below retain their Day 11 context; V3 performance has not been remeasured.

## 1. Content problems

As the slice grew beyond its first table, configuration work needed to handle:

- consistent columns and required values across tables;
- integer/range checks for `requiredInteractions`, unique IDs, and valid interaction types;
- Interactable references to item IDs and serialized scene references to config IDs;
- repeated lookup and editing when tuning multiple records;
- malformed CSV and preservation of valid output after failed validation.

Practitioner feedback prompted V3: routine CLI use was inconvenient, and changing standards required Python edits. V3 adds a desktop interface, external rules, and optional natural-language authoring. The local engine executes all checks.

## 2. Current V3 design

### Data and validation

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
├── batch_interaction_updates.csv
└── validation_rules.json
```

```text
CSV → SourceTable (raw strings, parsed once per operation)
→ configurable rule engine → no ERROR → typed ContentModel
→ interactables.json + objectives.json → Unity config databases → gameplay / HUD
```

`ContentModel` holds `ItemConfig`, `ObjectiveConfig`, and `InteractableConfig` lists. Items provide the reference registry; the two outputs live in `Assets/Data`. CSV edits propagate through generation. V3 preserves Unity JSON fields, gameplay, and the `Pickup` / `Device` baseline.

External JSON supplies standards; Python executes columns, required, type, range, enum, unique, regex, cross-table, and scene rules. The 22 baseline rules cover:

- the required columns/values and ID uniqueness for each table;
- integer interaction counts and boolean completion state;
- `requiredInteractions >= 1` as ERROR and values above 10 as WARNING;
- `interactionType` values, `requiredItemId` / `grantedItemId → items.id`, and batch target IDs;
- `configId` references in `VerticalSlice_01.unity` for `ConfigurableInteractable`, `PickupInteractable`, and `DeviceInteractable`.

Rule configuration is checked even for disabled rules. CSV integrity errors (missing/duplicate headers, malformed quotes, mismatched widths) are mandatory. Typed conversion protects Unity integers/booleans. Content errors block generation and Batch writes; warnings allow them. Failed validation preserves JSON.

`config_tool.py` dispatches CLI commands. The shared services, model, and rules live in `pipeline_core.py`, `pipeline_model.py`, and `rule_engine.py`; `rule_authoring.py` manages drafts/proposals. GUI and credential handling have separate modules. All entry points consume structured `ValidationIssue` objects. Full module details: [技术实现 (Chinese)](技术实现.md).

### GUI and batch tuning

The tkinter/ttk GUI switches between Chinese (default) and English without discarding work. It supports rule CRUD, enable/disable, draft validation, save/reload, generation, and Batch. The Windows EXE includes the runtime and locates the external project.

Drafts work without saving: minimum 1 → 4 fails the five baseline interactables; restoring 1 passes. **Save Rules** persists rules separately from generated content.

Batch still targets `requiredInteractions`:

```text
batch_interaction_updates.csv → check update table → stage changes in memory
→ validate all staged content and scene references → preview or atomically write CSV
→ generate JSON
```

Preview makes no source changes. Apply checks all staged data, including untouched rows, before writing `interactables.csv`. It shares Validate/Generate rules. `BatchInteractionUpdate` records provide before/after values.

Rules/CSV use temporary files and atomic replacement. JSON stages both outputs and attempts I/O rollback; multi-file publication is not crash-atomic. Rule saves check for external changes.

### AI-assisted rules

```text
Natural-language request + headers + supported types + current rules
→ provider → checked RulePatch → GUI preview → Apply to Draft
→ deterministic content validation → user chooses whether to Save Rules
```

OpenAI/DeepSeek propose `add`, `update`, or `disable`. Checks cover JSON, operations, types, tables, fields, parameters, regex, references, ID conflicts, and update targets. Applying rechecks the proposal and draft baseline. AI receives no CSV rows and cannot delete rules, execute Python, or save files. Fake Provider supports offline demos/tests.

Masked GUI keys default to session use. Explicitly remembered keys go to Windows Credential Manager, per provider and outside the project. Environment variables are a fallback. Non-AI functions need no credentials or SDK.

Entry points:

```powershell
py Tools/config_tool.py gui
py Tools/config_tool.py rules-check
py Tools/config_tool.py validate
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
py Tools/build_exe.py
py -m unittest discover -s Tools/tests
```

No-subcommand CLI invocation still generates JSON. The build produces `Builds/ConfigTool/TDConfigTool.exe`; builds remain outside Git. Operation details: [使用说明 (Chinese)](使用说明.md).

## 3. Day 11 QA evidence

`QA/Fixtures/scale_valid/` contains 8 items, 12 objectives, and 20 interactables: **40 records** plus 8 batch updates. It tested behavior beyond a few rows; commercial-scale performance was out of scope.

Recorded results:

- generation passed and produced 20 interactables and 12 objectives;
- all 8 previewed updates matched the request, with no source changes;
- Apply changed exactly 8 `requiredInteractions` fields and no other source fields;
- regeneration propagated all 8 values into JSON;
- bad-data tests covered missing values/columns, duplicate IDs, invalid integers/ranges/interaction types, broken item/scene references, empty CSV, and extra columns.

### Active-scene reference gap

Renaming `control_terminal` to `control_terminal_renamed` left `configId: control_terminal` stale in the scene. Generation passed because validation still targeted `Prototype_01.unity` and only `ConfigurableInteractable`.

Commit `97b24be` (`fix: validate active scene config references`) targeted `VerticalSlice_01.unity` and `ConfigurableInteractable`, `PickupInteractable`, and `DeviceInteractable`. Bad input was blocked and valid scale data passed. V3 retains this scope in its scene rule.

### Silent CSV truncation

This three-column Objective row contains an unescaped comma:

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` put overflow under `None`; the old pipeline ignored it and generated a shortened description while reporting success. Commit `bb088b3` (`fix: reject malformed CSV rows with extra columns`) fixed the then-current `validate_schema()`. V3 rejects these rows in `pipeline_core.parse_csv_table()`.

### Output preservation and V3 regression

For a missing required value, both generated JSON SHA256 hashes were unchanged after failed generation. The [Day 11 record](D11_QA.md) retains the exact inputs, logs, hashes, and fix results.

V3 `unittest` coverage includes the scale fixture, rule configuration, changed-rule Batch behavior, JSON, write failures, drafts, languages, providers, keys, and EXE project discovery. Tests use temporary copies and mocked AI. Tk needs a desktop; native credential testing is opt-in. These tests establish neither live-provider quality nor new performance results.

## 4. Historical execution benchmark

The Day 11 follow-up compared the same 40-record fixture and the same eight changes:

| ID | Before | After |
| --- | --- | --- |
| cube_sturdy | 3 | 4 |
| power_node | 3 | 2 |
| control_terminal | 2 | 1 |
| aux_power_box | 2 | 3 |
| coolant_pump | 3 | 4 |
| sensor_array | 4 | 2 |
| backup_generator | 5 | 3 |
| maintenance_panel | 4 | 5 |

Manual work located/edited CSV rows, copied values into matching JSON records, checked consistency, and saved both files. Automation ran `batch-preview → batch-apply → generate`.

| Measurement | Recorded result |
| --- | --- |
| Manual execution | 192.000 s |
| Automated execution, PowerShell `Measure-Command` | 0.2865603 s, rounded to 0.287 s |
| Execution speedup | ~670× |
| Execution-time reduction | ~99.85% |

Independent verification found 20 CSV and 20 JSON records, eight correct changes, and no unintended CSV edits. Both paths passed with zero errors.

This pre-V3 measurement covers execution after request preparation, excluding authoring and total production time. The speedup applies only to this sample. Separate bad-data QA supports error detection; a zero-error timing sample cannot measure error-rate reduction.

## 5. Trade-offs and outcome

The pipeline automates CSV/JSON synchronization, provides rule/row/field/value diagnostics, catches broken references before runtime, and preserves output on validation failure.

Scope decisions followed the observed work:

- The standalone GUI addresses routine tool access; Unity Editor integration would add a separate maintenance surface.
- External rules address changing standards; Python remains responsible for executing supported rule types.
- AI assists rule authoring, while explicit preview/apply/save steps preserve user control.
- The project has no generalized objective dependency graph, so cycle/unreachable-objective checks are deferred.
- All-scene/all-prefab scanning, dependency visualization, and a large test framework remain outside scope. Standard-library tests cover the current tool; Python regex checks have no execution timeout.
- Scene coverage and malformed-row rejection were expanded after the two reproduced QA failures.

The result connects playable content, typed multi-table data, configurable validation, GUI, Batch, and optional AI authoring. Evidence includes Day 11 QA, hash-based output preservation, the scoped benchmark, V3 regression tests, and the v1.0.0 Windows x64 manual launch-to-Mission-Complete check.
