# TD Pipeline Demo

[English](README.md) | 简体中文

**可玩版本：** [下载 Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/download/v1.0.0/TD-Pipeline-Demo-Windows-x64-v1.0.0.zip) · [Release Notes](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

这是一个面向 **Technical Designer（技术策划）求职作品集** 的项目，将可玩的 Unity Vertical Slice 与面向策划的内容生产管线、校验工具、Batch 自动化、QA 证据和真实流程量化结合在一起。

```text
Game Content Vertical Slice
↕
Content Model
↕
Python Validation / Batch Pipeline
```

## 作品集概览

- 可完整游玩的室内 Unity Vertical Slice，并已发布 Windows x86-64 standalone Release；
- 多表 CSV → Python Typed Model → Unity JSON 的 Content Pipeline；
- Schema / malformed-row / type / range / duplicate 校验；
- `interactionType`、跨表 Item Reference、Active Scene `configId` 校验；
- 校验失败时保留上一版合法输出的 fail-safe generation；
- 经过验证的 Batch Preview / atomic Apply；
- 可复用的 **40 条 Scale Fixture**；
- 系统 QA 中发现并修复 **2 个真实校验 Bug**；
- 8 条批量修改受控对比：**人工 192.000 s vs 自动执行 0.287 s**；
- 中英文 QA 记录与 Pipeline Case Study。

主要配套文档：

- Pipeline Case Study：[`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md)
- Day 11 QA Record：[`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md)
- [`Docs/README.md`](Docs/README.md) — 当前文档 / 历史文档索引
- [`TODO.md`](TODO.md) — 冲刺执行记录
- [`STATUS.md`](STATUS.md) — 当前项目状态

---

## 可玩版本

当前作品集 Release：

```text
v1.0.0
Windows x86-64
Unity 6.3 LTS
```

从上方 GitHub Release 下载完整压缩包，解压后运行：

```text
TD-Pipeline-Demo.exe
```

操作方式：

- `WASD` — 移动
- Mouse — 控制镜头
- `E` — 交互
- `Esc` — 释放鼠标
- 关闭窗口即可退出

该版本已经从启动到 Mission Complete 完成人工测试。Build 产物仍不进入 Git 历史，正式可玩包通过 GitHub Releases 分发。

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

完整玩法依赖链：

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

当前切片包含多房间工业设施布局、第三人称鼠标相机、玩家相对移动、基于 `IInteractable` 的通用交互、Pickup / Device / Gate 内容、最小 Inventory 状态、配置驱动 Item 依赖与 Objective 文本、事件驱动 Gate / Mission 流程、HUD 反馈、材质、灯光以及持久 World-State Feedback。

Presentation Pass 后熟练玩家实测：

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

早期 5–8 分钟目标已经主动废弃，没有通过 filler 硬凑时长。

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
items.csv + objectives.csv + interactables.csv
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

Typed Model：

```text
ContentModel
├── items: list[ItemConfig]
├── objectives: list[ObjectiveConfig]
└── interactables: list[InteractableConfig]
```

生成 JSON 被视为 Pipeline Output，而不是由策划手工维护的第二份真值。

### CLI

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

生成契约：

- `ERROR` 阻断 generation；
- `WARNING` 输出但不阻断；
- Validation failure 不覆盖上一版合法 JSON；
- Batch Preview 不修改源数据；
- Batch Apply 在完整逻辑校验通过后进行 atomic source replacement。

---

## QA + Scale 证据

可复用 Fixture：

```text
QA/Fixtures/scale_valid/
├── items.csv                     8 records
├── objectives.csv               12 records
├── interactables.csv            20 records
└── batch_interaction_updates.csv 8 updates
```

Scale Test 总内容：**40 records**。

QA 覆盖合法 Scale 生成、Batch Preview / Apply、required value / column 缺失、duplicate IDs、invalid type / range / `interactionType`、broken cross-table reference、broken active-Scene config reference、empty CSV、malformed row 以及 fail-safe output preservation。

QA 中发现并修复两个真实缺陷：

1. **Active V2 Scene Reference Coverage Gap** — `VerticalSlice_01.unity` 中 stale `configId` 原本可能错误通过 Validation；修复提交 `97b24be`。
2. **Malformed CSV Silent Truncation** — 未转义逗号原本可能被接受并静默截断 Objective 内容；修复提交 `bb088b3`。

在一次非法源数据测试中，失败 Generation 前后两个 generated JSON 的 SHA256 均未变化，直接验证了“保留上一版 known-good output”的契约。

完整证据：[`English`](Docs/D11_QA.md) | [`简体中文`](Docs/D11_QA.zh-CN.md)

---

## Before / After 量化

使用同一套 40-record fixture 和同一组 8 条 `requiredInteractions` 修改进行等价输出对比：

```text
Manual execution:       192.000 s
Automated execution:      0.287 s
Execution speedup:        ~670×
Execution-time reduction: ~99.85%
```

自动路径：

```text
batch-preview
→ batch-apply
→ generate
```

人工和自动输出均通过独立校验。

这明确是 **execution-stage benchmark**：不包含 Batch Request 本身的编写时间，也不代表“整个内容生产流程快 670 倍”。错误风险下降由 D11 的 QA 证据单独支持，而不是从这次计时样本推断。

完整分析：[`English`](Docs/Pipeline_Case_Study.md) | [`简体中文`](Docs/Pipeline_Case_Study.zh-CN.md)

---

## 设计取舍

项目有意没有加入 Unity Editor GUI、dependency visualization、generalized Quest framework、cycle / unreachable-objective detection、全 Scene / 全 Prefab scanning 或大型 test framework。

决策原则：

> 只有实现、QA 或工作流证明确实存在真实问题时，才为解决它增加复杂度。

Active Scene Reference Validator 与 malformed-row validation 都是在 QA 实际复现失败后才加入的。

---

## 文档结构

当前作品集文档：

```text
README.md / README.zh-CN.md
→ 作品集入口 + 可玩 Release

Docs/Pipeline_Case_Study.md / .zh-CN.md
→ Problem / Design / QA / Benchmark / Trade-offs / Outcome

Docs/D11_QA.md / .zh-CN.md
→ 可复现 QA 与 Bug 修复证据

QA/Fixtures/scale_valid/
→ 可复用 Scale / Benchmark Fixture
```

`D10_HANDOFF.md`、`Pipeline_V1.md` 等旧文档有意保留为历史里程碑快照，而不是改写成最终 V2 规格。

---

## AI 辅助开发

AI / Codex 用于加速实现、检查和调试，而不是替代验证和理解。两个 QA Bug 都经历了具体输入复现、原因定位、小范围修复和回归测试。进入 README、Case Study、视频或简历的内容都应能够在不依赖 Codex 的情况下独立解释。

---

## 作品集 / 面试一句话说明

> 我做了一个 Unity Vertical Slice，并让真实玩法依赖推动 Python Content Pipeline 的演进。Pipeline 将多表 CSV 解析成 Typed Intermediate Model，校验 Schema、数值、重复 ID、跨表 Item 引用和 Active Scene Config 引用，再生成 Unity 可消费 JSON；同时加入经过完整校验的 atomic Batch Update。项目使用 40 条数据完成 Scale / QA，并通过 QA 发现并修复 2 个真实校验 Bug。在受控的 8 条批量修改 execution benchmark 中，人工等价输出耗时 192 秒，而 Batch Preview → Apply → Generate 耗时 0.287 秒；这个数字只用于说明 execution-stage 自动化收益，不代表整个内容生产流程快 670 倍。

---

## 当前状态

项目技术核心、QA 证据、量化 Case Study、中英文文档以及可玩的 **v1.0.0 Windows x64 Release** 已全部完成。

下一优先级是：**简历、项目讲解和正式投递**，而不是继续增加功能。
