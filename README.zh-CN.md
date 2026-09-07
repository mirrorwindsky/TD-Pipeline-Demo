# TD Pipeline Demo

[English](README.md) | 简体中文

这是一个仍在持续开发中的 Technical Designer（技术策划）作品集项目，使用 Unity、C# 与 Python 探索**玩法 / 内容实现、数据驱动设计、校验工具、自动化与内容生产管线**。

## 项目概述

`TD-Pipeline-Demo` 将一个可玩的 Unity Gameplay Slice 与一条面向策划的配置生产管线结合在一起。

这个项目并不把玩法实现和工具开发拆成彼此独立的练习，而是把它们放进一条连续工作流中：

```text
策划侧 CSV
        ↓
Python 校验 / 生成
        ↓
生成 JSON
        ↓
Unity 配置加载
        ↓
运行时配置查找
        ↓
配置驱动玩法
```

本项目希望展示：

- Gameplay / Content Implementation（玩法 / 内容实现）
- Data-Driven Design（数据驱动设计）
- Python Tooling & Automation（Python 工具与自动化）
- Pre-Runtime Content Validation（运行前内容校验）
- Runtime Content Dependencies（运行时内容依赖）
- End-to-End Content Pipeline Understanding（端到端内容生产管线理解）
- Debugging & Iteration（调试与迭代）
- Explainable AI-Assisted Development（可解释的 AI 辅助开发）

---

## 当前里程碑

**Day 8 核心已完成：项目现在已经拥有一个可完整跑通的灰盒 Vertical Slice，以及第一版真正接入运行时的 Content Model V2。**

Week 1 的原始原型保留在：

```text
Assets/Scenes/Prototype_01.unity
```

当前玩法切片开发场景位于：

```text
Assets/Scenes/VerticalSlice_01.unity
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

当前 Vertical Slice 已包含：

- 多房间灰盒设施布局
- 基于 `CharacterController` 的移动与重力
- 平滑跟随相机
- 基于 `IInteractable` 的通用交互
- Pickup / Device / Gate 三类玩法内容
- 基于 ID 的最小 Inventory 状态
- Required Item 与 prerequisite Device 依赖
- 事件驱动的 Gate 解锁
- Interaction Prompt、Objective UI 与 Feedback
- 事件驱动的任务目标推进
- 从开始到结束可完整跑通的任务循环
- 由 CSV 驱动的 Pickup / Device 运行时参数

一次真实的源数据验证只修改了：

```text
power_node.requiredInteractions
3 → 5
```

然后运行：

```text
CSV
→ Python
→ JSON
→ Unity
```

最终验证 PowerNode 在运行时确实需要 5 次交互。

整个过程中：

- 没有手动修改生成 JSON
- 没有修改玩法 C# 代码

第二次验证则故意修改：

```text
power_node.requiredItemId
power_cell → fake_cell
```

当前生成工具仍会接受这个错误依赖，问题只会在运行时通过行为异常暴露出来。

这暴露出了下一阶段真实的 Pipeline 问题：

> **内容依赖已经可以通过源数据表达，但非法的跨记录引用还不能在运行前被校验。**

这将成为 Pipeline V2 的直接起点。

---

## 快速开始

### 环境要求

- Unity 6.3 LTS
- Python 3

### 1. 生成配置数据

当前面向策划的源配置位于：

```text
ConfigSource/interactables.csv
```

在项目根目录运行：

```powershell
py Tools/config_tool.py
```

校验通过后，工具会生成：

```text
Assets/Data/interactables.json
```

当前生成行为：

- 检测到 `ERROR` 时阻止生成
- `WARNING` 会报告，但不会阻止生成
- 被当前校验规则识别为非法的数据不会覆盖上一版合法生成结果

### 2. 运行当前 Vertical Slice

1. 使用 Unity 6.3 LTS 打开项目。
2. 打开 `Assets/Scenes/VerticalSlice_01.unity`。
3. 进入 Play Mode。
4. 按照屏幕上的 Objective 推进。
5. 在 Storage 找到并拾取 Power Cell。
6. 前往 Maintenance，使用它修复 Power Node。
7. 激活 Control Terminal。
8. 进入已经解锁的 Exit 区域。
9. 到达 EndMarker 完成任务。

当前玩法流程：

```text
找到 PowerCell
→ 修复 PowerNode
→ 激活 ControlTerminal
→ 解锁 ExitDoor
→ 到达 Exit
→ Mission Complete
```

原先的 `Prototype_01.unity` 仍保留为 Pipeline V1 / Week 1 基线场景。

---

## 玩法架构

### 玩家移动

```text
WASD
→ movement vector
→ normalization
→ CharacterController.Move()
→ gravity
→ player movement
```

玩家会朝当前移动方向旋转。

### 跟随相机

简单的跟随相机会在 `LateUpdate` 中，于玩家移动后更新。

这使玩家在更大的 Vertical Slice 场景中移动时仍能持续保持在合适视野内。

### 通用交互

玩家交互代码不再直接依赖某一个具体交互组件。

```text
E / forward Raycast
→ Interactable tag
→ IInteractable
→ 对象自己的交互逻辑
```

当前实现包括：

```text
IInteractable
├── ConfigurableInteractable   （V1 基线）
├── PickupInteractable         （V2 Pickup）
└── DeviceInteractable         （V2 Device）
```

因此，在新增交互类型时，玩家侧交互代码无需跟着修改。

### Inventory / Pickup

```text
PowerCell
→ PickupInteractable
→ PlayerInventory
→ grantedItemId = power_cell
```

`PlayerInventory` 当前使用：

```text
HashSet<string>
```

因为现阶段只需要：

- 判断某个 Item ID 是否存在
- 保证同一 Item ID 不重复

### Device 状态

`DeviceInteractable` 当前维护：

```text
前置条件是否满足？
        ↓
当前交互进度
        ↓
是否完成？
```

一个 Device 当前可以依赖：

- 一个 Item ID
- 另一个 `DeviceInteractable`
- 配置中的交互次数

当前 PowerNode 示例：

```text
PlayerInventory 中存在 power_cell
→ PowerNode 可操作
→ 消耗 power_cell
→ 推进 PowerNode 交互进度
→ PowerNode Completed
```

### Device 依赖

ControlTerminal 当前依赖 PowerNode 完成：

```text
PowerNode 未完成
→ ControlTerminal 被阻挡

PowerNode 已完成
→ ControlTerminal 可以操作
```

### Gate 流程

`GateController` 监听 ControlTerminal 的完成事件：

```text
ControlTerminal.Completed
→ GateController
→ ExitDoor 解锁
```

### Mission / Objective 流程

当前玩家看到的 Objective 顺序：

```text
Find a Power Cell in Storage
→ Repair the Power Node in Maintenance
→ Activate the Control Terminal
→ Reach the Exit
→ Mission Complete
```

HUD 当前提供：

- 当前 Objective
- Interaction Prompt
- 条件不足反馈
- 交互进度反馈
- 完成反馈

因此玩家现在可以在**不查看 Unity Console** 的情况下理解并完成整个流程。

---

## Content Model

当前源配置文件：

```text
ConfigSource/interactables.csv
```

当前字段包括：

- `id`
- `displayName`
- `interactionType`
- `requiredInteractions`
- `requiredItemId`
- `grantedItemId`
- `blockedMessage`
- `completionMessage`
- `deactivateOnComplete`

当前 V2 模型仍然是**单表结构**。

目前已经存在真实的数据关系，例如：

```text
power_cell
grantedItemId = power_cell
```

以及：

```text
power_node
requiredItemId = power_cell
requiredInteractions = 3
```

运行时内容通过：

```text
configId
↓
InteractableConfigDatabase
↓
InteractableConfig
```

获取对应配置。

同一套配置数据库现在已经被多个运行时组件消费：

```text
InteractableConfigDatabase
├── ConfigurableInteractable
├── PickupInteractable
└── DeviceInteractable
```

下一阶段 Pipeline V2 将优先强化源数据建模和引用校验，而不是继续无限扩张当前单表结构。

---

## Python 工具

当前 Pipeline 工具：

```text
Tools/config_tool.py
```

Week 1 形成的校验流程：

```text
CSV / Unity Scene
↓
Schema Validation
↓
Value / Range Validation
↓
Duplicate-ID Validation
↓
Scene Reference Validation
↓
ERROR / WARNING Gate
↓
Typed Configuration
↓
JSON Generation
```

当前已经包含的校验：

- CSV Header 缺失
- Required Column 缺失
- Required Field 值为空
- 非法整数
- 非法布尔值
- 非法交互范围
- 可疑的过大交互次数
- 重复 ID
- V1 Unity Scene 中的 `configId` 引用

当前工具还**不能**检查类似：

```text
requiredItemId = fake_cell
```

这样的字段是否真的引用了一个合法 Item / Content ID。

这正是 Pipeline V2 的明确目标之一。

---

## 项目结构

关键目录：

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   └── interactables.json
│   ├── Prefabs/
│   ├── Scenes/
│   │   ├── Prototype_01.unity
│   │   └── VerticalSlice_01.unity
│   ├── Scripts/
│   └── Settings/
│
├── ConfigSource/
│   └── interactables.csv
│
├── Docs/
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

### `ConfigSource`

面向策划的源配置。

### `Tools`

Python 校验、转换与内容生产管线工具。

### `Assets/Data`

Unity 运行时消费的生成配置。

### `Assets/Scripts`

当前 Gameplay 与 Pipeline 集成代码，包括：

- 玩家移动 / 重力
- 跟随相机
- 通用 Raycast 交互
- Inventory
- Pickup 行为
- Device 行为
- 配置数据类
- 配置数据库
- Gate 控制
- HUD
- Objective / Mission Flow

### `Assets/Scenes`

- `Prototype_01.unity` — Pipeline V1 / Week 1 基线
- `VerticalSlice_01.unity` — 当前 Gameplay Vertical Slice 开发场景

### `Docs`

用于说明项目技术实现与 Pipeline 的文档。

---

## 文档

- [`Docs/Pipeline_V1.md`](Docs/Pipeline_V1.md) — Pipeline V1 端到端流程、校验、Unity 加载、验证过程与当前边界
- [`Docs/Pipeline_V1.zh-CN.md`](Docs/Pipeline_V1.zh-CN.md) — 简体中文版本
- [`STATUS.md`](STATUS.md) — 当前项目状态与交接信息
- [`TODO.md`](TODO.md) — 当前 V2 Sprint 执行清单

Pipeline V2 文档将在 D9 架构与校验模型稳定后再补充。

---

## 技术栈

- Unity 6.3 LTS
- C#
- TextMeshPro
- Python
- CSV / JSON
- Git / GitHub

---

## 开发日志

### Day 1 — Minimal Unity Prototype

- 完成 Unity 6.3 LTS 项目初始化
- 完成基础移动、Raycast 交互、Debug 与 Git 初始化

### Day 2 — First Config-Driven Gameplay Chain

- 加入外部 JSON 配置
- 加入运行时 Dictionary 查找
- 验证配置修改可以改变运行时行为

### Day 3 — Python Tool V0

- 加入策划侧 CSV
- 完成 CSV → Python → JSON → Unity 的第一条生成链

### Day 4 — Demo V0

- 完成第一版可完整跑通的灰盒任务循环

### Day 5 — Python Tool V1

加入：

- Schema 校验
- 类型 / 范围校验
- Duplicate ID 校验
- `ERROR` / `WARNING`
- 可执行的错误信息
- Unity Scene 引用校验
- Fail-safe 生成

### Day 6 — Pipeline V1

验证：

```text
Designer CSV
→ Python Validation
→ Generated JSON
→ Unity
→ Runtime Gameplay
```

完成真实的：

```text
requiredInteractions
3 → 5
```

源数据到运行时验证。

并新增：

```text
Docs/Pipeline_V1.md
```

### Day 7 — Week 1 Wrap-up

- 回归测试 Demo V1 与 Tool V1
- 清理无关 Unity 模板资源
- 修正 Build Scene 配置
- 重构 README，使其更适合作品集外部阅读
- 加入中英文 README / Pipeline 文档
- 重构剩余 Sprint，使 D8–D10 聚焦 Vertical Slice + Pipeline V2

### Day 8 — Gameplay Vertical Slice + Content Model V2 Core

- 创建 `VerticalSlice_01.unity`
- 保留 `Prototype_01.unity` 作为 V1 基线
- 搭建多房间设施灰盒布局
- 为 CharacterController 增加重力
- 加入平滑跟随相机
- 引入 `IInteractable`
- 保留 V1 `ConfigurableInteractable` 兼容
- 加入 `PlayerInventory`
- 加入 `PickupInteractable`
- 加入可复用 `DeviceInteractable`
- 加入 Required Item 与 prerequisite Device 逻辑
- 加入事件驱动 `GateController`
- 加入 TextMeshPro Objective / Feedback / Prompt HUD
- 加入事件驱动的 Vertical Slice Objective Flow
- 加入最终任务完成 Trigger
- 扩展配置模型，加入 Interaction / Item / Feedback 相关字段
- 将 PowerCell 与 PowerNode 的行为重新接回 CSV 生成数据
- 验证 `requiredInteractions: 3 → 5` 可以传播到真实运行时玩法
- 故意测试 `requiredItemId = fake_cell`
- 识别出“缺少跨记录引用校验”这一真实 Pipeline V2 问题

当前 Day 8 完整玩法链：

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

---

## 当前范围

已知限制包括：

- 当前 Vertical Slice 视觉上仍然是灰盒
- 最终 5–8 分钟目标尚未正式计时
- 当前 Content Model V2 仍然只有一张 CSV
- `requiredItemId` 等跨记录引用尚不能在运行前校验
- `interactionType` 已经进入配置，但还没有合法 enum / value 校验
- V1 的 Unity 引用校验仍然只针对现有 `ConfigurableInteractable.configId`
- 当前 Validation 仍会多次读取 CSV，而不是共享同一个已解析 Intermediate Model
- 当前 Python 工具仍是 CLI

这些都是下一阶段明确的迭代目标，而不是当前实现已经解决的问题。

---

## 下一步

### Day 9 — Pipeline V2

下一阶段目标是把当前单表 Content Model V2 升级成更完整的内容生产 Pipeline。

计划包括：

- 在真实需要的地方引入多表源数据
- 将源数据统一 Parse Once
- 建立 Typed Intermediate Model
- 让 Validation 与 Generation 共用同一份解析结果
- 校验合法 `interactionType`
- 加入跨记录 / 跨表引用校验
- 在运行前拦截 `requiredItemId = fake_cell` 这类错误
- 保留现有 Schema、Type、Range、Duplicate-ID 与 Unity Reference Validation
- 加入至少一个真实 Batch Processing 工作流
