# Day 11 QA 与规模测试记录

[English](D11_QA.md) | 简体中文

> 历史测试记录：**2026-09-11，Pipeline V2**。下文输入、控制台输出、哈希和结果均属于当次测试。配置工具 V3 延续这些用例，实现和输出格式已有调整；见文末 V3 说明及[当前案例文档](Pipeline_Case_Study.zh-CN.md)。

## 目的与环境

Day 11 检查了更大输入集、坏数据处理，以及生成失败后保留合法输出的行为。期间建立了可复用的 40 条记录样例，完成规模生成和 8 项批量更新测试，并发现两项缺陷。两项缺陷均已复现、修复、回归，并合入 `main`。

替换源文件和注入异常数据的测试使用独立 Git worktree/branch，从 `4514da2`（`docs: close Day 10 and hand off to QA`）开始，场景为 `Assets/Scenes/VerticalSlice_01.unity`。主要命令：

```powershell
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

多数坏数据用例直接运行 Python，无需逐项打开 Unity。实现修改限定在已复现的缺陷内。

## 规模样例

保留的样例位于 `QA/Fixtures/scale_valid/`：

| 文件 | 记录数 |
| --- | --- |
| items.csv | 8 |
| objectives.csv | 12 |
| interactables.csv | 20 |
| **内容总数** | **40** |
| batch_interaction_updates.csv | 对现有记录的 8 条更新 |

样例用于检查超出最初几行数据后的单次解析、类型模型、校验、生成和批量行为，未提供商业项目规模的性能测量。

目标修改：

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

## 测试汇总

| ID | 测试 | 结果 |
| --- | --- | --- |
| QA-00 | D10 基线检查 | PASS |
| QA-01 | 40 条合法数据生成 | PASS |
| QA-02 | 8 条批量更新预览 | PASS |
| QA-03 | 8 条批量更新应用与重新生成 | PASS |
| QA-04 | 缺少必填值与输出保留 | PASS |
| QA-05 | 交互物 ID 重复 | PASS |
| QA-06 | 整数类型错误 | PASS |
| QA-07 | 数值范围错误 | PASS |
| QA-08 | 跨表物品引用失效 | PASS |
| QA-09 | 主场景 configId 引用失效 | FAIL → FIXED → PASS |
| QA-10 | 缺少必需列 | PASS |
| QA-11 | interactionType 非法 | PASS |
| QA-12 | 空 CSV | PASS |
| QA-13 | CSV 格式错误与多余列 | FAIL → FIXED → PASS |

## 规模与 Batch 结果

### QA-01 — 生成

输入为 8 个物品、12 个目标和 20 个交互物，当时输出：

```text
Validation: PASSED
Loaded 8 item configs.
Loaded 12 objective configs.
Loaded 20 interactable configs.
```

独立统计得到 20 个生成交互物和 12 个生成目标。8 个物品作为 Item-ID 引用表使用，不单独输出 `items.json`，与生成格式一致。

### QA-02 — 预览

8 条预期修改全部显示，结尾为：

```text
Validated 8 batch updates. No source files were changed.
```

直接比较文件后确认源内容没有变化。

### QA-03 — 应用与重新生成

应用后独立比较：

```text
baseline records: 20
actual records:   20
field changes:     8
```

仅目标 8 个 `requiredInteractions` 发生变化，其他源字段不变。重新生成以 8 / 12 / 20 条加载记录通过，JSON 中的 8 个目标值也通过独立检查。

## 坏数据结果

### QA-04 — 缺少必填值与输出保留

注入 `aux_power_box.requiredInteractions: 2 → 空值`，输出为：

```text
[ERROR] interactables.csv row 14 field 'requiredInteractions': value is required.
Validation failed. Generated JSON files were not updated.
```

失败生成前后，两份 SHA256 均未改变：

```text
interactables.json
9ACE14305F3CDE1910504A5DC582DD8F0ABFAF612577D1242BCBEF240BE7212F
→ unchanged

objectives.json
3FF580778CB730008198C0826CDDB240588604F7AED18246A9C8E3907AEBB60E
→ unchanged
```

### 其他被拦截的输入

| ID | 注入内容 | 当时的错误输出 |
| --- | --- | --- |
| QA-05 | `maintenance_panel → power_node` | `[ERROR] interactables.csv row 21 field 'id': duplicate id 'power_node'.` |
| QA-06 | `backup_generator.requiredInteractions: 5 → three` | `[ERROR] interactables.csv row 18 field 'requiredInteractions': expected integer, got 'three'.` |
| QA-07 | `sensor_array.requiredInteractions: 4 → 0` | `[ERROR] interactables.csv row 17 field 'requiredInteractions': must be >= 1, got 0.` |
| QA-08 | `coolant_pump.requiredItemId: coolant_canister → missing_coolant` | `[ERROR] interactables.csv row 15 field 'requiredItemId': unknown item id 'missing_coolant'.` |
| QA-10 | 删除 `objectives.csv` 的 `description` 列 | `[ERROR] objectives.csv: missing required column 'description'.` |
| QA-11 | `security_console.interactionType: Device → Terminal` | `[ERROR] interactables.csv row 16 field 'interactionType': unknown value 'Terminal'. Expected one of: Device, Pickup.` |
| QA-12 | 将 `items.csv` 清空为 0 字节 | `[ERROR] items.csv: CSV header is missing.` |

QA-12 返回错误时没有出现 Python traceback。QA-09 和 QA-13 需要修复，过程如下。

## QA-09 — 主场景引用覆盖缺口

场景保留以下引用：

```text
Assets/Scenes/VerticalSlice_01.unity
configId: control_terminal
```

只将源 ID 从 `control_terminal` 改为 `control_terminal_renamed`，生成最初错误通过。独立检查发现 JSON 已使用新 ID，场景仍引用旧 ID。

校验器仍使用 V1 范围：`SCENE_PATH → Prototype_01.unity`，且只识别 `ConfigurableInteractable.configId`。V2 场景还使用 `PickupInteractable` 和 `DeviceInteractable`。

提交 `97b24be`（`fix: validate active scene config references`）将目标改为 `VerticalSlice_01.unity`，覆盖以下三类配置驱动组件：

```text
ConfigurableInteractable
PickupInteractable
DeviceInteractable
```

相同坏数据随后得到：

```text
[ERROR] VerticalSlice_01.unity: DeviceInteractable references unknown config id 'control_terminal'.
```

恢复 40 条合法样例后，回归通过。**结果：FAIL → FIXED → PASS。**

## QA-13 — 异常 CSV 静默截断

在三列目标表中注入：

```csv
inspect_storage,Inspect Storage,Objective: Inspect storage, then return.
```

`csv.DictReader` 将多出的值放入 `None` 键。管线忽略该值，报告成功并生成缩短的目标描述，造成静默内容损坏。

提交 `bb088b3`（`fix: reject malformed CSV rows with extra columns`）在当时的 `validate_schema()` 中拒绝额外值。同一输入得到：

```text
[ERROR] objectives.csv row 7: unexpected extra column value(s) [' then return.']. Check for an unescaped comma or mismatched column count.
```

恢复 40 条合法样例后，回归通过。**结果：FAIL → FIXED → PASS。**

## 范围与调试

本轮 QA 未增加依赖环路检查、不可达目标检查、通用任务校验、全 prefab 扫描、依赖可视化、Unity Editor GUI 或大型测试框架，修改集中于两项已复现的问题。

AI/Codex 参与诊断与实现。两项缺陷均来自具体 QA 输入，并经过独立检查、小范围修复、回归和合入 `main`。

## 后续基准

同一套样例随后用于相同 8 项修改的受控对比：

| 测量项 | 记录值 |
| --- | --- |
| 人工执行 | 192.000 s |
| 自动执行 | 0.287 s |
| 执行提速 | 约 670 倍 |
| 执行用时减少 | 约 99.85% |

测量仅包含执行阶段，未计批量请求编写，且发生在 V3 之前。完整方法、精确计时与核对结果见[中文案例](Pipeline_Case_Study.zh-CN.md) / [English](Pipeline_Case_Study.md)。

## 在 V3 中复用这些用例

V3 提交 `22c992e` 将项目标准移入 `ConfigSource/validation_rules.json`，CLI、GUI 和 Batch 共用校验。场景规则延续上述三类组件，多余列拦截现由 `pipeline_core.parse_csv_table()` 执行；Batch 写入前检查全部修改后数据。

`Tools/tests/` 在临时项目副本中继续使用规模样例，并补充规则配置、草稿、GUI、AI 服务、凭据和项目定位测试：

```powershell
py -m unittest discover -s Tools/tests
```

AI HTTP 响应使用 mock。GUI 测试需要 tkinter 和桌面环境，Windows 凭据真实存取另有显式启用的测试。可通过这些测试回归当前工具，无需替换工作项目的 CSV。上面的历史日志和哈希保留为 2026-09-11 测试的证据。
