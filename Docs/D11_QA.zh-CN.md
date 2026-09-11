# D11 QA + Scale Test 记录

[English](D11_QA.md) | 简体中文

## 状态

**Day 11 已完成。**

D11 将项目重点从“继续开发功能”切换为“建立可靠性证据”。目标是验证 Pipeline V2 在更大内容集下仍然可预测，系统覆盖坏数据路径，确认 fail-safe generation，并且只修复 QA 真正暴露的缺陷。

本文档记录 2026-09-11 实际执行的测试。

最终结果：

- 已建立并保留 40 条合法 Scale Fixture；
- Scale Generation 通过；
- 8 条 Batch Preview / Apply 通过；
- 计划要求的主要坏数据类别均已覆盖；
- 发现、复现并修复 2 个真实 Validation Bug；
- 两个修复都完成回归并进入 `main`；
- dependency-cycle / unreachable-objective 等可选系统被有意跳过，因为当前架构没有证明真实需求；
- D11 没有自然出现可归因于“AI 生成错误实现”的案例，因此没有为了 checklist 人为制造；
- 两个真实 QA Bug 均形成了可解释的 AI-assisted debugging 证据。

---

## 测试环境

破坏性 QA 与稳定 D10 workspace 隔离在独立 Git worktree / branch 中：

```text
D:\UnityProjects\TD-Pipeline-Demo
→ stable main workspace

D:\UnityProjects\TD-Pipeline-Demo-D11-QA
→ d11-qa worktree
```

这样可以反复替换 Source、制造 malformed input、生成和恢复，而不污染 D10 baseline。

QA worktree 从 D10 封版提交开始：

```text
4514da2 docs: close Day 10 and hand off to QA
```

主要命令：

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Week 1 的 `Prototype_01.unity` 没有被拿来改造成测试场；当前 V2 Runtime Scene 始终保持：

```text
Assets/Scenes/VerticalSlice_01.unity
```

大多数 D11 测试直接针对 Python Pipeline，因此没有为了每个坏数据案例重复打开 Unity。

---

## Scale Fixture

可复用合法 Fixture：

```text
QA/Fixtures/scale_valid/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

规模：

```text
items.csv           8 records
objectives.csv     12 records
interactables.csv  20 records
-----------------------------
total              40 records
```

Fixture 保留真实 Demo ID：

```text
power_cell
power_node
control_terminal
cube_quick
cube_sturdy
```

同时加入额外合法 Items / Pickups / Devices，用于验证 Lookup、Cross-Table Reference、Generation 和 Batch 在多记录情况下仍然正常。

这 40 条不是为了模拟商业项目规模，而是确认 Parse Once / Typed Model / Validation / Generation 不依赖“只有几条数据”这个偶然条件。

### Scale Batch Fixture

包含 8 条修改：

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

## 测试汇总

| ID | 测试 | 结果 |
| --- | --- | --- |
| QA-00 | QA worktree 中复现 D10 baseline | PASS |
| QA-01 | 40 条合法数据 Scale Generation | PASS |
| QA-02 | 8 条 Scale Batch Preview | PASS |
| QA-03 | 8 条 Scale Batch Apply + Regeneration | PASS |
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

## Scale / Batch 证据

### QA-00 — Baseline Sanity Check

未修改的 D10 baseline 在 QA worktree 中可以干净复现：

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 1 item configs.
Loaded 5 objective configs.
Loaded 5 interactable configs.
```

重新生成后 `git status --short` 仍为空。

**结果：PASS**

### QA-01 — 40 条合法 Scale Generation

输入：

```text
8 Items
12 Objectives
20 Interactables
40 total source records
```

实际结果：

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

独立解析 Generated JSON：

```text
generated interactables: 20
generated objectives: 12
```

8 条 Item 当前作为权威 Item-ID Registry 使用，不单独生成 `items.json`，所以 `20 + 12` 正是当前 Output Contract，不是数据丢失。

**结果：PASS**

### QA-02 — Scale Batch Preview

8 条 old → new 值全部正确输出，最后显示：

```text
Validated 8 batch updates. No source files were changed.
```

随后用 `git diff --no-index` 直接比较 Active `ConfigSource/interactables.csv` 与合法 Fixture，Exit Code 为 `0`，确认 Preview 未修改内容。

**结果：PASS**

### QA-03 — Scale Batch Apply + Regeneration

Batch Apply 后独立比较：

```text
baseline records: 20
actual records:   20
field changes:     8
```

恰好只有预期 8 个 `requiredInteractions` 值变化，其余字段保持不变。

随后正常 Generation 通过：

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

Generated JSON 再次独立验证：

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

**结果：PASS**

---

## 直接通过的坏数据测试

### QA-04 — Missing Required Value + Fail-Safe Generation

注入：

```text
aux_power_box.requiredInteractions
2 -> empty
```

实际结果：

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

失败 Generation 前后分别记录两个 Generated JSON 的 Hash：

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

这直接证明 fail-safe output-preservation contract。

**结果：PASS**

### QA-05 — Duplicate ID

注入：

```text
maintenance_panel.id
maintenance_panel -> power_node
```

实际结果：

```text
[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-06 — Invalid Integer Type

注入：

```text
backup_generator.requiredInteractions
5 -> three
```

实际结果：

```text
[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-07 — Invalid Range

注入：

```text
sensor_array.requiredInteractions
4 -> 0
```

实际结果：

```text
[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-08 — Broken Cross-Table Item Reference

注入：

```text
coolant_pump.requiredItemId
coolant_canister -> missing_coolant
```

实际结果：

```text
[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-10 — Missing Required Column

从 `objectives.csv` 整体删除 required `description` 列。

实际结果：

```text
[ERROR] objectives.csv: missing required column 'description'.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-11 — Invalid `interactionType`

注入：

```text
security_console.interactionType
Device -> Terminal
```

实际结果：

```text
[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.
Validation failed. Generated JSON files were not updated.
```

**结果：PASS**

### QA-12 — Empty CSV Input

将 `items.csv` 截断为精确 `0` Byte。

实际结果：

```text
[ERROR] items.csv: CSV header is missing.
Validation failed. Generated JSON files were not updated.
```

没有 Python traceback。

**结果：PASS**

---

## Bug 1 — Active V2 Scene Reference Coverage Gap

### QA-09 复现

Active Scene 中存在：

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

只修改源 ID：

```text
control_terminal -> control_terminal_renamed
```

Scene 本身不动。

### 初始结果 — FAIL

修复前 Generation 错误地成功：

```text
=== Content Pipeline ===
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

独立验证：

```text
control_terminal in generated JSON: False
control_terminal_renamed in generated JSON: True
```

而 Active Scene 仍然是：

```text
configId: control_terminal
```

这意味着 Validator 会允许真实 Runtime Dependency 断链进入 Unity。

### 根因

Unity Reference Validator 仍然是 V1 时代的实现：

```text
SCENE_PATH -> Prototype_01.unity
ConfigurableInteractable.configId only
```

而当前 V2 Scene 使用 `PickupInteractable` / `DeviceInteractable` 的 `configId`。

### 修复

Validator 改为针对：

```text
Assets/Scenes/VerticalSlice_01.unity
```

并使用显式组件白名单：

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

同一份坏输入修复后变为：

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
Validation failed. Generated JSON files were not updated.
```

恢复 40 条合法 Fixture 后 Regression PASS。

QA Branch 修复：

```text
5fbf998 fix: validate active scene config references
```

进入 `main` 的等价修复：

```text
97b24be fix: validate active scene config references
```

**最终结果：FAIL → FIXED → PASS**

---

## Bug 2 — Malformed CSV Silent Truncation

### QA-13 复现

注入：

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

表头只有三列。

### 初始结果 — FAIL

修复前 `csv.DictReader` 解析为：

```text
{
  'id': 'inspect_storage',
  'displayName': 'Inspect Storage',
  'description': 'Objective: Inspect storage',
  None: [' then return.']
}
```

但 Pipeline 仍然输出：

```text
Validation: PASSED
```

并生成：

```text
Objective: Inspect storage
```

而不是完整 Description。

这属于 **silent data corruption**，不是 crash。

### 修复

`validate_schema()` 现在会检查 `DictReader` 在额外 value 情况下生成的 `None` key，并输出 row-level ERROR。

同一份 malformed input 变为：

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
Validation failed. Generated JSON files were not updated.
```

恢复 40 条合法 Fixture 后 Generation 再次 PASS。

QA Branch 修复：

```text
7d2c058 fix: reject malformed CSV rows with extra columns
```

进入 `main` 的等价修复：

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

**最终结果：FAIL → FIXED → PASS**

---

## Scope 决策

D11 没有增加：

- dependency-cycle detection；
- unreachable-objective detection；
- generalized quest validation；
- all-Prefab scanning；
- dependency visualization；
- Unity Editor GUI；
- 大型 automated-test framework。

原因：

扩展后的真实数据和 QA 并没有证明这些系统当前有必要。D11 的代码修改严格限制在实际被 Test Case 复现出来的缺陷。

---

## AI-Assisted Development Note

D11 没有自然出现可以诚实归因于“AI 生成错误实现”的案例，因此没有为了 checklist 人工制造。

但两个真实 QA Bug 都形成了完整的 AI-assisted debugging 过程：

```text
active V2 Scene-reference coverage gap
→ reproduce
→ root cause
→ targeted fix
→ re-test same failure
→ valid 40-record regression
→ integrated into main
```

以及：

```text
malformed CSV silent truncation
→ independently verify silent corruption
→ identify validation gap
→ targeted fix
→ re-test malformed input
→ valid 40-record regression
→ integrated into main
```

这些案例具备具体输入、可复现 Failure、明确 Root Cause 和 Regression Evidence，适合作为 AI-assisted debugging 证据，但不会被包装成“AI 生成的 Bug”。

---

## D12 Handoff / 后续结果

D11 原计划建议 D12 继续复用同一套 40-record Fixture 做 Before / After 量化。该工作随后已经完成，完整结果见：

[`Pipeline_Case_Study.zh-CN.md`](Pipeline_Case_Study.zh-CN.md)

D11 为 Case Study 提供的证据包括：

- 40 条合法 Scale Generation；
- 8 条 Batch Preview / Apply；
- Source / Generated Output 独立校验；
- row / field / value 错误定位；
- fail-safe generated-output preservation；
- Active Scene Validation Coverage Bug 的发现与修复；
- malformed CSV silent-corruption Bug 的发现与修复；
- 不编造 AI-generated failure 的真实 AI-assisted debugging 记录；
- 不增加无证据系统的 Scope 决策。

在任何受控 QA / Measurement 之外，`ConfigSource` 与 Generated JSON 都应保持正常可玩 Demo Baseline。