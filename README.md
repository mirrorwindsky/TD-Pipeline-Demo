# TD Pipeline Demo

English | [简体中文](README.zh-CN.md)

**Playable build:** [Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/download/v1.0.0/TD-Pipeline-Demo-Windows-x64-v1.0.0.zip) · [Release notes](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

A Technical Designer portfolio project combining a playable Unity slice with CSV authoring, Python validation, JSON generation, batch tuning, and QA. **Tool V3** adds a desktop GUI, editable rules, and AI rule proposals.

Stack: Unity 6.3 LTS, C#, Python, CSV / JSON, Git / GitHub.

## Try the project

### Playable Unity build

Extract the complete release archive and run `TD-Pipeline-Demo.exe`. The v1.0.0 Windows x86-64 build was manually tested through Mission Complete.

| Input | Action |
| --- | --- |
| WASD | Move |
| Mouse | Camera |
| E | Interact |
| Esc | Release cursor |
| Close window | Exit |

### Configuration tool V3

From the repository root, with Python 3.10+ and tkinter:

```powershell
py Tools/config_tool.py gui
```

The GUI defaults to Chinese; select **English** in the upper-right corner. To build a Windows EXE:

```powershell
py Tools/build_exe.py
```

The output, `Builds/ConfigTool/TDConfigTool.exe`, includes Python and tkinter. It locates the project or asks for its folder; editable data stays there. Builds are excluded from Git. This tool EXE is separate from the Unity game launcher.

Instructions: [使用说明 / User guide (Chinese)](Docs/使用说明.md) · [技术实现 / Implementation (Chinese)](Docs/技术实现.md).

## Gameplay slice

The active gameplay/build scene is `Assets/Scenes/VerticalSlice_01.unity`. The Week 1 prototype remains at `Assets/Scenes/Prototype_01.unity`.

```text
PowerCell → PlayerInventory → PowerNode → ControlTerminal
→ ExitDoor → EndMarker → Mission Complete
```

The industrial-facility slice has multiple rooms, a third-person mouse camera, player-relative movement, `IInteractable` pickups/devices, gates, minimal inventory, config-driven item requirements/objective text, and event-driven mission flow. HUD, materials, lighting, and persistent world-state feedback complete the presentation.

## Content pipeline V3

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
├── batch_interaction_updates.csv
└── validation_rules.json
```

```text
CSV → SourceTable (raw strings) → configurable rule engine → no ERROR
→ typed ContentModel → Unity JSON → config databases → gameplay / HUD
```

`ContentModel` contains `ItemConfig`, `ObjectiveConfig`, and `InteractableConfig` lists. It outputs `Assets/Data/interactables.json` and `objectives.json`; items supply the reference registry. Edit CSV and regenerate JSON.

The JSON defines 22 baseline rules: columns, required values, types, ranges, enums, uniqueness, item/batch references, and `VerticalSlice_01.unity` references. Interaction counts must be integers ≥1; values >10 warn. The engine also supports string/boolean checks and regex rules.

CLI, GUI, and Batch share the core and structured `ValidationIssue` results. CSV integrity and Unity type conversion are mandatory. Content errors block writes; warnings allow them. Failed validation preserves output. Replacements are atomic per file, with attempted I/O rollback across JSON outputs; crash-atomic multi-file publication is unsupported.

### Rule editing and batch updates

Add, edit, copy, enable/disable, or delete rules in the GUI. Validate, Generate, and Batch use the draft; **Save Rules** persists it. Changing the minimum from 1 to 4 makes all five baseline interactables fail; restoring 1 passes.

Batch updates modify `requiredInteractions`:

```text
Check update table → apply in memory → validate all staged content
→ preview, or atomically write interactables.csv → generate JSON
```

One Interactable minimum rule governs Validate, Generate, and Batch Apply. Preview makes no changes; Apply updates CSV. Generate JSON afterward.

### AI rule proposals

OpenAI and DeepSeek can turn a natural-language request into an `add`, `update`, or `disable` RulePatch. The flow is:

```text
Request + headers + supported rule types + current rules
→ checked proposal → preview → Apply to Draft → local validation → optional Save Rules
```

Python determines content validity. AI receives no CSV rows and cannot execute code or write files. Invalid/stale proposals are rejected. GUI, editing, Validate, Generate, and Batch work without AI credentials or an SDK; Fake Provider provides an offline demo.

Enter a masked API key for session use. **Remember key on this computer** plus Apply stores it in Windows Credential Manager, separately per provider and outside project files. **Forget key** removes it. Environment variables remain a fallback.

### CLI and tests

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py rules-check
py Tools/config_tool.py validate
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
py -m unittest discover -s Tools/tests
```

No subcommand defaults to Generate. CLI path overrides: `--root`, `--source-dir`, `--output-dir`, `--rules`. Tests use temporary copies and mocked AI; Tk needs a desktop, and native Windows credential tests are opt-in.

## QA and measured results

The reusable fixture at `QA/Fixtures/scale_valid/` contains:

| File | Content |
| --- | --- |
| items.csv | 8 records |
| objectives.csv | 12 records |
| interactables.csv | 20 records |
| batch_interaction_updates.csv | 8 updates to those records |

Day 11 covered the 40 records, missing values/columns, duplicates, invalid types/ranges/enums, broken references, empty/malformed CSV, and output preservation. Fixes addressed scene coverage (`97b24be`) and silent CSV truncation (`bb088b3`). Unchanged SHA256 hashes verified preservation after failed generation. V3 reuses the fixture and tests rules, drafts, GUI, providers, credentials, and EXE project discovery.

The Day 11 follow-up benchmark compared the same eight changes and independently checked both outputs.

## Scope and documentation

Scope excludes Unity Editor integration, CSV editing, dependency visualization, generalized quest graphs, cycle/unreachable-objective detection, all-scene/all-prefab scanning, and large test frameworks. Reproduced QA failures drove fixes; practitioner feedback drove V3's desktop GUI and editable standards.

AI/Codex assisted implementation/debugging. Evidence comes from history, reproducible tests, measurements, and manual playable-build checks.

| Document | Purpose |
| --- | --- |
| [Case study](Docs/Pipeline_Case_Study.md) / [中文](Docs/Pipeline_Case_Study.zh-CN.md) | Design evolution through V3, QA findings, historical benchmark, and trade-offs |
| [Day 11 QA](Docs/D11_QA.md) / [中文](Docs/D11_QA.zh-CN.md) | Tests, logs, hashes, and fixes recorded on 2026-09-11 |
| [使用说明](Docs/使用说明.md) | GUI, rules, Batch, EXE, and AI setup (Chinese) |
| [技术实现](Docs/技术实现.md) | Current modules, data flow, persistence, and provider design (Chinese) |
| [Pipeline V1](Docs/Pipeline_V1.md) / [中文](Docs/Pipeline_V1.zh-CN.md) | Week 1 single-table architecture and Day 6 verification |

The repository includes the complete Unity/Python source, the reusable fixture, bilingual case study and QA records, and links to the tested v1.0.0 playable release.
