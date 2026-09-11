# Pipeline Case Study — TD Pipeline Demo

[English](Pipeline_Case_Study.md) | 简体中文

## 概览

这个项目是一份面向 Technical Designer 求职的作品集案例，围绕一条连续工作流构建：

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

目标不是制作商业级游戏，也不是搭建大型通用框架，而是证明：一个小型可玩 Unity Slice 会自然产生真实内容生产问题，而一层聚焦的 Tooling / Pipeline 可以减少重复工作、在 Runtime 前发现内容错误，并维持稳定、可解释的策划工作流。

当前技术栈：

- Unity 6.3 LTS
- C#
- Python
- CSV / JSON
- Git / GitHub

可玩切片依赖链：

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ Mission Complete
```

当前 Content Pipeline 支持多表源数据、Typed Intermediate Model、校验、Batch Processing、fail-safe generation 和 Active Scene config-reference check。

---

## 1. 问题

项目最初只有一张小型配置表和简单的 CSV → JSON 流程。对于最小原型来说已经足够，但当 Gameplay Slice 开始出现真实内容依赖后，原流程很快暴露出脆弱点。

主要生产风险包括：

- 多张源表需要保持结构合法；
- `requiredInteractions` 需要类型 / 范围校验；
- ID 必须唯一；
- `interactionType` 必须是合法枚举值；
- Interactable 会引用另一张表中的 Item ID；
- Unity Scene 对象持有 `configId`，配置改名后可能出现 stale reference；
- 多条参数重复修改既慢又容易输错；
- malformed CSV 可能生成错误内容；
- Validation failure 不应该破坏上一版 known-good generated data。

人工流程还需要在源数据和生成数据之间反复查找和核对。数据量很小时这些工作并不难，但随着记录数量和跨表引用增加，重复劳动和错误风险会迅速上升。

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

三张主要内容表各自只 Parse 一次成为 `SourceTable`，再转换成 Typed Python Data：

```text
SourceTable
→ ItemConfig
→ ObjectiveConfig
→ InteractableConfig
→ ContentModel
```

这样避免多个 Validation Function 重复读取和解析同一份 CSV。

### Validation Flow

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
ERROR gate
↓
Generated JSON
```

当前校验覆盖：

- CSV header 缺失；
- required columns / values 缺失；
- unexpected extra columns / malformed rows；
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

Generated JSON 被视为 Pipeline Output，而不是另一份由策划手工维护的源数据。

### Batch Workflow

当前真实 Batch 用例是批量修改 `requiredInteractions`：

```text
batch_interaction_updates.csv
↓
validate complete batch
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source-file replacement
↓
normal generation
```

策划侧 CLI：

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

`batch-preview` 不修改源文件；`batch-apply` 只有在整批逻辑校验通过后才写入 `interactables.csv`。

---

## 3. QA + Scale 证据

D11 使用了可复用的 40 条 Scale Fixture：

```text
QA/Fixtures/scale_valid/
├── items.csv                    8 records
├── objectives.csv              12 records
├── interactables.csv           20 records
└── batch_interaction_updates.csv 8 updates
```

目的不是模拟商业项目规模，而是确认当前 Pipeline 行为并不依赖“表里只有几条记录”。

### Scale 结果

- 40 条合法数据生成：PASS；
- 20 条 Interactable 全部正确生成；
- 12 条 Objective 全部正确生成；
- 8 条 Batch Preview：PASS；
- 8 条 Batch Apply：PASS；
- 恰好只有目标 8 个 `requiredInteractions` 发生变化；
- 其他 Interactable 字段保持不变；
- 8 个目标值全部进入 generated JSON。

### Bad-Data Coverage

QA 系统测试覆盖：

- missing required values；
- missing required columns；
- duplicate IDs；
- invalid integer types；
- invalid ranges；
- invalid `interactionType`；
- broken cross-table Item references；
- broken active-Scene config references；
- empty CSV；
- malformed CSV rows。

结果不是继续堆 speculative feature，而是实际发现两个真实 Validation Defect。

### Bug 1 — Active V2 Scene Reference Coverage Gap

旧 Validator 仍然针对 V1 baseline Scene，并且只识别旧的 `ConfigurableInteractable`。

真实失败复现：

```text
VerticalSlice_01.unity
configId = control_terminal

source ID
control_terminal → control_terminal_renamed
```

修复前 Validation 错误地通过，Generated JSON 已不再包含 `control_terminal`，但 Active Scene 仍然引用旧 ID。

修复后 Validator 改为针对 `VerticalSlice_01.unity`，并显式维护 config-driven Interactable Component 白名单：

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

同样的坏引用现在会在 Generation 前被拒绝。

### Bug 2 — Malformed CSV Silent Truncation

未转义逗号制造了额外 CSV value：

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

Python `csv.DictReader` 会把溢出部分放到 `None` key 下。修复前 Pipeline 忽略这部分，Validation 仍显示成功，并生成被截断的 description：

```text
Objective: Inspect storage
```

这不是 crash，而是 silent data corruption。

现在 `validate_schema()` 会拒绝 unexpected extra values，并在 Generation 前输出 row-level error。

### Fail-Safe Output 证据

针对 required value 缺失测试，D11 在 failed generation 前后分别计算两个 generated JSON 的 SHA256。

两个 Hash 完全一致。

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

完整 QA 证据见 [`D11_QA.zh-CN.md`](D11_QA.zh-CN.md)。

---

## 4. Before / After 量化

使用同一套 40-record Scale Fixture 和同一组 8 条 `requiredInteractions` 修改，做受控 execution-stage 对比。

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

### 人工等价输出路径

人工 Benchmark 要求：

1. 在 `ConfigSource/interactables.csv` 找到 8 个目标 ID；
2. 修改 8 个 `requiredInteractions`；
3. 在 `Assets/Data/interactables.json` 找到对应记录；
4. 手工同步相同 8 个值；
5. 检查并保存两个文件。

实测：

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

通过 PowerShell `Measure-Command` 实测：

```text
0.2865603 s
```

独立校验得到同样的 PASS。

### 结果

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

这个数字被严格定义为 **execution-stage benchmark**。

它不包含 Batch Request 本身的编写时间，因此不能解释为“整个内容生产过程快 670 倍”。

更准确的结论是：

> 当批量变更请求已经结构化后，Pipeline 几乎消除了 Execution Stage 中重复的查找、编辑和传播工作，同时仍然经过正常 Generation 使用的同一套 Validation。

这次受控计时里人工和自动都没有出现错误，因此“错误风险下降”不从计时样本中推断，而由 D11 的坏数据 QA、两个真实 Bug 和 fail-safe 证据单独支持。

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

主要风险：

- 重复查找工作；
- 漏改目标；
- Source / Generated Data 不一致；
- 缺少系统化 Pre-Runtime Validation；
- malformed data 可能在人工检查中漏过。

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

当前项目已经实际证明的收益：

- deterministic bulk updates；
- Generated Output 被覆盖前先校验；
- row / field / value-level error localization；
- cross-table reference checks；
- active-Scene config-reference checks；
- failure 时保留上一版 known-good generated data；
- Generated Data 始终由 Source 派生，而不是成为第二份手工维护真值。

---

## 6. 设计取舍与 Scope

以下潜在扩展被有意留在当前范围外：

- Unity Editor GUI；
- dependency visualization；
- generalized Quest framework；
- dependency-cycle detection；
- unreachable-objective detection；
- all-Scene / all-Prefab scanning；
- large automated-test framework。

决策规则很简单：

> 只有当前 Content / QA / Workflow 提供证据说明它能解决真实问题时，才增加复杂度。

例如：

- Unity Editor Integration 被跳过，因为 CLI 已经能清楚提供 Generate / Preview / Apply，而 Editor 方案会额外引入 Python Process、PATH、Working Directory、stdout/stderr capture 和 Editor-only code 的维护成本；
- cycle / unreachable checks 被跳过，因为当前架构并没有外部化通用 Objective Dependency Graph；
- Scene-reference validation 只在 QA 实际证明 V2 Active Scene 会出现 stale config ID 后才扩展；
- malformed-row validation 只在 QA 实际复现 silent content truncation 后加入。

这样项目保持在“可靠、可解释、解决真实问题”的范围内，而不是靠 Feature Count 堆复杂度。

---

## 7. 结果

最终项目形成了一条连续的 Technical Designer Workflow，而不是互不相关的 Gameplay / Python 练习：

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
- Windows standalone Vertical Slice 可从启动完整玩到 Mission Complete。

Pipeline 的主要价值不是单独的 Benchmark 数字，而是：**更少的重复执行、更早的错误发现、known-good output 保护，以及一条规模足够小、可以被完整解释和维护的内容生产流程。**

---

## 面试 / 作品集摘要

> 我做了一个 Unity Vertical Slice，并让真实玩法依赖推动 Python Content Pipeline 的演进。Pipeline 将多表 CSV 解析成 Typed Intermediate Model，校验 Schema、数值、重复 ID、跨表 Item 引用和 Active Scene Config 引用，再生成 Unity 可消费 JSON；同时加入经过完整校验的 atomic Batch Update。项目使用 40 条数据完成 Scale / QA，并通过 QA 发现并修复 2 个真实校验 Bug。在受控的 8 条批量修改 execution benchmark 中，人工等价输出耗时 192 秒，而 Batch Preview → Apply → Generate 耗时 0.287 秒；这个数字只用于说明 execution-stage 自动化收益，不代表整个内容生产流程快 670 倍。