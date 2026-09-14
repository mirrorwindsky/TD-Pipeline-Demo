"""Real Tk widget/event smoke tests; all writes target temporary project copies."""
import gc
import io
import json
import threading
import time
import unittest
from unittest.mock import patch

from test_pipeline import ProjectCase
from test_credentials import MemoryStore
from rule_authoring import FakeProvider

try:
    import tkinter as tk
    from config_gui import ConfigApp, RuleEditor
except ImportError:
    tk = None


@unittest.skipIf(tk is None, "tkinter is not installed")
class GuiTests(ProjectCase):
    def setUp(self):
        super().setUp()
        try:
            self.window = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"No desktop display: {exc}")
        self.window.withdraw()
        self.credential_store = MemoryStore()
        self.app = ConfigApp(self.window, self.pipeline, credential_store=self.credential_store)
        self.addCleanup(self.destroy_window)
        self.window.update()

    def destroy_window(self):
        try:
            self.window.after_cancel(self.app.poll_id)
            self.window.destroy()
        except tk.TclError:
            pass
        self.app = None
        self.window = None
        # Collect destroyed Tk object cycles on their owning thread, before another test starts a worker.
        gc.collect()

    def edit_minimum(self, minimum):
        self.app.rule_tree.selection_set("interactables.minimum")
        editor = RuleEditor(self.app, self.app.selected_rule())
        self.window.update()
        editor.parameters["minimum"][0].set(str(minimum))
        editor.commit()
        self.window.update()

    def test_draft_demo_through_real_editor_and_buttons(self):
        disk = self.pipeline.rules_path.read_bytes()
        self.app.buttons["Validate Draft"].invoke()
        self.assertTrue(self.app.last_result.ok)
        self.edit_minimum(4)
        self.app.buttons["Validate Draft"].invoke()
        self.assertFalse(self.app.last_result.ok)
        self.assertEqual(len(self.app.issue_tree.get_children()), 5)
        self.assertTrue(self.app.draft.dirty)
        self.assertIn("未保存", self.app.draft_status.get())
        self.assertEqual(disk, self.pipeline.rules_path.read_bytes())
        self.edit_minimum(1)
        self.app.buttons["Validate Draft"].invoke()
        self.assertTrue(self.app.last_result.ok)
        self.app.buttons["Generate with Draft"].invoke()
        self.assertTrue(self.app.last_result.ok)
        self.assertEqual(disk, self.pipeline.rules_path.read_bytes())

    def test_gui_crud_save_reload(self):
        self.app.rule_tree.selection_set("interactables.minimum")
        self.app.duplicate_rule()
        copied = self.app.selected_rule()["id"]
        self.app.toggle_rule()
        self.assertFalse(self.app.selected_rule()["enabled"])
        with patch("config_gui.messagebox.askyesno", return_value=True):
            self.app.delete_rule()
        self.assertNotIn(copied, self.app.rule_tree.get_children())
        self.edit_minimum(4)
        self.assertTrue(self.app.save())
        self.assertFalse(self.app.draft.dirty)
        self.edit_minimum(1)
        with patch("config_gui.messagebox.askyesno", return_value=True):
            self.app.reload()
        self.assertFalse(self.app.draft.dirty)
        self.assertFalse(self.app.validate().ok)

    def test_editor_add_and_invalid_rule(self):
        editor = RuleEditor(self.app)
        editor.values["id"].set("custom.minimum")
        editor.parameters["minimum"][0].set("bad number")
        editor.commit()
        self.assertTrue(editor.error.get())
        self.assertNotIn("custom.minimum", self.app.rule_tree.get_children())
        editor.parameters["minimum"][0].set("1")
        editor.commit()
        self.assertIn("custom.minimum", self.app.rule_tree.get_children())

    def test_batch_buttons(self):
        self.assertTrue(self.app.batch_preview().ok)
        self.assertEqual(len(self.app.batch_tree.get_children()), 3)
        with patch("config_gui.messagebox.askyesno", return_value=True):
            self.assertTrue(self.app.batch_apply().ok)
        self.assertIn("已写入源 CSV", self.app.batch_summary.get())

    def wait_proposal(self):
        deadline = time.monotonic() + 3
        while self.app.propose_button.instate(["disabled"]) and time.monotonic() < deadline:
            self.window.update()
            time.sleep(0.01)
        self.assertFalse(self.app.propose_button.instate(["disabled"]))

    def test_fake_ai_async_preview_apply_validation(self):
        disk = self.pipeline.rules_path.read_bytes()
        self.app.provider_name.set("Fake demo: minimum = 4")
        self.app.propose_button.invoke()
        self.wait_proposal()
        self.assertIsNotNone(self.app.proposal)
        self.assertIn('"minimum": 4', self.app.proposal_text.get("1.0", "end"))
        self.assertFalse(self.app.draft.dirty)
        self.app.apply_button.invoke()
        self.assertTrue(self.app.draft.dirty)
        self.assertFalse(self.app.last_result.ok)
        self.assertEqual(disk, self.pipeline.rules_path.read_bytes())
        self.assertTrue(self.app.apply_button.instate(["disabled"]))

    def test_bad_ai_output_and_missing_key_leave_gui_usable(self):
        self.app.start_proposal(FakeProvider("malformed"))
        self.wait_proposal()
        self.assertIn("未通过检查", self.app.ai_status.get())
        self.assertFalse(self.app.draft.dirty)
        with patch.dict("os.environ", {}, clear=True):
            self.app.start_proposal()
            self.wait_proposal()
        self.assertIn("OPENAI_API_KEY", self.app.ai_status.get())
        self.assertTrue(self.app.validate().ok)
        self.assertTrue(self.app.generate().ok)
        self.assertTrue(self.app.batch_preview().ok)

    def test_default_chinese_and_switch_preserves_draft_results_and_request(self):
        self.assertEqual(self.window.title(), "TD 内容配置工具 V3")
        self.assertEqual(self.app.buttons["Validate Draft"].cget("text"), "校验草稿")
        self.edit_minimum(4)
        result = self.app.validate()
        before = self.app.draft.config
        request = self.app.request_text.get("1.0", "end")
        self.assertIn("超出范围", self.app.issue_tree.item("0", "values")[-1])
        self.assertIn("5 个错误", self.app.summary.get())
        self.app.language.set("English")
        self.app.change_language()
        self.assertEqual(self.app.buttons["Validate Draft"].cget("text"), "Validate Draft")
        self.assertIn("outside range", self.app.issue_tree.item("0", "values")[-1])
        self.assertIn("5 errors", self.app.summary.get())
        self.assertEqual(self.app.draft.config, before)
        self.assertIs(self.app.last_result, result)
        self.assertEqual(self.app.request_text.get("1.0", "end"), request)
        self.app.language.set("中文")
        self.app.change_language()
        self.assertIn("超出范围", self.app.issue_tree.item("0", "values")[-1])
        self.assertEqual(self.app.rule_tree.heading("Parameters", "text"), "参数")

    def test_chinese_rule_type_choice_persists_machine_identifiers(self):
        editor = RuleEditor(self.app)
        choice = next(child for child in editor.winfo_children()[0].winfo_children()
                      if hasattr(child, "variable") and child.variable is editor.values["type"])
        choice.current(choice.codes.index("regex"))
        choice.event_generate("<<ComboboxSelected>>")
        self.window.update()
        self.assertEqual(editor.values["type"].get(), "regex")
        self.assertEqual(choice.get(), "命名格式 (regex)")
        editor.values["id"].set("custom.naming")
        editor.values["field"].set("id")
        editor.parameters["pattern"][0].set("[")
        editor.commit()
        self.assertIn("正则表达式无效", editor.error.get())
        editor.parameters["pattern"][0].set("[a-z_]+")
        editor.commit()
        rule = next(r for r in self.app.draft.config["rules"] if r["id"] == "custom.naming")
        self.assertEqual((rule["type"], rule["field"]), ("regex", "id"))

    def choose_provider(self, code):
        self.app.provider_box.current(self.app.provider_box.codes.index(code))
        self.app.provider_box.event_generate("<<ComboboxSelected>>")
        self.window.update()

    def test_deepseek_gui_routing_and_model_choices(self):
        self.app.model.set("my-openai-model")
        self.choose_provider("DeepSeek")
        self.assertIn("DEEPSEEK_API_KEY", self.app.provider_hint.get())
        self.assertTrue(self.app.model.get())
        self.app.model.set("my-deepseek-model")
        rule = self.rule("interactables.minimum")
        rule["params"]["minimum"] = 4
        body = {"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"operations": [{"op": "update", "rule": rule}]})}}]}
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"}), \
                patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(body).encode())) as request:
            self.app.propose_button.invoke()
            self.wait_proposal()
        self.assertEqual(json.loads(request.call_args.args[0].data)["model"], "my-deepseek-model")
        self.assertIn("api.deepseek.com", request.call_args.args[0].full_url)
        self.assertFalse(self.app.draft.dirty)
        proposal = self.app.proposal
        self.app.language.set("English")
        self.app.change_language()
        self.assertIs(self.app.proposal, proposal)
        self.assertIn("Proposed draft", self.app.proposal_text.get("1.0", "end"))
        self.app.apply_button.invoke()
        self.assertTrue(self.app.draft.dirty)
        self.assertFalse(self.app.last_result.ok)
        self.choose_provider("OpenAI")
        self.assertEqual(self.app.model.get(), "my-openai-model")
        self.choose_provider("DeepSeek")
        self.assertEqual(self.app.model.get(), "my-deepseek-model")
        self.choose_provider("Fake demo: minimum = 4")
        self.assertTrue(self.app.model_entry.instate(["disabled"]))

    def test_language_switch_while_proposal_is_running(self):
        ready, release = threading.Event(), threading.Event()
        rule = self.rule("interactables.minimum")
        rule["params"]["minimum"] = 4

        class WaitingProvider:
            def propose(self, request, context):
                ready.set()
                release.wait(3)
                return json.dumps({"operations": [{"op": "update", "rule": rule}]})

        self.app.start_proposal(WaitingProvider())
        self.assertTrue(ready.wait(1))
        self.app.language.set("English")
        self.app.change_language()
        self.assertIn("Generating proposal", self.app.ai_status.get())
        self.assertTrue(self.app.propose_button.instate(["disabled"]))
        release.set()
        self.wait_proposal()
        self.assertIn("Proposal checked", self.app.ai_status.get())
        self.assertFalse(self.app.draft.dirty)

    def test_key_entry_session_persistence_and_forget(self):
        original = self.pipeline.rules_path.read_bytes()
        self.choose_provider("DeepSeek")
        self.assertEqual(self.app.key_entry.cget("show"), "*")
        self.assertFalse(self.app.remember_key.get())
        self.app.api_key.set("typed-deepseek-key")
        self.choose_provider("OpenAI")
        self.assertEqual(self.app.api_key.get(), "")
        self.app.api_key.set("typed-openai-key")
        self.choose_provider("DeepSeek")
        self.assertEqual(self.app.api_key.get(), "typed-deepseek-key")
        self.assertFalse(self.credential_store.writes)
        self.app.remember_key.set(True)
        self.choose_provider("OpenAI")
        self.choose_provider("DeepSeek")
        self.assertFalse(self.credential_store.writes)
        self.assertNotIn("已保存", self.app.key_status.get())
        self.app.key_apply_button.invoke()
        self.assertEqual(self.credential_store.read("DeepSeek"), "typed-deepseek-key")
        self.assertIn("凭据管理器", self.app.key_status.get())
        self.app.language.set("English")
        self.app.change_language()
        self.assertEqual(self.app.key_entry.cget("show"), "*")
        self.assertEqual(self.app.api_key.get(), "typed-deepseek-key")
        self.assertNotIn("typed-deepseek-key", self.app.key_status.get())
        self.app.key_forget_button.invoke()
        self.assertEqual(self.app.api_key.get(), "")
        self.assertIsNone(self.credential_store.read("DeepSeek"))
        self.assertEqual(original, self.pipeline.rules_path.read_bytes())

    def test_typed_key_used_without_save_and_without_environment(self):
        self.choose_provider("DeepSeek")
        self.app.api_key.set("session-request-key")
        body = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
            "operations": [{"op": "disable", "id": "interactables.minimum"}]})}}]}
        with patch.dict("os.environ", {}, clear=True), \
                patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(body).encode())) as request:
            self.app.propose_button.invoke()
            self.wait_proposal()
        self.assertIsNotNone(self.app.proposal)
        self.assertEqual(request.call_args.args[0].get_header("Authorization"), "Bearer session-request-key")
        self.assertFalse(self.credential_store.writes)
        self.assertNotIn("session-request-key", self.app.proposal_text.get("1.0", "end"))


if __name__ == "__main__":
    unittest.main()
