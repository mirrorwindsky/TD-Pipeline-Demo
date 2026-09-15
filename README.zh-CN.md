# TD Pipeline Demo

[English](README.md) | 简体中文

**可玩版本：** [下载 Windows x64 v1.0.0](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/download/v1.0.0/TD-Pipeline-Demo-Windows-x64-v1.0.0.zip) · [版本说明](https://github.com/mirrorwindsky/TD-Pipeline-Demo/releases/tag/v1.0.0)

这是一个 Technical Designer（技术策划）作品集项目，包含可玩的 Unity 玩法切片和 Python 内容配置管线，覆盖 CSV 编写、数据校验、JSON 生成、批量调参及 QA。**配置工具 V3** 新增独立桌面 GUI、可编辑校验规则和 AI 规则提案。

技术栈：Unity 6.3 LTS、C#、Python、CSV / JSON、Git / GitHub。

## 运行项目

### Unity 可玩版本

下载并完整解压发行包，运行 `TD-Pipeline-Demo.exe`。v1.0.0 Windows x86-64 版本已完成从启动到 Mission Complete 的人工测试。

| 操作 | 功能 |
| --- | --- |
| WASD | 移动 |
| 鼠标 | 控制镜头 |
| E | 交互 |
| Esc | 释放鼠标 |
| 关闭窗口 | 退出 |

### 配置工具 V3

安装 Python 3.10 及以上版本（含 tkinter）后，在项目根目录运行：

```powershell
py Tools/config_tool.py gui
```

界面默认中文，右上角可切换 English。需要 Windows EXE 时，运行：

```powershell
py Tools/build_exe.py
```

生成的 `Builds/ConfigTool/TDConfigTool.exe` 自带 Python 和 tkinter。它会从自身位置查找项目；移到项目外时，会提示选择项目目录。CSV、规则和生成结果仍保存在所选项目中。构建产物不进入 Git；Unity 可玩版本与配置工具使用各自的启动程序。

详细操作见[使用说明](Docs/使用说明.md)，模块与数据流程见[技术实现](Docs/技术实现.md)。

## 玩法切片

当前玩法与构建主场景为 `Assets/Scenes/VerticalSlice_01.unity`，Week 1 原型保留在 `Assets/Scenes/Prototype_01.unity`。

```text
PowerCell → PlayerInventory → PowerNode → ControlTerminal
→ ExitDoor → EndMarker → Mission Complete
```

切片包含多房间工业设施、第三人称鼠标相机、玩家相对移动、基于 `IInteractable` 的交互、拾取物、设备、门、最小背包状态、配置驱动物品需求与目标文本，以及事件驱动的门和任务流程。视觉整理阶段补充了 HUD、材质、灯光和持续显示的世界状态反馈。

## 内容配置管线 V3

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
├── batch_interaction_updates.csv
└── validation_rules.json
```

```text
CSV → SourceTable（原始字符串）→ 可配置规则引擎 → 无 ERROR
→ 带类型的 ContentModel → Unity JSON → 配置数据库 → 玩法 / HUD
```

`ContentModel` 包含 `ItemConfig`、`ObjectiveConfig`、`InteractableConfig` 列表。输出为 `Assets/Data/interactables.json` 和 `objectives.json`；items 提供物品引用表。日常修改在 CSV 中完成，再重新生成 JSON。

外部 JSON 包含 22 条基线规则，支持必需列、必填值、整数/布尔/文本类型、范围、枚举、唯一值、正则、跨表引用和场景引用。基线要求交互次数至少为 1，超过 10 时警告，并检查物品引用、Batch 目标 ID 及 `VerticalSlice_01.unity` 中受支持组件的引用。

CLI、GUI 和 Batch 共用校验核心及结构化 `ValidationIssue`。CSV 解析完整性和 Unity 类型转换始终受检查。内容错误阻止生成和批量写入，警告允许继续；校验失败时保留原输出。单个文件采用原子替换；多个 JSON 写入发生 I/O 错误时会尝试回滚，但没有跨文件的断电事务保障。

### 规则编辑与批量更新

GUI 支持新增、编辑、复制、启用/停用和删除规则。修改先保存在草稿中，点击 **保存规则** 才写入规则文件；校验、生成和 Batch 可直接使用未保存的草稿。例如，把次数下限从 1 改为 4，当前 5 个交互物都会报错；恢复为 1 后通过。

Batch 用于批量修改 `requiredInteractions`：

```text
检查更新表 → 在内存中应用修改 → 校验全部修改后数据
→ 预览，或原子写入 interactables.csv → 生成 JSON
```

因此，调整同一条 Interactable 下限规则，就会同时影响普通校验、生成和 Batch Apply。预览不改源文件；应用会修改 CSV，之后需单独生成 JSON。

### AI 规则提案

OpenAI 和 DeepSeek 可将自然语言需求转换为新增、更新或停用规则的 RulePatch：

```text
需求 + 表头 + 支持的规则类型 + 当前规则
→ 检查提案结构 → 预览 → 应用到草稿 → 本地校验 → 按需保存规则
```

内容是否合格由 Python 引擎判断。AI 不接收 CSV 数据行，流程中也没有执行生成代码或直接写文件的步骤。非法或过期提案会被拒绝。没有 AI 密钥或 SDK 时，GUI、规则编辑、校验、生成和 Batch 均可使用；Fake Provider 提供离线演示。

在 GUI 中输入遮蔽显示的 API 密钥即可供本次使用。需要保留时，勾选 **在此电脑记住密钥** 并应用设置，Windows 凭据管理器会分别保存 OpenAI 和 DeepSeek 的密钥。密钥不写入项目文件；环境变量保留为兼容方式，**忘记密钥** 可移除本工具保存的凭据。

### CLI 与测试

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py rules-check
py Tools/config_tool.py validate
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
py -m unittest discover -s Tools/tests
```

无子命令的 `py Tools/config_tool.py` 仍执行生成。CLI 可通过 `--root`、`--source-dir`、`--output-dir`、`--rules` 指定路径。测试使用临时项目副本和模拟 AI 响应；Tk 测试需要桌面环境，Windows 凭据真实存取测试需显式启用。

## QA 与测量结果

可复用样例位于 `QA/Fixtures/scale_valid/`：

| 文件 | 内容 |
| --- | --- |
| items.csv | 8 条记录 |
| objectives.csv | 12 条记录 |
| interactables.csv | 20 条记录 |
| batch_interaction_updates.csv | 对上述记录的 8 条更新 |

Day 11 使用这 40 条内容记录，覆盖缺列、缺值、重复 ID、类型/范围/枚举错误、物品与场景引用失效、空文件、异常 CSV 和失败时保留输出。期间修复了场景引用覆盖缺口（`97b24be`）和异常 CSV 静默截断（`bb088b3`）；失败生成前后不变的 SHA256 验证了输出保留行为。V3 继续使用该样例，并增加规则配置、草稿、GUI、AI 服务、凭据和 EXE 项目定位测试。

Day 11 后续基准对比了相同的 8 条修改，两种输出均通过独立校验。

## 范围与文档

工具采用独立 GUI 和标准库测试。Unity Editor 集成、CSV 内容编辑器、依赖可视化、通用任务图、环路/不可达目标检查及全场景/全 prefab 扫描均未纳入范围。校验缺陷根据 QA 复现结果修复；V3 根据从业者对工具使用和规则调整的反馈扩展。

AI/Codex 参与实现与调试。仓库历史、可复现测试、实测数据和可玩版本人工检查构成项目证据。

| 文档 | 内容 |
| --- | --- |
| [案例说明](Docs/Pipeline_Case_Study.zh-CN.md) / [English](Docs/Pipeline_Case_Study.md) | 到 V3 的设计演进、QA 发现、历史基准和取舍 |
| [Day 11 QA](Docs/D11_QA.zh-CN.md) / [English](Docs/D11_QA.md) | 2026-09-11 的测试、日志、哈希与修复 |
| [使用说明](Docs/使用说明.md) | GUI、规则、Batch、EXE 和 AI 配置 |
| [技术实现](Docs/技术实现.md) | 当前模块、数据流程、存储和 AI 接口 |
| [Pipeline V1](Docs/Pipeline_V1.zh-CN.md) / [English](Docs/Pipeline_V1.md) | Week 1 单表架构及 Day 6 验证 |

仓库包含完整 Unity/Python 源码、可复用样例、中英文案例与 QA 记录，以及经过测试的 v1.0.0 可玩版本下载入口。
