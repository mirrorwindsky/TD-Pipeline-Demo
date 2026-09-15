# 内容配置管线案例 — TD Pipeline Demo

[English](Pipeline_Case_Study.md) | 简体中文

**可玩版本：** [Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

## 项目与设计演进

`TD-Pipeline-Demo` 是一个技术策划作品集项目，将 Unity 玩法切片与 CSV 编写、Python 校验、JSON 生成和运行时玩法连接起来。技术栈为 Unity 6.3 LTS、C#、Python、CSV / JSON、Git / GitHub。

可玩流程为 `PowerCell → PlayerInventory → PowerNode → ControlTerminal → ExitDoor → Mission Complete`。管线围绕这个小型切片中的内容依赖开发和验证。

| 阶段 | 主要工作 |
| --- | --- |
| V1，Week 1 | 单张交互物表、运行前校验，以及源数据到玩法的验证 |
| V2，Day 11 | 多表解析与类型模型、物品和场景引用、批量调参、规模 QA 和受控计时 |
| 配置工具 V3 | 独立中英文 GUI/EXE、外部规则、草稿编辑、AI 规则提案，以及各入口共享校验 |

V3 已包含在提交 `22c992e` 中。下文的 QA 发现与基准保留 Day 11 的版本背景，本次文档更新没有新增 V3 性能测量。

## 1. 内容配置中的问题

切片从单表扩展后，配置工作需要处理：

- 多表列结构与必填值的一致性；
- `requiredInteractions` 的整数/范围检查、ID 唯一性和交互类型合法性；
- 交互物引用物品 ID，以及场景中序列化的 configId 引用；
- 多条记录调参时反复查找和编辑；
- CSV 格式错误，以及校验失败时保留合法输出。

V3 根据技术策划从业者反馈继续调整：日常使用纯命令行不够方便，修改项目标准还需要编辑 Python。因此新增桌面界面和外部规则，并提供可选的自然语言编写入口。所有内容检查由本地引擎执行。

## 2. 当前 V3 设计

### 数据与校验

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
├── batch_interaction_updates.csv
└── validation_rules.json
```

```text
CSV → SourceTable（原始字符串，每次操作解析一次）
→ 可配置规则引擎 → 无 ERROR → 带类型的 ContentModel
→ interactables.json + objectives.json → Unity 配置数据库 → 玩法 / HUD
```

`ContentModel` 包含 `ItemConfig`、`ObjectiveConfig`、`InteractableConfig` 列表。物品记录用于引用检查，两份输出位于 `Assets/Data`。内容在 CSV 中修改，再通过生成同步。Unity JSON 字段和玩法保持原样，`interactionType` 基线仍为 `Pickup`、`Device`。

外部规则文件定义项目标准，Python 实现规则的执行方式。支持必需列、必填值、类型、范围、枚举、唯一值、正则、跨表引用和场景引用。22 条基线规则覆盖：

- 各表的必需列、必填值和 ID 唯一性；
- 整数交互次数与布尔完成状态；
- `requiredInteractions >= 1`，低于下限报错，超过 10 警告；
- `interactionType`、`requiredItemId` / `grantedItemId → items.id`、Batch 目标 ID；
- `VerticalSlice_01.unity` 中 `ConfigurableInteractable`、`PickupInteractable`、`DeviceInteractable` 的 configId 引用。

规则使用前会检查配置结构，停用的规则也必须合法。缺失/重复表头、破损引号和行列数不一致始终属于解析错误；类型转换还会检查 Unity 整数和布尔格式。内容错误阻止生成和批量写入，警告允许继续。校验失败保留原 JSON。

`config_tool.py` 负责 CLI 分发；共享服务、数据模型和规则分别位于 `pipeline_core.py`、`pipeline_model.py`、`rule_engine.py`，`rule_authoring.py` 管理草稿与提案。GUI 和凭据也有独立模块。各入口使用结构化 `ValidationIssue`。完整模块说明见[技术实现](技术实现.md)。

### GUI 与批量调参

tkinter/ttk GUI 默认中文，可切换英文并保留当前工作。它支持规则增删改、复制、启用/停用、草稿校验、显式保存/重载、生成和 Batch 预览/应用。Windows EXE 自带运行环境，并定位外部项目目录。

草稿可直接试用：把次数下限从 1 改为 4，当前 5 个交互物会报错；恢复为 1 后通过。**保存规则** 单独写入规则配置，与内容生成分开。

Batch 仍用于修改 `requiredInteractions`：

```text
batch_interaction_updates.csv → 检查更新表 → 在内存中修改
→ 校验全部修改后数据及场景引用 → 预览或原子写入 CSV
→ 生成 JSON
```

预览不改源文件。应用前检查全部修改后数据，包括未修改的行；通过后才写入 `interactables.csv`。次数下限与普通校验、生成共用同一条规则，`BatchInteractionUpdate` 提供修改前后的数值供核对。

规则和 CSV 通过临时文件原子替换。JSON 会先准备两份输出，普通写入失败时尝试回滚；多个文件之间没有断电事务保障。保存规则前还会检查文件是否被其他程序修改。

### AI 辅助规则编写

```text
自然语言需求 + 表头 + 支持的类型 + 当前规则
→ AI 服务 → 检查 RulePatch → GUI 预览 → 应用到草稿
→ 确定性内容校验 → 用户决定是否保存规则
```

OpenAI 和 DeepSeek 支持新增、更新和停用规则的提案。工具检查 JSON、操作/类型/表/字段、参数、正则、引用、ID 冲突和更新目标，应用前再次检查提案与草稿基准。AI 不接收 CSV 行数据，也不能删除规则、执行生成的 Python 或保存文件。Fake Provider 用于离线演示和自动测试。

密钥可在 GUI 的遮蔽输入框中填写，默认仅本次使用。用户明确选择记住后，Windows 凭据管理器会按服务分别保存，项目中不落盘明文密钥。环境变量保留为兼容方式。全部非 AI 功能无需密钥或 SDK。

入口命令：

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

无子命令时仍执行生成。打包输出为 `Builds/ConfigTool/TDConfigTool.exe`，构建产物不进入 Git。操作步骤见[使用说明](使用说明.md)。

## 3. Day 11 QA 证据

`QA/Fixtures/scale_valid/` 包含 8 个物品、12 个目标和 20 个交互物，共 **40 条内容记录**，另有 8 条批量更新。它用于检查超出最初几行数据后的行为，测试范围未涵盖商业项目规模的性能。

当时记录的结果：

- 生成通过，输出 20 个交互物和 12 个目标；
- 预览正确显示 8 条更新，源文件无变化；
- 应用仅改变目标 8 个 `requiredInteractions`，其他字段不变；
- 重新生成后，8 个目标值均进入 JSON；
- 坏数据测试覆盖缺列、缺值、重复 ID、整数/范围/交互类型错误、物品/场景引用失效、空 CSV 和多余列。

### 场景引用覆盖缺口

源 ID `control_terminal` 改为 `control_terminal_renamed` 后，场景仍保留 `configId: control_terminal`。生成最初错误通过，因为校验器仍扫描 `Prototype_01.unity`，且只识别 `ConfigurableInteractable`。

提交 `97b24be`（`fix: validate active scene config references`）将校验目标改为 `VerticalSlice_01.unity`，覆盖 `ConfigurableInteractable`、`PickupInteractable`、`DeviceInteractable`。相同坏数据被拦截，合法规模样例恢复通过。V3 将这一范围保留在场景引用规则中。

### CSV 静默截断

以下三列目标记录包含未转义逗号：

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` 将溢出值放在 `None` 键下。旧管线忽略了该值，报告成功并生成被截短的描述。提交 `bb088b3`（`fix: reject malformed CSV rows with extra columns`）在当时的 `validate_schema()` 中加入拦截。V3 在 `pipeline_core.parse_csv_table()` 中保留该项解析完整性检查。

### 输出保留与 V3 回归

必填值缺失导致生成失败时，两份 JSON 的 SHA256 均未改变。[Day 11 记录](D11_QA.zh-CN.md)保留了具体输入、日志、哈希和修复结果。

V3 在 `unittest` 中继续使用规模样例，并覆盖规则配置、规则变更对 Batch 的影响、JSON 格式、写入失败、草稿存储、界面语言切换、AI 响应、密钥和 EXE 项目定位。测试使用临时项目副本，AI 请求由 mock 提供。Tk 测试需要桌面环境，Windows 凭据真实存取测试需显式启用。这些测试不用于评价在线模型的回复质量，也没有产生新的性能测量结果。

## 4. 历史执行基准

Day 11 后续基准使用同一套 40 条样例和相同的 8 项修改：

| ID | 修改前 | 修改后 |
| --- | --- | --- |
| cube_sturdy | 3 | 4 |
| power_node | 3 | 2 |
| control_terminal | 2 | 1 |
| aux_power_box | 2 | 3 |
| coolant_pump | 3 | 4 |
| sensor_array | 4 | 2 |
| backup_generator | 5 | 3 |
| maintenance_panel | 4 | 5 |

人工路径逐条查找和编辑 CSV，再定位 JSON 中对应记录、同步数值、核对并保存两份文件。自动路径执行 `batch-preview → batch-apply → generate`。

| 测量项 | 记录结果 |
| --- | --- |
| 人工执行 | 192.000 s |
| 自动执行，PowerShell `Measure-Command` | 0.2865603 s，四舍五入为 0.287 s |
| 执行提速 | 约 670 倍 |
| 执行用时减少 | 约 99.85% |

独立校验确认 CSV 和 JSON 均为 20 条记录，8 项修改全部正确，CSV 其他字段无额外变化。两条路径均通过，错误数均为 0。

测量从批量更新请求准备好后开始，只计执行阶段，未计请求编写与完整生产周期，且发生在 V3 之前。提速结果仅适用于此样本。错误拦截由单独的坏数据 QA 支持；这个零错误计时样本无法量化错误率下降。

## 5. 取舍与结果

管线将反复同步 CSV/JSON 的工作收敛为批量核对、校验和生成，提供规则、行、字段和值的定位信息，在运行前发现失效引用，并在校验失败时保留原输出。

实现范围根据实际工作确定：

- 独立 GUI 解决日常使用问题；Unity Editor 集成会增加一套维护入口。
- 外部规则支持调整标准，Python 负责执行已支持的规则类型。
- AI 帮助编写规则，预览、应用和保存仍由用户操作。
- 项目尚无通用目标依赖图，环路和不可达目标检查暂缓。
- 全场景/全 prefab 扫描、依赖可视化和大型测试框架未纳入范围。当前工具采用标准库测试，Python 正则检查没有执行超时。
- 场景引用覆盖与异常行拦截根据两次已复现的 QA 缺陷扩展。

项目形成了可玩切片、数据驱动内容、多表类型模型、可配置校验、桌面工具、Batch 自动化和可选 AI 规则编写流程。证据包括 Day 11 规模与坏数据测试、哈希验证的输出保留、限定范围的执行基准、V3 回归测试，以及 v1.0.0 Windows x64 从启动到 Mission Complete 的人工测试记录。
