"""GUI-only translations. Rule identifiers, persisted data and CLI diagnostics stay stable."""
import re
import string
import tkinter as tk
from tkinter import ttk
from weakref import WeakKeyDictionary, WeakValueDictionary


ZH = {
    "TD Content Pipeline V3": "TD 内容配置工具 V3",
    "TD Content Pipeline": "TD 内容配置工具",
    "Source: {path}": "数据目录：{path}",
    "Rule file: {path}": "规则文件：{path}",
    "Validate Draft": "校验草稿",
    "Generate with Draft": "按草稿生成 JSON",
    "Save Rules": "保存规则",
    "Reload Rules": "重新加载规则",
    "Validation": "校验结果", "Rules": "规则", "Batch": "批量更新",
    "AI Rule Authoring": "AI 编写规则",
    "Level": "级别", "Rule": "规则", "Table": "数据表", "Row": "行号",
    "Field": "字段", "Message": "说明", "ID": "ID", "Enabled": "启用",
    "Type": "类型", "Parameters": "参数", "Before": "修改前", "After": "修改后",
    "Add": "新增", "Edit": "编辑", "Duplicate": "复制",
    "Enable / Disable": "启用 / 停用", "Delete": "删除",
    "Batch Preview": "预览批量更新", "Batch Apply": "应用批量更新",
    "Model": "模型", "Generate Proposal": "生成提案", "Apply to Draft": "应用到草稿",
    "API Key": "API 密钥",
    "Remember key on this computer": "在此电脑记住密钥",
    "Apply key settings": "应用密钥设置", "Forget key": "忘记密钥",
    "{provider}: enter API Key above. A blank key uses {key} if available.":
        "{provider}：在上方填写 API 密钥；留空时兼容使用 {key} 环境变量。",
    "Key stays in this session. To remember it, select the checkbox and apply key settings.":
        "默认仅本次使用。需要记住密钥时，勾选后点击“应用密钥设置”。",
    "Remembering changes only takes effect after Apply key settings.":
        "修改密钥或记住选项后，需点击“应用密钥设置”才会更新保存的内容。",
    "Key saved in Windows Credential Manager.": "密钥已保存到 Windows 凭据管理器。",
    "Session key applied; any previously remembered key was removed.": "密钥仅本次使用，之前记住的密钥已移除。",
    "Key removed from this tool. Environment variables, if set, remain available.":
        "已清除本工具中的密钥。如设置过环境变量，它仍可使用。",
    "Invalid API key: paste the key only, without spaces or line breaks": "密钥格式无效，请只粘贴密钥，去掉内部空格或换行。",
    "Unknown AI provider": "未知 AI 服务",
    "Remembering keys is supported on Windows only": "仅 Windows 支持记住密钥；仍可在本次运行中使用密钥。",
    "Windows Credential Manager is unavailable": "Windows 凭据管理器暂不可用；仍可输入密钥在本次运行中使用。",
    "Cannot read saved API key; you can enter a session key": "无法读取记住的密钥，可重新输入供本次使用。",
    "Saved API key is invalid; remove it and enter a new key": "记住的密钥无效，请先忘记密钥，再重新输入。",
    "Enter an API key before remembering it": "请先输入密钥，再选择记住。",
    "Cannot save API key; session use is still available": "密钥保存失败，仍可在本次运行中使用。",
    "Cannot remove saved API key": "无法移除记住的密钥，请稍后重试。",
    "Cancel": "取消", "Edit draft rule": "编辑草稿规则", "Add draft rule": "新增草稿规则",
    "id": "规则 ID", "type": "规则类型", "table": "数据表", "field": "字段",
    "level": "级别", "description": "说明", "Rule parameters": "规则参数",
    "minimum (blank = no bound)": "最小值（留空则不限）",
    "maximum (blank = no bound)": "最大值（留空则不限）",
    "allow_empty": "允许空值", "value_type": "数据类型",
    "fields (one per line)": "字段列表（每行一个）", "values (one per line)": "允许值（每行一个）",
    "components (one per line)": "组件标识（每行一个）", "pattern": "正则表达式",
    "target_table": "目标数据表", "target_field": "目标字段",
    "source_field": "场景引用字段", "scene": "场景文件路径",
    "columns": "必需列 (columns)", "required": "必填值 (required)",
    "type_rule": "数据类型 (type)", "range": "数值范围 (range)", "enum": "允许值 (enum)",
    "unique": "唯一值 (unique)", "regex": "命名格式 (regex)",
    "reference": "跨表引用 (reference)", "scene_reference": "场景引用 (scene_reference)",
    "integer": "整数 (integer)", "boolean": "布尔值 (boolean)", "string": "文本 (string)",
    "finite number": "有限数值",
    "ERROR": "错误", "WARNING": "警告", "True": "是", "False": "否",
    "PASS": "通过", "FAILED": "未通过",
    "Draft: UNSAVED CHANGES": "草稿：有未保存的修改",
    "Draft: matches saved rule file": "草稿：与已保存的规则一致",
    "Validate to check current CSV content using the draft rules.": "点击“校验草稿”，按当前规则检查 CSV 数据。",
    "Edits affect the draft only. Use Save Rules to persist; Generate and Batch use the current draft.":
        "编辑只修改草稿；点击“保存规则”才会写入规则文件。生成 JSON 和批量更新均使用当前草稿。",
    "Reads batch_interaction_updates.csv. Apply rechecks all staged content and writes interactables.csv.":
        "从 batch_interaction_updates.csv 读取更新。应用前会校验全部修改结果，通过后写入 interactables.csv。",
    "Preview before applying.": "请先预览，再应用更新。",
    "Rules changed or reloaded. Validate again to refresh results.": "规则已修改或重新加载，请重新校验。",
    "Rules changed or reloaded. Preview again before applying.": "规则已修改或重新加载，请重新预览批量更新。",
    "Draft changed. Generate a new proposal before applying.": "草稿已变化，请重新生成提案。",
    "Fake demo: minimum = 4": "离线演示：最小值改为 4",
    "AI sends your request, headers and rules to the selected provider; CSV rows stay local.\n"
    "Fake demo returns a fixed minimum = 4 proposal without a network request.":
        "AI 会将需求、表头和规则发送给所选服务；CSV 数据行保留在本地。\n离线演示会返回最小值为 4 的固定提案，无需联网。",
    "{provider}: set {key} in the environment. Model can be entered here or set with {model_env}.":
        "{provider}：在环境变量中设置 {key}；模型可在上方填写，也可通过 {model_env} 设置。",
    "Offline demo: no API key or model is needed.": "离线演示：无需 API 密钥或模型。",
    "Set the minimum requiredInteractions to 4.": "将 requiredInteractions 的最小值改为 4。",
    "Proposals require review and explicit Apply to Draft. Saving is a separate action.":
        "请先检查提案，再点击“应用到草稿”；需要保留规则时，另点“保存规则”。",
    "Generating proposal… Draft and saved rules remain unchanged.": "正在生成提案……草稿和已保存的规则保持原样。",
    "Proposal rejected: {detail}": "提案未通过检查：{detail}",
    "Proposal checked. Review the patch and diff, then Apply to Draft.": "提案已通过结构检查。请阅读修改内容和差异，再应用到草稿。",
    "Draft changed during request. Generate a new proposal.": "请求期间草稿已变化，请重新生成提案。",
    "Fake demo requires the baseline interactables.minimum rule.": "离线演示需要存在 interactables.minimum 规则。",
    "Applied to draft only. Content validation: {status}. Review Validation results. Save Rules remains a separate action.":
        "已应用到草稿。数据校验：{status}。请查看校验结果；规则尚未保存。",
    "Delete draft rule": "删除草稿规则", "Delete {rid} from the draft?": "从草稿中删除 {rid}？",
    "Rules were not saved": "规则未保存", "Cannot reload rules": "无法重新加载规则",
    "Discard draft": "放弃草稿修改", "Discard unsaved rule edits and reload?": "放弃未保存的规则修改，重新加载文件？",
    "Apply batch": "应用批量更新",
    "Validate the current batch using draft rules and write interactables.csv?":
        "按当前草稿校验批量更新，通过后写入 interactables.csv？",
    "Unsaved rules": "规则尚未保存", "Save rule edits before closing?": "关闭前保存规则修改吗？",
    "{operation}: {status} | {errors} errors, {warnings} warnings{written}":
        "{operation}：{status} | {errors} 个错误，{warnings} 个警告{written}",
    " | Written: {paths}": " | 已写入：{paths}",
    "{status}: {count} staged updates. {detail}": "{status}：共 {count} 条更新。{detail}",
    "Source written.": "已写入源 CSV。", "No source files changed.": "源文件未修改。",
    "{level} / {rid}\n{table} row {row} field {field}\n{detail}": "{level} / {rid}\n{table} 第 {row} 行，字段 {field}\n{detail}",
    "Current draft": "当前草稿", "Proposed draft": "提案草稿",
    # Localize structured issue.message for display only. Never derive validation decisions from text.
    "Value is required": "此处必须填写内容",
    "Missing column '{field}'": "缺少列：{field}",
    "Expected {kind}, got {value}": "需要{kind}，当前值为 {value}",
    "Value {value} outside range [{minimum}, {maximum}]": "数值 {value} 超出范围 [{minimum}, {maximum}]",
    "Expected one of {values}, got {value}": "允许值为 {values}，当前值为 {value}",
    "Duplicate value {value}": "值重复：{value}",
    "Value {value} does not match {pattern}": "值 {value} 不符合格式 {pattern}",
    "Unknown reference {value} to {target}": "在 {target} 中找不到引用值 {value}",
    "Reference target table/column is unavailable": "引用的目标表或列不存在",
    "Scene path escapes project root": "场景路径超出项目目录",
    "Cannot read scene {scene}: {detail}": "无法读取场景 {scene}：{detail}",
    "{scene}: {component} has missing/unknown {field}: {value}": "{scene}：{component} 的 {field} 为空或找不到对应配置：{value}",
    "{file}: CSV header is missing or empty": "{file}：缺少表头或表头为空",
    "{file}: duplicate CSV header": "{file}：表头列名重复",
    "{file} row {row}: unexpected extra column value(s)": "{file} 第 {row} 行：列数过多，请检查逗号和引号",
    "{file} row {row}: mismatched column count": "{file} 第 {row} 行：列数与表头不一致",
    "{file} row {row}: NUL byte in CSV": "{file} 第 {row} 行：包含无效的空字节",
    "{file}: cannot parse CSV: {detail}": "{file}：无法读取 CSV：{detail}",
    "Cannot convert to Unity JSON contract: {detail}": "无法转换为 Unity 所需的数据格式：{detail}",
    "Unity boolean must be true or false": "布尔值必须为 true 或 false",
    "Unity integer must fit Int32": "整数超出 Unity Int32 范围",
    "JSON write failed: {detail}": "JSON 写入失败：{detail}",
    "Batch write failed: {detail}": "批量更新写入失败：{detail}",
    "Cannot stage batch integer: {detail}": "无法读取批量更新中的整数：{detail}",
    "Batch target {value} is missing or ambiguous": "批量更新目标 {value} 不存在或对应多行",
    "Rule config must contain only version and rules": "规则配置只能包含 version 和 rules",
    "Unsupported RuleSpec version (expected 1)": "不支持此规则版本，version 应为 1",
    "rules must be an array": "rules 必须为列表", "Each rule must be an object": "每条规则必须为对象",
    "Rule keys must be id/type/table/field/params/level/enabled and optional description":
        "规则需包含 id、type、table、field、params、level、enabled，可另填 description",
    "Rule id must be a stable identifier": "规则 ID 需以英文字母开头，只能包含字母、数字、下划线、点和短横线",
    "Duplicate rule id: {rid}": "规则 ID 重复：{rid}",
    "{rid}: unknown rule type": "{rid}：不支持此规则类型",
    "{rid}: unknown table": "{rid}：数据表不存在", "{rid}: unknown field": "{rid}：字段不存在",
    "{rid}: unknown field {field}": "{rid}：字段 {field} 不存在",
    "{rid}: field must be a string": "{rid}：字段名必须为文本",
    "{rid}: level must be ERROR or WARNING": "{rid}：级别必须为 ERROR 或 WARNING",
    "{rid}: enabled must be boolean": "{rid}：启用状态必须为布尔值",
    "{rid}: description must be text": "{rid}：说明必须为文本",
    "{rid}: params must be an object": "{rid}：参数必须为对象",
    "{rid}: invalid params for {kind}": "{rid}：{kind} 的参数不正确",
    "{rid}: allow_empty must be boolean": "{rid}：允许空值必须为布尔值",
    "{rid}: columns/required use params.fields, field must be empty": "{rid}：请在字段列表中填写列名，单独的字段框需留空",
    "{rid}: fields must be a nonempty unique string array": "{rid}：字段列表不能为空，且不能包含重复项",
    "{rid}: value_type must be integer, boolean or string": "{rid}：数据类型应为 integer、boolean 或 string",
    "{rid}: range needs a bound": "{rid}：至少填写一个数值边界",
    "{rid}: {bound} must be a finite number": "{rid}：{bound} 必须是有限数值",
    "{rid}: reversed range": "{rid}：最小值不能大于最大值",
    "{rid}: values must be a nonempty unique string array": "{rid}：允许值列表不能为空，且不能包含重复项",
    "{rid}: pattern must be a string of at most 512 characters": "{rid}：正则表达式须为文本，最多 512 个字符",
    "{rid}: invalid regex: {detail}": "{rid}：正则表达式无效：{detail}",
    "{rid}: unknown reference table": "{rid}：引用的目标表不存在",
    "{rid}: unknown reference field": "{rid}：引用的目标字段不存在",
    "{rid}: content cannot depend on optional batch input": "{rid}：内容规则不能引用可选的批量更新表",
    "{rid}: scene must be a relative Unity path": "{rid}：请填写场景文件相对项目目录的路径",
    "{rid}: invalid scene path": "{rid}：场景路径无效",
    "{rid}: components must be a string array": "{rid}：组件列表不能为空，且不能包含重复项",
    "{rid}: invalid source_field": "{rid}：场景引用字段名无效",
    "{rid}: scene cannot reference batch": "{rid}：场景不能引用批量更新表",
    "Cannot read rules: {detail}": "无法读取规则：{detail}",
    "Duplicate JSON key: {key}": "JSON 键重复：{key}", "Invalid JSON number: {value}": "JSON 数值无效：{value}",
    "Invalid JSON: {detail}": "JSON 格式无效：{detail}",
    "RulePatch must contain a nonempty operations array": "提案需包含非空的 operations 列表",
    "Patch operation must be an object": "每项提案操作必须为对象",
    "Only add, update and disable operations are supported": "提案只支持新增、更新和停用规则",
    "{op} requires exactly {keys}": "{op} 操作只能使用这些字段：{keys}",
    "Every operation must target a distinct rule id": "每项操作需指定规则 ID，同一提案中不能重复操作同一 ID",
    "Rule id already exists: {rid}": "规则 ID 已存在：{rid}",
    "Update target does not exist: {rid}": "待更新的规则不存在：{rid}",
    "Rule does not exist: {rid}": "规则不存在：{rid}",
    "Draft changed since proposal creation; generate a new proposal": "生成提案后草稿发生了变化，请重新生成提案",
    "Proposal preview does not match patch": "提案预览与实际修改内容不一致",
    "Rule file changed outside this tool. Reload before saving": "规则文件已被其他程序修改，请重新加载后再保存",
    "Describe the rule you want to add or change": "请描述希望新增或修改的规则",
    "AI unavailable: set {key} in the environment": "请先在 API 密钥框中填写密钥（也兼容 {key} 环境变量）。",
    "Enter an {provider} model ID or set {env}": "请填写 {provider} 模型 ID，或设置 {env}",
    "Enter a {provider} model ID or set {env}": "请填写 {provider} 模型 ID，或设置 {env}",
    "AI request failed (HTTP {code}); check model/access/quota": "AI 请求失败（HTTP {code}），请检查模型、权限和额度",
    "AI connection failed ({kind}); try again": "AI 连接失败（{kind}），请稍后重试",
    "AI response was incomplete or refused; no proposal was applied": "AI 回复被截断或拒绝，本次未应用提案",
    "Malformed AI response envelope": "AI 回复结构不正确",
    "AI returned no rule proposal": "AI 未返回规则提案",
    "AI response is too large": "AI 回复过长",
    "Invalid AI request configuration": "AI 请求配置无效",
}


def _patterns():
    """Match display templates only; placeholders are escaped and never executed."""
    patterns = []
    for source, target in ZH.items():
        if "{" not in source:
            continue
        pieces = []
        for literal, name, _, _ in string.Formatter().parse(source):
            pieces.append(re.escape(literal))
            if name:
                pieces.append(f"(?P<{name}>.*?)")
        specificity = sum(len(literal) for literal, _, _, _ in string.Formatter().parse(source))
        patterns.append((specificity, re.compile("".join(pieces), re.DOTALL), target))
    return [(pattern, target) for _, pattern, target in sorted(patterns, key=lambda item: -item[0])]


PATTERNS = _patterns()


class LocalizedVar(tk.StringVar):
    def __init__(self, ui, master, value=""):
        self.ui, self.source = ui, value
        super().__init__(master, value=ui.text(value))
        ui.variables[id(self)] = self

    def set(self, value):
        self.source = str(value)
        super().set(self.ui.text(self.source))

    def refresh(self):
        super().set(self.ui.text(self.source))


class Translator:
    def __init__(self, language="zh"):
        self.language = language
        self.originals = WeakKeyDictionary()
        self.variables = WeakValueDictionary()
        self.choices = WeakValueDictionary()

    def text(self, value):
        if self.language == "en":
            return value
        if value in ZH:
            return ZH[value]
        for pattern, target in PATTERNS:
            match = pattern.fullmatch(value)
            if match:
                values = match.groupdict()
                for key in {"detail", "status", "level", "operation", "written", "kind"} & values.keys():
                    if values[key] != value:
                        values[key] = self.text(values[key])
                return target.format_map(values)
        # Keep unrecognized OS/parser details intact rather than losing useful diagnostics.
        return value

    def widgets(self, widget):
        if "text" in widget.keys() and ("textvariable" not in widget.keys() or not str(widget.cget("textvariable"))):
            self.originals.setdefault(widget, widget.cget("text"))
            widget.configure(text=self.text(self.originals[widget]))
        if isinstance(widget, ttk.Treeview):
            for column in widget.cget("columns"):
                widget.heading(column, text=self.text(column))
        for child in widget.winfo_children():
            self.widgets(child)

    def refresh(self, root):
        self.widgets(root)
        for variable in list(self.variables.values()):
            variable.refresh()
        for choice in list(self.choices.values()):
            if choice.winfo_exists():
                choice.refresh()


class CodeChoice(ttk.Combobox):
    """Translated options backed by unchanged rule/provider identifiers."""
    def __init__(self, parent, ui, variable, codes, **kwargs):
        self.ui, self.variable, self.codes = ui, variable, list(codes)
        self.display = tk.StringVar(parent)
        super().__init__(parent, textvariable=self.display, state="readonly", **kwargs)
        self.bind("<<ComboboxSelected>>", self.selected)
        self.trace_id = variable.trace_add("write", lambda *args: self.refresh())
        self.bind("<Destroy>", self.cleanup, add=True)
        ui.choices[id(self)] = self
        self.refresh()

    def label(self, code):
        return self.ui.text("type_rule" if code == "type" else code) if self.ui.language == "zh" else code

    def refresh(self):
        self.configure(values=[self.label(code) for code in self.codes])
        self.display.set(self.label(self.variable.get()))

    def selected(self, event=None):
        index = self.current()
        if index >= 0:
            self.variable.set(self.codes[index])

    def cleanup(self, event):
        if event.widget is self:
            self.variable.trace_remove("write", self.trace_id)
