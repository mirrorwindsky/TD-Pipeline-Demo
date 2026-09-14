"""Standalone tkinter/ttk front end; calls shared Python services directly."""
from copy import deepcopy
import json
import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from pipeline_model import TABLE_HEADERS
from ai_credentials import CredentialError, KeySettings, PROVIDERS, checked_key
from rule_authoring import (DEEPSEEK_DEFAULT_MODEL, DeepSeekProvider, FakeProvider,
                            OpenAIProvider, RuleDraft, author_rules)
from gui_i18n import CodeChoice, LocalizedVar, Translator
from rule_engine import RULE_TYPES, RuleConfigError, strict_json


def put_text(widget, value):
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", value)
    widget.configure(state="disabled")


def tree_panel(parent, columns, widths):
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
    for name, width in zip(columns, widths):
        tree.heading(name, text=name)
        tree.column(name, width=width, minwidth=50)
    vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.pack(fill="both", expand=True)
    return tree


class RuleEditor(tk.Toplevel):
    def __init__(self, app, rule=None):
        super().__init__(app.root)
        self.app = app
        self.target = rule["id"] if rule else None
        self.title(app.ui.text("Edit draft rule" if rule else "Add draft rule"))
        self.resizable(True, False)
        self.transient(app.root)
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        rule = deepcopy(rule) if rule else {
            "id": "new_rule", "type": "range", "table": "interactables",
            "field": "requiredInteractions", "level": "ERROR", "enabled": True,
            "params": {"minimum": 1},
        }
        self.values = {}
        options = {"type": list(RULE_TYPES), "table": list(TABLE_HEADERS),
                   "level": ["ERROR", "WARNING"]}
        for row, name in enumerate(("id", "type", "table", "field", "level", "description")):
            ttk.Label(frame, text=name).grid(row=row, column=0, sticky="w", padx=(0, 14), pady=4)
            variable = tk.StringVar(value=rule.get(name, ""))
            self.values[name] = variable
            if name in options or name == "field":
                widget = (ttk.Combobox(frame, textvariable=variable, state="readonly", width=50,
                                       values=TABLE_HEADERS[rule["table"]]) if name == "field" else
                          CodeChoice(frame, app.ui, variable, options[name], width=50))
                if name == "field":
                    self.field_widget = widget
            else:
                widget = ttk.Entry(frame, textvariable=variable, width=50)
            widget.grid(row=row, column=1, sticky="ew", pady=4)
            if name == "type":
                widget.bind("<<ComboboxSelected>>", lambda event: self.build_params(), add=True)
            elif name == "table":
                widget.bind("<<ComboboxSelected>>", lambda event: self.refresh_fields(), add=True)
        self.enabled = tk.BooleanVar(value=rule["enabled"])
        ttk.Checkbutton(frame, text="Enabled", variable=self.enabled).grid(row=6, column=1, sticky="w")
        self.params_frame = ttk.LabelFrame(frame, text="Rule parameters", padding=10)
        self.params_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        self.build_params(rule["params"])
        self.error = LocalizedVar(app.ui, self)
        ttk.Label(frame, textvariable=self.error, foreground="#b42318", wraplength=540).grid(
            row=8, column=0, columnspan=2, sticky="w")
        buttons = ttk.Frame(frame)
        buttons.grid(row=9, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=4)
        ttk.Button(buttons, text="Apply to Draft", command=self.commit).pack(side="left", padx=4)
        frame.columnconfigure(1, weight=1)
        self.bind("<Escape>", lambda event: self.destroy())
        app.ui.widgets(self)
        self.update_idletasks()
        x = max(0, app.root.winfo_rootx() + (app.root.winfo_width() - self.winfo_reqwidth()) // 2)
        y = max(0, app.root.winfo_rooty() + (app.root.winfo_height() - self.winfo_reqheight()) // 2)
        self.geometry(f"+{x}+{y}")
        self.grab_set()
        self.focus_set()

    def refresh_fields(self):
        fields = TABLE_HEADERS[self.values["table"].get()]
        if self.values["type"].get() in {"columns", "required"}:
            fields = [""]
        self.field_widget.configure(values=fields)
        if self.values["field"].get() not in fields:
            self.values["field"].set(fields[0])

    def build_params(self, current=None):
        for child in self.params_frame.winfo_children():
            child.destroy()
        kind = self.values["type"].get()
        sample = RULE_TYPES[kind]
        current = sample if current is None else current
        self.parameters = {}
        for row, (key, example) in enumerate(sample.items()):
            label = key + (" (one per line)" if isinstance(example, list) else "")
            if key in {"minimum", "maximum"}:
                label += " (blank = no bound)"
            ttk.Label(self.params_frame, text=label).grid(row=row, column=0, sticky="nw", pady=4, padx=(0, 10))
            value = current.get(key, False if isinstance(example, bool) else "")
            if isinstance(example, bool):
                var = tk.BooleanVar(value=value)
                widget = ttk.Checkbutton(self.params_frame, variable=var)
            elif isinstance(example, list):
                var = tk.Text(self.params_frame, height=3, width=40, wrap="none")
                var.insert("1.0", "\n".join(value))
                widget = var
            else:
                var = tk.StringVar(value=value)
                values = None
                if key == "value_type":
                    values = ["integer", "boolean", "string"]
                elif key == "target_table":
                    values = list(TABLE_HEADERS)
                widget = (CodeChoice(self.params_frame, self.app.ui, var, values)
                          if values else ttk.Entry(self.params_frame, textvariable=var, width=40))
            widget.grid(row=row, column=1, sticky="ew", pady=4)
            self.parameters[key] = (var, example)
        self.params_frame.columnconfigure(1, weight=1)
        self.refresh_fields()
        self.app.ui.widgets(self.params_frame)

    def commit(self):
        try:
            params = {}
            for key, (var, example) in self.parameters.items():
                if isinstance(example, list):
                    params[key] = [line.strip() for line in var.get("1.0", "end").splitlines() if line.strip()]
                elif isinstance(example, bool):
                    params[key] = var.get()
                elif key in {"minimum", "maximum"}:
                    if var.get().strip():
                        params[key] = strict_json(var.get().strip())
                else:
                    params[key] = var.get().strip()
            rule = {name: variable.get().strip() for name, variable in self.values.items()}
            rule.update(params=params, enabled=self.enabled.get())
            self.app.draft.put_rule(rule, self.target)
        except (RuleConfigError, ValueError) as exc:
            self.error.set(str(exc))
            return
        self.app.refresh_rules(rule["id"])
        self.destroy()


class ConfigApp:
    def __init__(self, root, pipeline, language="zh", credential_store=None):
        self.root, self.pipeline = root, pipeline
        self.ui = Translator(language)
        self.key_settings = KeySettings(credential_store)
        self.draft = RuleDraft(pipeline.rules_path)
        self.proposal = None
        self.ai_queue = queue.Queue()
        self.last_result = None
        root.title(self.ui.text("TD Content Pipeline V3"))
        root.geometry("1160x780")
        root.minsize(900, 650)
        root.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        title_bar = ttk.Frame(frame)
        title_bar.pack(fill="x")
        ttk.Label(title_bar, text="TD Content Pipeline", font=("Segoe UI", 20, "bold")).pack(side="left")
        self.language = tk.StringVar(root, value="中文" if language == "zh" else "English")
        language_box = ttk.Combobox(title_bar, textvariable=self.language, values=["中文", "English"],
                                    state="readonly", width=12)
        language_box.pack(side="right")
        language_box.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(frame, text=f"Source: {pipeline.source_dir}").pack(anchor="w", pady=(4, 0))
        ttk.Label(frame, text=f"Rule file: {pipeline.rules_path}").pack(anchor="w")
        self.draft_status = LocalizedVar(self.ui, root)
        ttk.Label(frame, textvariable=self.draft_status, foreground="#175cd3").pack(anchor="w", pady=(4, 10))
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 12))
        self.buttons = {}
        for label, command in (("Validate Draft", self.validate), ("Generate with Draft", self.generate),
                               ("Save Rules", self.save), ("Reload Rules", self.reload)):
            button = ttk.Button(toolbar, text=label, command=command)
            button.pack(side="left", padx=(0, 8))
            self.buttons[label] = button
        self.tabs = []
        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill="both", expand=True)
        validation = ttk.Frame(self.notebook, padding=10)
        rules = ttk.Frame(self.notebook, padding=10)
        batch = ttk.Frame(self.notebook, padding=10)
        ai = ttk.Frame(self.notebook, padding=10)
        for tab, label in ((validation, "Validation"), (rules, "Rules"), (batch, "Batch"), (ai, "AI Rule Authoring")):
            self.notebook.add(tab, text=label)
            self.tabs.append((tab, label))
        self.validation_tab = validation
        self.summary = LocalizedVar(self.ui, root, value="Validate to check current CSV content using the draft rules.")
        ttk.Label(validation, textvariable=self.summary).pack(anchor="w", pady=(0, 8))
        self.issue_tree = tree_panel(validation, ("Level", "Rule", "Table", "Row", "Field", "Message"),
                                     (80, 170, 100, 50, 130, 480))
        self.issue_tree.tag_configure("ERROR", foreground="#b42318")
        self.issue_tree.tag_configure("WARNING", foreground="#946200")
        self.issue_detail = ScrolledText(validation, height=4, wrap="word", state="disabled")
        self.issue_detail.pack(fill="x", pady=(6, 0))
        self.issue_tree.bind("<<TreeviewSelect>>", self.show_issue)
        rule_toolbar = ttk.Frame(rules)
        rule_toolbar.pack(fill="x", pady=(0, 8))
        for label, command in (("Add", lambda: RuleEditor(self)), ("Edit", self.edit_rule),
                               ("Duplicate", self.duplicate_rule), ("Enable / Disable", self.toggle_rule),
                               ("Delete", self.delete_rule)):
            ttk.Button(rule_toolbar, text=label, command=command).pack(side="left", padx=(0, 6))
        self.rule_tree = tree_panel(rules, ("ID", "Enabled", "Type", "Table", "Field", "Level", "Parameters"),
                                    (215, 65, 110, 100, 130, 75, 350))
        self.rule_tree.bind("<Double-1>", lambda event: self.edit_rule())
        ttk.Label(rules, text="Edits affect the draft only. Use Save Rules to persist; Generate and Batch use the current draft.").pack(
            anchor="w", pady=(8, 0))
        batch_toolbar = ttk.Frame(batch)
        batch_toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(batch_toolbar, text="Batch Preview", command=self.batch_preview).pack(side="left", padx=(0, 8))
        ttk.Button(batch_toolbar, text="Batch Apply", command=self.batch_apply).pack(side="left")
        ttk.Label(batch, text="Reads batch_interaction_updates.csv. Apply rechecks all staged content and writes interactables.csv.",
                  wraplength=950).pack(anchor="w", pady=(0, 10))
        self.batch_summary = LocalizedVar(self.ui, root, value="Preview before applying.")
        ttk.Label(batch, textvariable=self.batch_summary).pack(anchor="w", pady=(0, 8))
        self.batch_tree = tree_panel(batch, ("ID", "Before", "After"), (300, 180, 180))
        ai_bar = ttk.Frame(ai)
        ai_bar.pack(fill="x")
        self.provider_name = tk.StringVar(root, value="OpenAI")
        self.provider_box = CodeChoice(ai_bar, self.ui, self.provider_name,
                                       ["OpenAI", "DeepSeek", "Fake demo: minimum = 4"], width=32)
        self.provider_box.pack(side="left", padx=(0, 8))
        ttk.Label(ai_bar, text="Model").pack(side="left", padx=(0, 5))
        self.provider_models = {"OpenAI": os.environ.get("OPENAI_MODEL", ""),
                                "DeepSeek": os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL,
                                "Fake demo: minimum = 4": ""}
        self.active_provider = None
        self.model = tk.StringVar(root, value=self.provider_models["OpenAI"])
        self.model_entry = ttk.Entry(ai_bar, textvariable=self.model, width=32)
        self.model_entry.pack(side="left")
        self.provider_box.bind("<<ComboboxSelected>>", self.change_provider, add=True)
        key_bar = ttk.Frame(ai)
        key_bar.pack(fill="x", pady=(8, 0))
        ttk.Label(key_bar, text="API Key").pack(side="left", padx=(0, 8))
        self.api_key = tk.StringVar(root)
        self.key_entry = ttk.Entry(key_bar, textvariable=self.api_key, show="*", width=40)
        self.key_entry.pack(side="left", padx=(0, 8))
        self.remember_key = tk.BooleanVar(root, value=False)
        self.remember_box = ttk.Checkbutton(key_bar, text="Remember key on this computer", variable=self.remember_key)
        self.remember_box.pack(side="left", padx=(0, 8))
        self.key_apply_button = ttk.Button(key_bar, text="Apply key settings", command=self.apply_key_settings)
        self.key_apply_button.pack(side="left", padx=(0, 8))
        self.key_forget_button = ttk.Button(key_bar, text="Forget key", command=self.forget_key)
        self.key_forget_button.pack(side="left")
        self.key_status = LocalizedVar(self.ui, root)
        ttk.Label(ai, textvariable=self.key_status, wraplength=1000).pack(anchor="w", pady=(4, 0))
        self.provider_hint = LocalizedVar(self.ui, root)
        ttk.Label(ai, textvariable=self.provider_hint, wraplength=1000).pack(anchor="w", pady=(8, 0))
        ttk.Label(ai, text="AI sends your request, headers and rules to the selected provider; CSV rows stay local.\n"
                  "Fake demo returns a fixed minimum = 4 proposal without a network request.", wraplength=1000).pack(anchor="w", pady=8)
        self.request_text = ScrolledText(ai, height=3, wrap="word")
        self.request_text.pack(fill="x")
        self.request_text.insert("1.0", self.ui.text("Set the minimum requiredInteractions to 4."))
        ai_actions = ttk.Frame(ai)
        ai_actions.pack(fill="x", pady=8)
        self.propose_button = ttk.Button(ai_actions, text="Generate Proposal", command=self.start_proposal)
        self.propose_button.pack(side="left", padx=(0, 8))
        self.apply_button = ttk.Button(ai_actions, text="Apply to Draft", command=self.apply_proposal, state="disabled")
        self.apply_button.pack(side="left")
        self.ai_status = LocalizedVar(self.ui, root, value="Proposals require review and explicit Apply to Draft. Saving is a separate action.")
        ttk.Label(ai, textvariable=self.ai_status, wraplength=1000).pack(anchor="w", pady=(0, 8))
        self.proposal_text = ScrolledText(ai, height=10, wrap="word", state="disabled")
        self.proposal_text.pack(fill="both", expand=True)
        self.change_provider()
        self.refresh_rules()
        self.apply_language()
        self.poll_id = root.after(100, self.poll_ai)

    def change_language(self, event=None):
        self.ui.language = "zh" if self.language.get() == "中文" else "en"
        self.apply_language()

    def apply_language(self):
        self.ui.refresh(self.root)
        self.root.title(self.ui.text("TD Content Pipeline V3"))
        for tab, label in self.tabs:
            self.notebook.tab(tab, text=self.ui.text(label))
        selected = self.rule_tree.selection()
        self.render_rules(selected[0] if selected else None)
        self.render_issues()
        self.render_proposal()

    def change_provider(self, event=None):
        if self.active_provider is not None:
            self.provider_models[self.active_provider] = self.model.get()
            self.key_settings.edit(self.active_provider, self.api_key.get(), self.remember_key.get())
        self.active_provider = self.provider_name.get()
        self.model.set(self.provider_models.get(self.active_provider, ""))
        offline = self.active_provider.startswith("Fake")
        self.model_entry.configure(state="disabled" if offline else "normal")
        for widget in (self.key_entry, self.key_apply_button, self.key_forget_button):
            widget.configure(state="disabled" if offline else "normal")
        self.remember_box.configure(state="disabled" if offline or not self.key_settings.store.available else "normal")
        try:
            profile = self.key_settings.get(self.active_provider)
            self.api_key.set(profile.key)
            self.remember_key.set(profile.remember)
            self.key_status.set("Remembering changes only takes effect after Apply key settings." if profile.remember else
                                "Key stays in this session. To remember it, select the checkbox and apply key settings.")
        except CredentialError as exc:
            self.api_key.set("")
            self.remember_key.set(False)
            self.key_status.set(str(exc))
        prefix = "DEEPSEEK" if self.active_provider == "DeepSeek" else "OPENAI"
        self.provider_hint.set("Offline demo: no API key or model is needed." if offline else
            f"{self.active_provider}: enter API Key above. A blank key uses {prefix}_API_KEY if available.")

    def apply_key_settings(self):
        provider = self.provider_name.get()
        if provider not in PROVIDERS:
            return
        try:
            self.key_settings.apply(provider, self.api_key.get(), self.remember_key.get())
            self.api_key.set(self.key_settings.get(provider).key)
            self.key_status.set("Key saved in Windows Credential Manager." if self.remember_key.get() else
                                "Session key applied; any previously remembered key was removed.")
        except CredentialError as exc:
            self.key_status.set(str(exc))

    def forget_key(self):
        provider = self.provider_name.get()
        if provider not in PROVIDERS:
            return
        try:
            self.key_settings.forget(provider)
            self.api_key.set("")
            self.remember_key.set(False)
            self.key_status.set("Key removed from this tool. Environment variables, if set, remain available.")
        except CredentialError as exc:
            self.key_status.set(str(exc))

    def render_rules(self, selected=None):
        self.rule_tree.delete(*self.rule_tree.get_children())
        for rule in self.draft.config["rules"]:
            kind = rule["type"]
            if self.ui.language == "zh":
                kind = self.ui.text("type_rule" if kind == "type" else kind)
            self.rule_tree.insert("", "end", iid=rule["id"], values=(rule["id"], self.ui.text(str(rule["enabled"])), kind,
                rule["table"], rule["field"], self.ui.text(rule["level"]), json.dumps(rule["params"], ensure_ascii=False)))
        if selected and self.rule_tree.exists(selected):
            self.rule_tree.selection_set(selected)
            self.rule_tree.see(selected)

    def refresh_rules(self, selected=None):
        self.render_rules(selected)
        self.draft_status.set("Draft: UNSAVED CHANGES" if self.draft.dirty else "Draft: matches saved rule file")
        if self.last_result is not None:
            self.summary.set("Rules changed or reloaded. Validate again to refresh results.")
            self.batch_summary.set("Rules changed or reloaded. Preview again before applying.")
        if self.proposal and self.proposal.base != self.draft.config:
            self.apply_button.configure(state="disabled")
            self.ai_status.set("Draft changed. Generate a new proposal before applying.")

    def selected_rule(self):
        selection = self.rule_tree.selection()
        return next((r for r in self.draft.config["rules"] if selection and r["id"] == selection[0]), None)

    def edit_rule(self):
        rule = self.selected_rule()
        if rule:
            RuleEditor(self, rule)

    def duplicate_rule(self):
        rule = self.selected_rule()
        if rule:
            self.refresh_rules(self.draft.duplicate(rule["id"]))

    def toggle_rule(self):
        rule = self.selected_rule()
        if rule:
            self.draft.toggle(rule["id"])
            self.refresh_rules(rule["id"])

    def delete_rule(self):
        rule = self.selected_rule()
        if rule and self.dialog("askyesno", "Delete draft rule", f"Delete {rule['id']} from the draft?"):
            self.draft.delete(rule["id"])
            self.refresh_rules()

    def dialog(self, kind, title, message):
        return getattr(messagebox, kind)(self.ui.text(title), self.ui.text(message), parent=self.root)

    def render_issues(self):
        selected = self.issue_tree.selection()
        self.issue_tree.delete(*self.issue_tree.get_children())
        put_text(self.issue_detail, "")
        if self.last_result is None:
            return
        for index, issue in enumerate(self.last_result.issues):
            self.issue_tree.insert("", "end", iid=str(index), values=(self.ui.text(issue.level), issue.rule_id, issue.table,
                issue.row or "", issue.field, self.ui.text(issue.message)), tags=(issue.level,))
        if selected and self.issue_tree.exists(selected[0]):
            self.issue_tree.selection_set(selected[0])
            self.show_issue()

    def show_result(self, result, operation, select=True):
        self.last_result = result
        self.render_issues()
        errors = sum(i.level == "ERROR" for i in result.issues)
        warnings = sum(i.level == "WARNING" for i in result.issues)
        written = " | Written: " + ", ".join(str(p) for p in result.written) if result.written else ""
        self.summary.set(f"{operation}: {'PASS' if result.ok else 'FAILED'} | {errors} errors, {warnings} warnings{written}")
        if select:
            self.notebook.select(self.validation_tab)
        return result

    def show_issue(self, event=None):
        selected = self.issue_tree.selection()
        if selected and self.last_result:
            issue = self.last_result.issues[int(selected[0])]
            put_text(self.issue_detail, self.ui.text(f"{issue.level} / {issue.rule_id}\n{issue.table} row {issue.row or '-'} "
                     f"field {issue.field or '-'}\n{issue.message}"))

    def validate(self):
        return self.show_result(self.pipeline.validate(self.draft.config), "Validate Draft")

    def generate(self):
        return self.show_result(self.pipeline.generate(self.draft.config), "Generate with Draft")

    def save(self):
        try:
            self.draft.save()
            self.refresh_rules()
            return True
        except (OSError, ValueError) as exc:
            self.dialog("showerror", "Rules were not saved", str(exc))
            return False

    def reload(self):
        if self.draft.dirty and not self.dialog("askyesno", "Discard draft", "Discard unsaved rule edits and reload?"):
            return
        try:
            self.draft.reload()
            self.refresh_rules()
        except (OSError, ValueError) as exc:
            self.dialog("showerror", "Cannot reload rules", str(exc))

    def batch_preview(self):
        return self.run_batch(False)

    def batch_apply(self):
        if self.dialog("askyesno", "Apply batch", "Validate the current batch using draft rules and write interactables.csv?"):
            return self.run_batch(True)

    def run_batch(self, apply):
        result = self.pipeline.batch(self.draft.config, apply=apply)
        self.batch_tree.delete(*self.batch_tree.get_children())
        for update in result.updates:
            self.batch_tree.insert("", "end", values=(update.id, update.oldRequiredInteractions, update.newRequiredInteractions))
        self.show_result(result, "Batch Apply" if apply else "Batch Preview", select=not result.ok)
        self.batch_summary.set(f"{'PASS' if result.ok else 'FAILED'}: {len(result.updates)} staged updates. "
                               + ("Source written." if result.written else "No source files changed."))
        return result

    def start_proposal(self, provider=None):
        request = self.request_text.get("1.0", "end").strip()
        rules = self.draft.config
        if provider is None:
            if self.provider_name.get().startswith("Fake"):
                rule = next((r for r in rules["rules"] if r["id"] == "interactables.minimum"), None)
                if rule is None:
                    self.ai_status.set("Fake demo requires the baseline interactables.minimum rule.")
                    return
                rule = deepcopy(rule)
                rule["params"] = {"minimum": 4}
                provider = FakeProvider(json.dumps({"operations": [{"op": "update", "rule": rule}]}))
            else:
                try:
                    key = checked_key(self.api_key.get()) or None
                except CredentialError as exc:
                    self.ai_status.set(str(exc))
                    return
                provider_type = DeepSeekProvider if self.provider_name.get() == "DeepSeek" else OpenAIProvider
                provider = provider_type(self.model.get(), api_key=key)
        headers = self.pipeline.headers()
        self.proposal = None
        self.apply_button.configure(state="disabled")
        self.propose_button.configure(state="disabled")
        put_text(self.proposal_text, "")
        self.ai_status.set("Generating proposal… Draft and saved rules remain unchanged.")
        output_queue = self.ai_queue

        def worker():
            try:
                output_queue.put((author_rules(provider, request, headers, rules), None))
            except Exception as exc:
                output_queue.put((None, str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def poll_ai(self):
        try:
            proposal, error = self.ai_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            self.propose_button.configure(state="normal")
            if error:
                self.ai_status.set("Proposal rejected: " + error)
            else:
                self.accept_proposal(proposal)
        self.poll_id = self.root.after(100, self.poll_ai)

    def accept_proposal(self, proposal):
        self.proposal = proposal
        self.render_proposal()
        current = proposal.base == self.draft.config
        self.apply_button.configure(state="normal" if current else "disabled")
        self.ai_status.set("Proposal checked. Review the patch and diff, then Apply to Draft."
                           if current else "Draft changed during request. Generate a new proposal.")

    def render_proposal(self):
        if self.proposal is not None:
            diff = self.proposal.preview(self.ui.text("Current draft"), self.ui.text("Proposed draft"))
            put_text(self.proposal_text, json.dumps(self.proposal.patch, indent=2, ensure_ascii=False) + "\n\n" + diff)

    def apply_proposal(self):
        if self.proposal is None:
            return
        try:
            self.draft.apply(self.proposal)
        except RuleConfigError as exc:
            self.ai_status.set(str(exc))
            self.apply_button.configure(state="disabled")
            return
        self.refresh_rules()
        result = self.validate()
        self.apply_button.configure(state="disabled")
        self.ai_status.set(f"Applied to draft only. Content validation: {'PASS' if result.ok else 'FAILED'}. "
                           "Review Validation results. Save Rules remains a separate action.")
        return result

    def close(self):
        if self.draft.dirty:
            choice = self.dialog("askyesnocancel", "Unsaved rules", "Save rule edits before closing?")
            if choice is None or (choice and not self.save()):
                return
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def launch(pipeline):
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError(f"tkinter needs a desktop display: {exc}") from exc
    try:
        ConfigApp(root, pipeline)
        root.mainloop()
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    from pipeline_core import Pipeline
    launch(Pipeline())
