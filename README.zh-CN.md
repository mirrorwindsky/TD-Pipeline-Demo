# TD Pipeline Demo

[English](README.md) | 简体中文

这是一个面向 **Technical Designer（技术策划）求职作品集** 的项目，将可玩的 Unity Vertical Slice 与面向策划的内容生产管线、校验工具、Batch 自动化、QA 证据和真实流程量化结合在一起。

项目不是把玩法实现和脚本工具拆成彼此独立的练习，而是围绕一条连续工作流构建：

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

## 作品集概览

当前项目已经具备以下可验证证据：

- 可完整游玩的室内 Unity Vertical Slice；
- Windows standalone Build 已从启动到 Mission Complete 完整 Smoke Test；
- 多表 CSV → Python Typed Model → Unity JSON 的 Content Pipeline；
- Schema / malformed-row / type / range / duplicate 校验；
- `interactionType` 合法值校验；
- 跨表 Item Reference 校验；
- Active Scene `configId` 校验；
- 校验失败时保留上一版合法输出的 fail-safe generation；
- 经过验证的 Batch Preview / atomic Apply；
- 可复用的 **40 条 Scale Fixture**；
- 系统 QA 中发现并修复 **2 个真实校验 Bug**；
- 8 条批量修改受控对比：**人工 192.000 s vs 自动执行 0.287 s**；
- 独立 QA 记录与 Pipeline Case Study。

主要配套文档：

- [`Docs/Pipeline_Case_Study.zh-CN.md`](Docs/Pipeline_Case_Study.zh-CN.md) — 问题、设计、QA、Before / After 量化、取舍与结果；
- [`Docs/D11_QA.zh-CN.md`](Docs/D11_QA.zh-CN.md) — 可复现 Scale / 坏数据 QA 证据与 Bug 修复记录；
- [`TODO.md`](TODO.md) — 冲刺执行记录；
- [`STATUS.md`](STATUS.md) — 当前项目状态与下一步。

---

## 当前 Gameplay Slice

当前玩法 / Build 主场景：

```text
Assets/Scenes/VerticalSlice_01.unity
```

Week 1 原始基线保留在：

```text
Assets/Scenes/Prototype_01.unity
```

当前完整玩法依赖链：

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

当前切片包含：

- 封闭式多房间工业设施布局；
- 鼠标控制第三人称相机；
- 基于 CharacterController 的玩家相对移动与重力；
- 基于 `IInteractable` 的通用交互；
- Pickup / Device / Gate 三类玩法内容；
- 基于 ID 的最小 Inventory 状态；
- Required Item 与 prerequisite Device 依赖；
- 事件驱动 Gate 解锁与 Objective 推进；
- 配置驱动 Objective 文本；
- `[E] Interact`、瞬时 Feedback、持久 Mission Complete HUD；
- 基础材质、室内灯光、区域区分和可交互对象可读性；
- PowerNode / ControlTerminal / Exit 持久完成状态反馈。

Presentation Pass 后熟练玩家实测：

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

早期 5–8 分钟目标已经主动废弃。项目没有通过降速、长空走廊、无意义增加交互次数、强制搜索或无关玩法系统来硬凑时长。

Windows x86-64 standalone Build 已完成，并由用户本人从启动完整玩到 Mission Complete。Build 产物保持本地并由 Git ignore。

---

## 面向策划的 Content Pipeline

策划侧源数据：

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

正常生成流程：

```text
items.csv
+ objectives.csv
+ interactables.csv
        ↓
Parse Once SourceTables
        ↓
Schema / malformed-row / type / range / duplicate validation
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
interactables.json + objectives.json
        ↓
Unity config databases
        ↓
Runtime gameplay + HUD
```

Typed Intermediate Model：

```text
ContentModel
├── items: list[ItemConfig]
├── objectives: list[ObjectiveConfig]
└── interactables: list[InteractableConfig]
```

生成输出：

```text
Assets/Data/
├── interactables.json
└── objectives.json
```

生成 JSON 被视为 Pipeline Output，而不是正常工作流里由策划手工维护的第二份真值。

### 当前校验覆盖

Pipeline 当前会检查：

- CSV header 缺失；
- required column / value 缺失；
- unexpected extra columns / malformed rows；
- integer / boolean 类型错误；
- 非法或异常 interaction range；
- duplicate IDs；
- 非法 `interactionType`；
- 未知 `requiredItemId` / `grantedItemId`；
- `VerticalSlice_01.unity` 中受支持 Interactable 组件的 `configId` 引用；
- Validation failure 后上一版合法输出是否被保留。

Active Scene Reference Validator 只覆盖当前明确的 config-driven Interactable 组件集合，并不是通用的全 Scene / 全 Prefab dependency scanner。

---

## CLI

工具入口：

```text
Tools/config_tool.py
```

依赖：

- Python 3
- Unity 6.3 LTS（用于可玩项目）

查看命令：

```powershell
py Tools/config_tool.py --help
```

正常校验 + 生成：

```powershell
py Tools/config_tool.py
```

或：

```powershell
py Tools/config_tool.py generate
```

只 Preview、不修改源数据：

```powershell
py Tools/config_tool.py batch-preview
```

应用经过完整校验的 Batch：

```powershell
py Tools/config_tool.py batch-apply
```

Batch Apply 后再次运行 normal generation，使修改重新走完整 Validation 并进入 Unity 数据。

当前生成契约：

- `ERROR` 阻断 generation；
- `WARNING` 输出但不阻断 generation；
- Validation failure 不覆盖上一版合法 JSON；
- Batch Preview 不修改源文件；
- Batch Apply 在逻辑校验通过后使用 atomic source replacement。

---

## Batch Processing

当前真实 Batch 用例是批量修改 `requiredInteractions`。

```text
batch_interaction_updates.csv
↓
full-batch validation
↓
typed BatchInteractionUpdate objects
↓
Preview or Apply
↓
atomic source-file replacement
↓
normal Pipeline generation
↓
Unity Runtime
```

正常 Demo Batch 示例：

```text
cube_sturdy:       3 → 4
power_node:        3 → 2
control_terminal:  2 → 1
```

D11 进一步在 20 条 Interactable 的 Scale Fixture 上验证了 8 条 Batch：恰好只有目标 8 个 `requiredInteractions` 字段发生变化，其他字段保持不变，并且 8 个目标值全部正确进入生成 JSON。

---

## QA + Scale 证据

可复用合法 Fixture：

```text
QA/Fixtures/scale_valid/
├── items.csv                    8 records
├── objectives.csv              12 records
├── interactables.csv           20 records
└── batch_interaction_updates.csv 8 updates
```

Scale Test 总内容：

```text
40 records
```

QA 覆盖：

- 40 条合法数据生成；
- 8 条 Batch Preview；
- 8 条 Batch Apply + regeneration；
- required value 缺失；
- required column 缺失；
- duplicate IDs；
- invalid integer type；
- invalid range；
- invalid `interactionType`；
- broken cross-table Item reference；
- broken active-Scene `configId` reference；
- empty CSV；
- malformed CSV；
- fail-safe output preservation。

完整证据见：[`Docs/D11_QA.zh-CN.md`](Docs/D11_QA.zh-CN.md)

### 真实 Bug 1 — Active V2 Scene Reference Coverage

QA 复现了一个真实断链：`VerticalSlice_01.unity` 仍引用 `control_terminal`，但源配置 ID 已被改名，生成 JSON 中不再存在原 ID。修复前 Validator 仍然扫描 V1 baseline Scene，因此错误地让 Generation 通过。

修复后 Validator 改为针对 Active Scene 和当前 config-driven Interactable 组件白名单，同样的坏引用会在 JSON 生成前被阻断。

Main 修复提交：

```text
97b24be fix: validate active scene config references
```

### 真实 Bug 2 — Malformed CSV Silent Truncation

未转义逗号会产生额外 CSV 值。修复前 `csv.DictReader` 将溢出值放到 `None` key 下，而校验没有发现，导致 Objective description 被静默截断后仍然生成。

现在 `validate_schema()` 会对 unexpected extra values 输出 row-level ERROR 并阻断 Generation。

Main 修复提交：

```text
bb088b3 fix: reject malformed CSV rows with extra columns
```

### Fail-Safe 证据

针对 required value 缺失测试，D11 在失败 Generation 前后分别计算两个 generated JSON 的 SHA256；两个 Hash 均未变化。

```text
valid generated data
→ invalid source introduced
→ ERROR detected
→ generation blocked
→ previous valid JSON preserved
```

---

## Before / After 量化

使用同一套 40-record fixture 和同一组 8 条 `requiredInteractions` 修改做受控等价输出对比。

### 人工路径

人工流程：

1. 在 `ConfigSource/interactables.csv` 找到 8 个目标；
2. 手工修改 8 个源值；
3. 在生成 JSON 中找到对应 8 条记录；
4. 手工同步相同的 8 个值；
5. 检查并保存两份文件。

实测执行时间：

```text
192.000 s
```

独立校验：

```text
CSV records: 20
JSON records: 20
overall: PASS
0 unintended CSV field changes detected
```

### 自动路径

```text
batch-preview
→ batch-apply
→ generate
```

实测执行时间：

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

这明确是 **execution-stage benchmark**：不包含 Batch Request 本身的编写时间，也不代表“整个内容生产流程快 670 倍”。

这次人工和自动流程都没有错误，因此“风险下降”不从这次计时样本推断，而由 D11 的坏数据 QA、真实 Bug 和 fail-safe 证据单独支持。

完整分析见：[`Docs/Pipeline_Case_Study.zh-CN.md`](Docs/Pipeline_Case_Study.zh-CN.md)

---

## 设计取舍

以下扩展被有意留在当前 Scope 外：

- Unity Editor GUI；
- dependency visualization；
- generalized Quest framework；
- dependency-cycle detection；
- unreachable-objective detection；
- all-Scene / all-Prefab scanning；
- 大型 automated-test framework。

决策原则：

> 只有当前内容、QA 或工作流证明确实存在真实问题时，才为解决它增加复杂度。

例如：

- Editor Integration 被跳过，因为 CLI 已经能清晰完成 Generate / Preview / Apply，无需引入额外的 Python process launching 和 Editor-only 维护成本；
- cycle / unreachable checks 被跳过，因为当前 Objective architecture 并没有外部化为通用 dependency graph；
- Active Scene Reference Validation 只在 QA 实际复现 stale-ID 问题后扩展；
- malformed-row validation 只在 QA 实际复现 silent corruption 后加入。

---

## 项目结构

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   ├── interactables.json
│   │   └── objectives.json
│   ├── Materials/
│   │   └── D10Facility/
│   ├── Scenes/
│   │   ├── Prototype_01.unity
│   │   └── VerticalSlice_01.unity
│   └── Scripts/
│
├── ConfigSource/
│   ├── items.csv
│   ├── objectives.csv
│   ├── interactables.csv
│   └── batch_interaction_updates.csv
│
├── QA/
│   └── Fixtures/
│       └── scale_valid/
│
├── Docs/
│   ├── README.md
│   ├── D10_HANDOFF.md
│   ├── D11_QA.md
│   ├── D11_QA.zh-CN.md
│   ├── Pipeline_Case_Study.md
│   ├── Pipeline_Case_Study.zh-CN.md
│   ├── Pipeline_V1.md
│   └── Pipeline_V1.zh-CN.md
│
├── Tools/
│   └── config_tool.py
│
├── README.md
├── README.zh-CN.md
├── STATUS.md
└── TODO.md
```

---

## AI 辅助开发

AI / Codex 用于加速实现、检查和调试，而不是替代验证和理解。

项目没有为了满足 checklist 人为制造“AI 生成错误”。D11 中两个真实 QA Bug 都经历了具体输入复现、原因定位、小范围修复和回归验证，并被完整记录。

进入 README、Case Study、视频或简历的实现都应能够在不依赖 Codex 的情况下独立解释。

---

## 作品集 / 面试一句话说明

> 我做了一个 Unity Vertical Slice，并让真实玩法依赖推动 Python Content Pipeline 的演进。Pipeline 将多表 CSV 解析成 Typed Intermediate Model，校验 Schema、数值、重复 ID、跨表 Item 引用和 Active Scene Config 引用，再生成 Unity 可消费 JSON；同时加入经过完整校验的 atomic Batch Update。项目使用 40 条数据完成 Scale / QA，并通过 QA 发现并修复 2 个真实校验 Bug。在受控的 8 条批量修改 execution benchmark 中，人工等价输出耗时 192 秒，而 Batch Preview → Apply → Generate 耗时 0.287 秒；这个数字只用于说明 execution-stage 自动化收益，不代表整个内容生产流程快 670 倍。

---

## 当前封装状态

项目技术核心、QA 证据、Pipeline Case Study 以及中英文核心文档已经完成。

当前优先级已经转为：**简历、项目讲解和正式投递**，而不是继续增加功能。

后续可选项：

- 录制一段简短最终演示视频；
- 有机会时获取 TD / 用户外部反馈。

稳定作品源以 GitHub `main` 分支为准。