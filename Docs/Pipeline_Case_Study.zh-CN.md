# Pipeline Case Study — TD Pipeline Demo

[English](Pipeline_Case_Study.md) | 简体中文

**可玩版本：** [Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

## 概览

`TD-Pipeline-Demo` 是一个面向 Technical Designer（技术策划）的作品集项目，围绕一条连续工作流构建：

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

目标不是制作商业级游戏，也不是搭建大型通用框架，而是让一个紧凑的可玩 Unity Slice 自然产生真实内容生产问题，再只解决实现、QA 或工作流证明确实存在的问题。

核心技术栈：

- Unity 6.3 LTS
- C#
- Python
- CSV / JSON
- Git / GitHub

可玩流程：

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ Mission Complete
```

---

## 1. 问题

第一版 Pipeline 只有一张小型配置表和简单的 CSV → JSON 流程。当 Gameplay Slice 开始出现真实内容依赖后，原流程暴露出一系列生产风险：

- 多张源表需要保持结构一致；
- `requiredInteractions` 需要类型 / 范围校验；
- ID 必须唯一；
- `interactionType` 需要语义合法性校验；
- Interactable 会引用另一张表中的 Item ID；
- Unity Scene 对象持有 `configId`，配置改名后可能产生 stale reference；
- 多条参数调优需要重复查找和编辑；
- malformed CSV 可能静默生成错误内容；
- Validation failure 不应覆盖上一版 known-good generated data。

因此核心设计问题变成：

> 什么样的最小 Pipeline，能够让这些内容变更在进入 Unity Runtime 前变得可预测？

---

## 2. Pipeline 设计

### 策划侧源数据

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

三张内容表各自只 Parse 一次成为 `SourceTable`，再转换成 Typed Data：

```text
SourceTable
→ ItemConfig
→ ObjectiveConfig
→ InteractableConfig
→ ContentModel
```

### Validation + Generation

```text
CSV Source
↓
Parse Once
↓
Schema / malformed-row validation
↓
Type / range / duplicate validation
↓
Typed ContentModel
↓
interactionType validation
↓
Item cross-reference validation
↓
active Scene configId validation
↓
ERROR / WARNING gate
↓
Generated JSON
↓
Unity Config Databases
↓
Runtime Gameplay + HUD
```

当前校验覆盖：

- CSV header / required column / required value 缺失；
- unexpected extra column / malformed row；
- integer / boolean 类型错误；
- 非法或异常 interaction range；
- duplicate IDs；
- 非法 `interactionType`；
- 未知 `requiredItemId` / `grantedItemId`；
- `VerticalSlice_01.unity` 中受支持 Interactable 的 `configId`；
- Validation failure 时保留上一版合法输出。

生成结果：

```text
Assets/Data/interactables.json
Assets/Data/objectives.json
```

Generated JSON 被视为 Pipeline Output，而不是第二份由策划手工维护的真值。

### Batch Workflow

当前真实 Batch 用例是批量修改 `requiredInteractions`：

```text
batch_interaction_updates.csv
↓
full-batch validation
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source replacement
↓
normal generation
```

策划侧 CLI：

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

`batch-preview` 不修改源数据；`batch-apply` 只有在整批逻辑校验通过后才写入 `interactables.csv`。

---

## 3. QA + Scale 证据

建立了可复用的 40 条 Scale Fixture：

```text
QA/Fixtures/scale_valid/
├── items.csv                     8 records
├── objectives.csv               12 records
├── interactables.csv            20 records
└── batch_interaction_updates.csv 8 updates
```

这并不是为了模拟商业项目规模，而是验证当前 Pipeline 不依赖“表里只有几条记录”这一偶然条件。

Scale 结果：

- 40 条合法数据 Generation：PASS；
- 20 条 Interactable 正确生成；
- 12 条 Objective 正确生成；
- 8 条 Batch Preview：PASS；
- 8 条 Batch Apply：PASS；
- 恰好只有目标 8 个 `requiredInteractions` 发生变化；
- 其他 Interactable 字段保持不变；
- 8 个目标值全部正确进入 Generated JSON。

坏数据覆盖包括 required value / column 缺失、duplicate ID、invalid integer type、invalid range、invalid `interactionType`、broken cross-table Item reference、broken active-Scene config reference、empty CSV 和 malformed CSV。

### 真实 Bug 1 — Active V2 Scene Reference Coverage Gap

复现了真实 stale-reference 问题：

```text
VerticalSlice_01.unity
configId = control_terminal

source ID
control_terminal → control_terminal_renamed
```

修复前 Generation 错误地通过，而 Active Scene 仍然引用旧 ID。

根因是 Validator 仍然针对 V1 baseline Scene，并只识别旧的 `ConfigurableInteractable` 契约。

修复后 Validator 改为针对 `VerticalSlice_01.unity`，并维护当前 config-driven Component 白名单：

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

同样的断链现在会在 Generation 前被阻断。

Main 修复：

```text
97b24be fix: validate active scene config references
```

### 真实 Bug 2 — Malformed CSV Silent Truncation

未转义逗号制造了额外 CSV value：

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` 会把溢出部分放到 `None` key 下。修复前 Pipeline 忽略该值，并在仍然报告成功的情况下生成被截断的 Objective Description。

现在 `validate_schema()` 会将 unexpected extra value 作为 row-level ERROR 拦截。

Main 修复：

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

### Fail-Safe Output 证据

针对 required value 缺失测试，失败 Generation 前后分别计算两个 Generated JSON 的 SHA256，两个 Hash 均保持不变：

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

完整可复现 QA：[`D11_QA.zh-CN.md`](D11_QA.zh-CN.md)

---

## 4. Before / After 量化

使用同一套 40-record Fixture 和同一组 8 条 `requiredInteractions` 修改进行等价输出 execution benchmark。

目标修改：

```text
cube_sturdy          3 → 4
power_node           3 → 2
control_terminal     2 → 1
aux_power_box        2 → 3
coolant_pump         3 → 4
sensor_array         4 → 2
backup_generator     5 → 3
maintenance_panel    4 → 5
```

### 人工路径

人工路径包括：查找 8 个源记录、修改 8 个源值、在 Generated JSON 中找到对应记录、手工同步相同数值、检查并保存两份文件。

实测执行时间：

```text
192.000 s
```

独立校验：

```text
CSV records: 20
JSON records: 20
overall: PASS
All 8 intended updates are correct in both CSV and JSON.
No unintended CSV field changes were detected.
```

### 自动路径

```text
batch-preview
→ batch-apply
→ generate
```

使用 PowerShell `Measure-Command` 实测：

```text
0.2865603 s
```

独立校验同样 PASS。

### 结果

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

这明确是 **execution-stage benchmark**：不包含 Batch Request 本身的编写时间，也不代表“整个内容生产过程快 670 倍”。

这次人工和自动路径都没有错误，因此“错误风险下降”由 D11 QA 证据单独支持，而不是从本次计时样本推断。

---

## 5. Before / After 工作流

### Before — 人工等价输出

```text
change request
↓
人工寻找目标记录
↓
人工修改源值
↓
人工寻找对应 generated records
↓
人工修改 generated values
↓
人工核对一致性
↓
Unity Runtime
```

### After — Pipeline Workflow

```text
structured change request
↓
Batch Preview
↓
full-batch validation
↓
Batch Apply
↓
atomic source replacement
↓
normal Pipeline validation
↓
Typed ContentModel
↓
Cross-Table + active-Scene validation
↓
Generated JSON
↓
Unity Runtime
```

已经实际证明的收益：

- deterministic bulk updates；
- Generated Output 被覆盖前先完成校验；
- row / field / value-level error localization；
- cross-table + active-Scene reference checks；
- failure 时保留上一版 known-good generated data；
- Generated Data 始终由 Source 派生，而不是成为第二份手工维护真值。

---

## 6. 设计取舍与 Scope

项目有意不在没有证据的情况下增加复杂度。当前没有实现：

- Unity Editor GUI；
- dependency visualization；
- generalized Quest framework；
- dependency-cycle / unreachable-objective detection；
- all-Scene / all-Prefab scanning；
- 大型 automated-test framework。

决策规则：

> 只有实现、QA 或工作流证明确实存在真实问题时，才为解决它增加复杂度。

例如：

- Editor Integration 被跳过，因为 CLI 已经清晰覆盖 Generate / Preview / Apply，无需额外引入 Editor-only 维护成本；
- cycle / unreachable checks 被跳过，因为当前架构没有外部化通用 Objective Dependency Graph；
- Active Scene Reference Validation 只在 QA 实际复现 stale-ID 问题后扩展；
- malformed-row validation 只在 QA 实际复现 silent truncation 后加入。

---

## 7. 结果

最终项目形成了一条连续的 Technical Designer Workflow：

```text
Playable Vertical Slice
+
Data-Driven Content
+
Typed Multi-Table Pipeline
+
Validation
+
Batch Automation
+
Scale / QA Evidence
+
Measured Execution Improvement
```

核心证据：

- 40-record Scale Test；
- 8-record Batch Preview / Apply；
- 受控 8 条修改 Benchmark：人工 192 s vs 自动执行 0.287 s；
- 在明确测量范围内约 670× execution-stage speedup；
- 系统坏数据 QA；
- 2 个真实 Validation Bug 被发现并修复；
- 通过 Hash Comparison 验证 fail-safe generated-output preservation；
- Windows x64 v1.0.0 Standalone 已从启动完整测试到 Mission Complete。

Pipeline 的主要价值不只是 Benchmark 数字，而是：**更少的重复执行、更早的错误发现、known-good output 保护，以及一条规模足够小、可以被完整理解和维护的内容生产流程。**