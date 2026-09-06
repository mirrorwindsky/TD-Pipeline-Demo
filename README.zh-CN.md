# TD Pipeline Demo

这是一个仍在持续开发中的 Technical Designer（技术策划）作品集项目，使用 Unity、C# 与 Python 探索**数据驱动玩法、内容校验、工具开发与内容生产管线自动化**。

## 项目概述

`TD-Pipeline-Demo` 将一个小型可玩 Unity 原型与面向策划的配置管线结合在一起。

项目并不把玩法实现和工具开发拆成彼此独立的练习，而是把它们连接成一条真实工作流：

```text
策划侧 CSV
        +
Unity Scene 引用
        ↓
Python 前置校验（Preflight Validation）
        ↓
通过校验的配置转换
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

- Gameplay / Content Implementation（玩法 / 内容落地）
- Data-Driven Design（数据驱动设计）
- Python Tooling & Automation（Python 工具与自动化）
- Pre-Runtime Content Validation（运行前内容校验）
- Cross-File Configuration Reference Checking（跨文件配置引用检查）
- End-to-End Content Pipeline Understanding（端到端内容生产管线理解）
- Debugging & Iteration（调试与迭代）
- Explainable AI-Assisted Development（可解释的 AI 辅助开发）

## 当前里程碑

**Pipeline V1 已完成，并通过端到端验证。**

当前项目已经包含：

- 一个可完整跑通的 Unity 灰盒任务循环
- 由外部配置驱动的运行时交互参数
- 面向策划的 CSV 源数据
- 自动 CSV → JSON 转换
- Schema、类型、范围、重复 ID 与 Unity Scene 引用校验
- `ERROR` / `WARNING` 严重级别处理
- 校验失败时保留上一版合法 JSON 的安全生成机制
- 通过 `Dictionary<string, InteractableConfig>` 完成运行时配置查找
- 已文档化并实际验证的“源数据 → 运行时”完整管线

一次真实的端到端验证只修改了：

```text
cube_sturdy.requiredInteractions
3 → 5
```

该值完整经过：

```text
CSV
→ Python 校验
→ 生成 JSON
→ Unity 配置加载
→ 运行时玩法
```

整个过程没有手动修改生成 JSON，也没有修改玩法 C# 代码。

数据修改后，完整玩法流程依旧能够正常运行：

```text
StartGate
→ 配置驱动目标
→ 目标完成
→ 出口解锁
→ EndMarker
→ Demo Complete
```

## 快速开始

### 环境要求

- Unity 6.3 LTS
- Python 3

### 1. 生成经过校验的配置数据

面向策划的源配置位于：

```text
ConfigSource/interactables.csv
```

在项目根目录运行：

```powershell
py Tools/config_tool.py
```

如果校验通过，工具会生成：

```text
Assets/Data/interactables.json
```

如果检测到任意 `ERROR`：

- 停止 JSON 生成
- 输出可定位、可执行的错误信息
- 保留上一版合法的生成 JSON

`WARNING` 会被报告，但不会阻止生成。

### 2. 运行 Unity Demo

1. 使用 Unity 6.3 LTS 打开项目。
2. 打开 `Assets/Scenes/Prototype_01.unity`。
3. 进入 Play Mode。
4. 通过 `StartGate`。
5. 完成两个可配置交互目标。
6. 两个目标都完成后，出口打开。
7. 到达 `EndMarker`，完成当前 Demo 流程。

当前玩法流程：

```text
StartGate
→ 配置驱动目标
→ Completed Events
→ 出口解锁
→ EndMarker
→ Demo Complete
```

## 核心管线

### 策划侧源数据

玩法配置编辑于：

```text
ConfigSource/interactables.csv
```

当前字段包括：

- `id`
- `displayName`
- `requiredInteractions`
- `deactivateOnComplete`

CSV 被视为当前交互物配置的可编辑 Source of Truth（源数据真值）。

正常工作流中不应手动修改生成后的 JSON。

### Python 工具

管线工具位于：

```text
Tools/config_tool.py
```

当前处理流程：

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

### 校验

当前校验包括：

- CSV 表头缺失
- 必需列缺失
- 必需字段为空
- 非法整数值
- 非法布尔值
- 非法交互次数范围
- 可疑的交互次数数值
- 重复配置 ID
- Unity Scene 中失效的 `configId` 引用

一个典型的 Broken Reference（失效引用）示例：

```text
CSV:
cube_sturdy → 重命名为 cube_sturdy_v2

Unity Scene:
configId = cube_sturdy
```

Python 工具会发现 Scene 仍引用已经不存在的 ID，并在错误配置进入 Unity Runtime 之前阻止 JSON 生成。

### 生成数据

通过校验的源数据会被转换为：

```text
Assets/Data/interactables.json
```

当前转换过程：

```text
CSV strings
↓
Python 类型转换
↓
InteractableConfig dataclass
↓
Dictionary representation
↓
JSON
```

### Unity 加载

Unity 通过 `InteractableConfigDatabase` 消费生成后的 JSON。

```text
interactables.json
↓
TextAsset
↓
InteractableConfigDatabase.Awake()
↓
JsonUtility.FromJson
↓
InteractableConfigCollection
↓
List<InteractableConfig>
↓
Dictionary<string, InteractableConfig>
```

每个 `ConfigurableInteractable` 都保存一个序列化的 `configId`，并通过 Dictionary 查找对应的运行时配置。

例如：

```text
SturdyCube
↓
configId = cube_sturdy
↓
Dictionary lookup
↓
requiredInteractions = 3
↓
运行时交互行为
```

## 文档

- [`Docs/Pipeline_V1.md`](Docs/Pipeline_V1.md) — 完整端到端管线、各校验阶段、Unity 加载路径、运行时流程、验证过程与当前能力边界。
- [`STATUS.md`](STATUS.md) — 当前项目状态与里程碑交接信息。
- [`TODO.md`](TODO.md) — 当前冲刺执行清单与后续工作。

## 项目结构

核心项目结构：

```text
TD-Pipeline-Demo/
├── Assets/
│   ├── Data/
│   │   └── interactables.json
│   ├── Prefabs/
│   ├── Scenes/
│   │   └── Prototype_01.unity
│   ├── Scripts/
│   └── Settings/
│
├── ConfigSource/
│   └── interactables.csv
│
├── Docs/
│   └── Pipeline_V1.md
│
├── Tools/
│   └── config_tool.py
│
├── README.md
├── STATUS.md
└── TODO.md
```

### `ConfigSource`

面向策划的源配置数据。

### `Tools`

Python 校验、转换与管线工具。

### `Assets/Data`

供 Unity 消费的生成配置。

### `Assets/Scripts`

当前玩法与配置系统，包括：

- 玩家移动
- Raycast 交互
- 配置数据类
- 配置数据库
- 配置驱动交互物行为
- 任务 / 目标流程

### `Assets/Scenes`

包含当前有效原型场景：

```text
Prototype_01.unity
```

### `Docs`

用于保存项目本身的技术和管线文档，而不是冲刺过程管理状态。

## 当前运行时行为

### 玩家移动

```text
WASD input
→ movement vector
→ normalization
→ CharacterController.Move()
→ 玩家移动
```

### 交互

```text
E input
→ forward Physics.Raycast
→ Interactable tag check
→ ConfigurableInteractable.Interact()
```

### 配置驱动目标

```text
ConfigurableInteractable
→ configId lookup
→ requiredInteractions
→ interaction progress
→ Completed event
```

### 任务流程

```text
StartTrigger
→ Mission Start
→ Complete 2 Objectives
→ Completed Events
→ DemoFlowController
→ ExitDoor Opens
→ EndTrigger
→ Demo Complete
```

## 技术栈

- Unity 6.3 LTS
- C#
- Python
- CSV / JSON
- Git / GitHub

## 开发记录

### Day 1 — Unity 最小原型

- 建立 Unity 6.3 LTS 项目
- 创建初始灰盒场景
- 使用 `CharacterController` 实现 WASD 移动
- 对输入方向做 Normalize，避免斜向移动速度更快
- 让玩家朝移动方向转向
- 使用 `Physics.Raycast` 实现 E 键交互
- 增加 `Interactable` Tag 检查
- 使用 Console Log 与 `Debug.DrawRay` 调试交互链

验证链路：

```text
Input
→ Raycast
→ Tag Check
→ Interaction
```

### Day 2 — 第一条配置驱动玩法链

- 添加外部 JSON 配置
- 添加可序列化 C# 配置类
- 使用 `JsonUtility` 加载 JSON
- 使用 `List<InteractableConfig>` 保存配置
- 使用 `Dictionary<string, InteractableConfig>` 建立运行时 ID 查询
- 添加 `ConfigurableInteractable`
- 允许 GameObject 通过 `configId` 选择配置
- 验证配置数值可以在不修改玩法逻辑的情况下改变运行时行为

初始配置链：

```text
interactables.json
→ JsonUtility
→ List<InteractableConfig>
→ Dictionary lookup
→ ConfigurableInteractable
→ Runtime behavior
```

### Day 3 — Python Tool V0

- 添加 `ConfigSource/interactables.csv`
- 添加 `Tools/config_tool.py`
- 使用 `pathlib` 处理项目相对路径
- 使用 `csv.DictReader` 读取源数据
- 添加 Python `InteractableConfig` dataclass
- 将 CSV 字符串转换为带类型的数据
- 使用 `json.dump` 生成 Unity 可消费 JSON
- 验证 CSV 修改能够经过 Python 与 JSON 传播到 Unity Runtime

第一版策划侧管线：

```text
CSV Source Data
→ Python Config Tool
→ Generated JSON
→ Unity Config Database
→ Runtime Gameplay
```

### Day 4 — Demo V0

- 建立完整灰盒玩法闭环
- 创建可复用 `StartGate` Prefab
- 添加基于 Trigger 的任务开始
- 给可配置交互物添加 `Completed` event
- 添加 `DemoFlowController`
- 使用 QuickCube 与 SturdyCube 作为配置驱动目标
- 两个目标完成后打开 `ExitDoor`
- 添加 `EndTrigger`
- 验证两个目标完成顺序任意
- 验证重复进入 StartGate 不会重新开始任务

玩法闭环：

```text
Start Trigger
→ Mission Start
→ Complete 2 Config-Driven Objectives
→ Completed Events
→ Exit Unlock
→ End Trigger
→ Demo Complete
```

### Day 5 — Python Tool V1

将 Python 转换脚本升级为带校验能力的内容工具。

新增：

- Schema / 缺字段校验
- 类型校验
- 范围校验
- 重复 ID 校验
- `ERROR` / `WARNING` 分级
- 可定位到文件 / 行 / 字段的错误信息
- Unity Scene `configId` 引用校验
- Fail-Safe Generation（失败保护生成）
- JSON 生成前的数据标准化

实际验证过：

- 缺字段值
- 缺必需列
- 非法整数
- 非法范围
- 非法布尔值
- 重复 ID
- Scene 失效引用
- 单次运行同时报告多个独立问题

### Day 6 — Pipeline V1

重新验证了完整的“源数据 → 运行时”工作流。

测试：

```text
cube_sturdy.requiredInteractions
3 → 5
```

过程：

1. 只修改策划侧 CSV。
2. 运行 `Tools/config_tool.py`。
3. 校验通过。
4. JSON 自动重新生成。
5. Unity 加载新配置。
6. SturdyCube 恰好需要 5 次交互。
7. 目标完成与出口解锁仍然正常工作。
8. Demo 最终到达 `Demo Complete`。
9. 将源值恢复为 3，并重新生成合法基线。

新增：

```text
Docs/Pipeline_V1.md
```

用于记录完整管线与当前能力边界。

### Day 7 — Week 1 里程碑收尾

当前收尾工作包括：

- 重新测试 Demo V1 与 Tool V1，没有发现阻断性错误
- 清理不属于项目本体的 Unity 模板 / 教学资产
- 将 Unity Build Scene List 更新为 `Prototype_01.unity`
- 清理后重新运行 Python 管线并成功通过
- 清理后重新完整跑通 Unity 玩法流程
- 将 README 重构为面向外部读者 / 作品展示的结构

## 当前范围

当前实现刻意保持小规模，重点是证明完整的内容生产链路。

已知限制包括：

- Scene 引用校验目前只针对当前原型场景，而不是所有 Scene 与 Prefab
- 缺失或完全畸形的源文件尚未被完整处理
- Unity 侧配置鲁棒性仍较基础
- 当前 Python 工具仍以 CLI 为主
- 玩法 Demo 仍是刻意保持简洁的灰盒原型
- 各 validator 目前分别读取 CSV，而不是共享一个统一解析后的中间表示

这些限制被明确视为后续迭代机会，而不是被隐藏在过度宽泛的能力描述中。

## 下一步

第一版完整 Pipeline V1 里程碑已经成立。

接下来的重点是完成 Week 1 收尾，并在进入下一阶段实现前，重新评估后续冲刺工作的范围与深度。
