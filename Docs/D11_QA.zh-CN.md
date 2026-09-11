# D11 QA + Scale Test 记录

[English](D11_QA.md) | 简体中文

## 状态

Day 11 将项目重点从继续开发功能切换为建立可靠性证据。目标是验证 Pipeline V2 在更大内容集下仍然可预测，系统覆盖坏数据路径，确认 fail-safe generation，并且只修复 QA 真正复现出来的缺陷。

本文档记录 2026-09-11 实际执行的测试。

最终结果：

- 建立并保留可复用的 40 条 Scale Fixture；
- Scale Generation 通过；
- 8 条 Batch Preview / Apply 通过；
- 主要坏数据类别均已覆盖；
- 发现、复现并修复 2 个真实 Validation Bug；
- 两个修复均完成回归并进入 `main`；
- 没有真实需求证据的可选系统被有意留在 Scope 外。

---

## 测试环境

破坏性 QA 使用独立 Git worktree / branch 与稳定工作区隔离，以便安全地反复替换 Source、制造 malformed input、Generation 和恢复。

QA 从 D10 封版提交开始：

```text
4514da2 docs: close Day 10 and hand off to QA
```

主要命令：

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

当前 V2 Runtime Scene 始终保持：

```text
Assets/Scenes/VerticalSlice_01.unity
```

大多数坏数据案例直接针对 Python Pipeline，因此不需要为了每个失败路径重复打开 Unity。

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

Scale Batch 修改：

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

这 40 条并不是为了模拟商业项目规模，而是验证 Parse Once / Typed Model / Validation / Generation / Batch 不依赖“只有几条数据”这一偶然条件。

---

## 测试汇总

| ID | 测试 | 结果 |
| --- | --- | --- |
| QA-00 | D10 baseline sanity check | PASS |
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

### QA-01 — 40 条合法 Generation

输入：

```text
8 Items
12 Objectives
20 Interactables
40 total source records
```

结果：

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

独立统计 Generated Output：

```text
generated interactables: 20
generated objectives: 12
```

8 条 Item 当前作为权威 Item-ID Registry 使用，不单独生成 `items.json`，因此 Output Count 与当前 Generation Contract 一致。

### QA-02 — Scale Batch Preview

8 条预期修改全部被正确输出，结尾显示：

```text
Validated 8 batch updates. No source files were changed.
```

随后直接比较文件内容，没有发现差异，确认 Preview 未修改 Source。

### QA-03 — Scale Batch Apply + Regeneration

Apply 后独立比较：

```text
baseline records: 20
actual records:   20
field changes:     8
```

恰好只有预期 8 个 `requiredInteractions` 字段发生变化，其他 Source Field 保持不变。

随后 Generation 以 8 / 12 / 20 条记录正常通过，并独立验证 8 个目标值全部进入 Generated JSON。

---

## 坏数据覆盖

### QA-04 — Missing Required Value + Fail-Safe Generation

注入：

```text
aux_power_box.requiredInteractions
2 -> empty
```

结果：

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

失败 Generation 前后 SHA256：

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

这直接验证 fail-safe output-preservation contract。

### QA-05 — Duplicate ID

```text
maintenance_panel -> power_node
```

结果：

```text
[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.
```

### QA-06 — Invalid Integer Type

```text
backup_generator.requiredInteractions
5 -> three
```

结果：

```text
[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.
```

### QA-07 — Invalid Range

```text
sensor_array.requiredInteractions
4 -> 0
```

结果：

```text
[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.
```

### QA-08 — Broken Cross-Table Item Reference

```text
coolant_pump.requiredItemId
coolant_canister -> missing_coolant
```

结果：

```text
[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.
```

### QA-10 — Missing Required Column

删除 `objectives.csv` 中 required `description` 列后：

```text
[ERROR] objectives.csv: missing required column 'description'.
```

### QA-11 — Invalid `interactionType`

```text
security_console.interactionType
Device -> Terminal
```

结果：

```text
[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.
```

### QA-12 — Empty CSV Input

将 `items.csv` 截断为 0 Byte 后：

```text
[ERROR] items.csv: CSV header is missing.
```

没有 Python traceback。

---

## Bug 1 — Active V2 Scene Reference Coverage Gap

### QA-09 复现

Active Scene：

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

只修改 Source ID：

```text
control_terminal -> control_terminal_renamed
```

修复前 Generation 错误地通过。独立验证发现 Generated JSON 只包含 `control_terminal_renamed`，而 Scene 仍引用 `control_terminal`。

### 根因

Unity Reference Validator 仍是 V1 时代的实现：

```text
SCENE_PATH -> Prototype_01.unity
ConfigurableInteractable.configId only
```

当前 V2 Scene 使用 `PickupInteractable` 和 `DeviceInteractable` 的 config reference。

### 修复

Validation 改为针对：

```text
Assets/Scenes/VerticalSlice_01.unity
```

并使用显式组件白名单：

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

同样的坏 Source 现在会产生：

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
```

恢复 40 条合法 Fixture 后 Regression PASS。

Main 修复：

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

在三列表头下，`csv.DictReader` 会把溢出部分放到 `None` key。修复前 Pipeline 仍报告成功，并生成被截断的 Objective Description。

这属于 **silent data corruption**，不是 crash。

### 修复

`validate_schema()` 现在会拒绝 unexpected extra row values。同一份输入会产生：

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
```

恢复 40 条合法 Fixture 后 Regression PASS。

Main 修复：

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

**最终结果：FAIL → FIXED → PASS**

---

## Scope 决策

QA 没有证明以下系统当前有必要：

- dependency-cycle detection；
- unreachable-objective detection；
- generalized quest validation；
- all-Prefab scanning；
- dependency visualization；
- Unity Editor GUI；
- 大型 automated-test framework。

因此本轮实现修改严格限制在真实 Test Case 已经复现出来的缺陷。

---

## AI-Assisted Debugging

AI / Codex 用于加速诊断和实现。上述两个真实 QA Bug 都经历了具体输入复现、独立验证、小范围修复、回归测试并最终进入 `main`。

文档将它们如实记录为 QA 发现的真实缺陷，而不是描述成“AI 生成 Bug”。

---

## 后续量化

同一套 40-record Fixture 后续被继续用于受控 Before / After Benchmark，完整结果记录在 Pipeline Case Study：

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

该数字明确属于 execution-stage measurement，不包含 Batch Request 本身的编写时间。

完整分析：

- [`Pipeline_Case_Study.md`](Pipeline_Case_Study.md)
- [`Pipeline_Case_Study.zh-CN.md`](Pipeline_Case_Study.zh-CN.md)
