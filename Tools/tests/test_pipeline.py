"""Isolated regression coverage for rule policies, publishing and authoring."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from pipeline_core import Pipeline, parse_csv_table
from rule_engine import RuleConfigError, check_config, load_config, strict_json
from rule_authoring import FakeProvider, OpenAIProvider, RuleDraft, author_rules, validate_patch


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "ConfigSource", self.root / "ConfigSource")
        shutil.copytree(ROOT / "Assets" / "Data", self.root / "Assets" / "Data")
        (self.root / "Assets" / "Scenes").mkdir()
        self.scene = self.root / "Assets" / "Scenes" / "VerticalSlice_01.unity"
        shutil.copy2(ROOT / "Assets" / "Scenes" / self.scene.name, self.scene)
        self.pipeline = Pipeline(self.root)
        self.rules = load_config(self.pipeline.rules_path)

    def rule(self, rid):
        return next(r for r in self.rules["rules"] if r["id"] == rid)

    def edit_csv(self, table, edit):
        name = "batch_interaction_updates" if table == "batch" else table
        path = self.pipeline.source_dir / (name + ".csv")
        data = parse_csv_table(path)
        edit(data.rows)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=data.fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(data.rows)

    def change(self, table, field, value, index=0):
        self.edit_csv(table, lambda rows: rows[index].__setitem__(field, value))

    def assert_issue(self, rid, result=None, level="ERROR"):
        result = result or self.pipeline.validate(self.rules)
        self.assertTrue(any(i.rule_id == rid and i.level == level for i in result.issues), result.issues)
        return result

    def outputs(self):
        return {p.name: p.read_bytes() for p in self.pipeline.output_dir.glob("*.json")}


class EngineTests(ProjectCase):
    def test_baseline_and_json_contract(self):
        before = self.outputs()
        result = self.pipeline.generate(self.rules)
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(before, self.outputs())
        self.assertEqual((len(result.content.items), len(result.content.objectives),
                          len(result.content.interactables)), (1, 5, 5))
        value = json.loads(before["interactables.json"])["interactables"][0]
        self.assertEqual(set(value), {"id", "displayName", "interactionType", "requiredInteractions",
            "requiredItemId", "grantedItemId", "blockedMessage", "completionMessage", "deactivateOnComplete"})
        self.assertIs(type(value["requiredInteractions"]), int)
        self.assertIs(type(value["deactivateOnComplete"]), bool)

    def test_required(self):
        self.change("items", "displayName", "  ")
        result = self.assert_issue("items.required")
        issue = next(i for i in result.issues if i.rule_id == "items.required")
        self.assertEqual((issue.table, issue.row, issue.field), ("items", 2, "displayName"))

    def test_columns(self):
        path = self.pipeline.source_dir / "items.csv"
        path.write_text("id\npower_cell\n", encoding="utf-8")
        self.assert_issue("items.columns")

    def test_integer_and_boolean(self):
        self.change("interactables", "requiredInteractions", "1.5")
        self.change("interactables", "deactivateOnComplete", "yes")
        result = self.pipeline.validate(self.rules)
        self.assert_issue("interactables.integer", result)
        self.assert_issue("interactables.boolean", result)

    def test_type_boolean_normalizes_case(self):
        self.change("interactables", "deactivateOnComplete", " FALSE ")
        result = self.pipeline.validate(self.rules)
        self.assertTrue(result.ok, result.issues)
        self.assertIs(result.content.interactables[0].deactivateOnComplete, False)

    def test_range_error_and_warning(self):
        self.change("interactables", "requiredInteractions", "0")
        self.assert_issue("interactables.minimum")
        self.change("interactables", "requiredInteractions", "11")
        result = self.assert_issue("interactables.recommended_maximum", level="WARNING")
        self.assertTrue(result.ok)
        self.assertTrue(self.pipeline.generate(self.rules).ok)

    def test_range_bounds_and_disable(self):
        self.rule("interactables.minimum")["params"]["minimum"] = 4
        self.assertEqual(sum(i.rule_id == "interactables.minimum"
                             for i in self.pipeline.validate(self.rules).issues), 5)
        self.rule("interactables.minimum")["enabled"] = False
        self.assertTrue(self.pipeline.validate(self.rules).ok)
        self.rule("interactables.minimum")["enabled"] = True
        self.rule("interactables.minimum")["params"]["minimum"] = 1
        self.assertTrue(self.pipeline.validate(self.rules).ok)

    def test_enum(self):
        self.change("interactables", "interactionType", "Gate")
        self.assert_issue("interactables.interaction_type")

    def test_unique_each_table(self):
        for table in ("items", "objectives", "interactables"):
            self.edit_csv(table, lambda rows: rows.append(deepcopy(rows[0])))
            self.assert_issue(table + ".unique_id")

    def test_regex(self):
        self.rules["rules"].append(dict(id="items.naming", type="regex", table="items", field="id",
                                       params={"pattern": "[a-z_]+"}, enabled=True, level="WARNING"))
        self.assertTrue(self.pipeline.validate(self.rules).ok)
        self.change("items", "id", "power_cell!")
        self.assert_issue("items.naming", level="WARNING")

    def test_item_references(self):
        for field in ("requiredItemId", "grantedItemId"):
            self.change("interactables", field, "missing_item")
            self.assert_issue("interactables." + field)
            self.change("interactables", field, "")
        self.assertTrue(self.pipeline.validate(self.rules).ok)

    def test_optional_headers_preserve_existing_contract_defaults(self):
        path = self.pipeline.source_dir / "interactables.csv"
        table = parse_csv_table(path)
        fields = ["id", "displayName", "interactionType", "requiredInteractions", "deactivateOnComplete"]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(table.rows)
        result = self.pipeline.generate()
        self.assertTrue(result.ok, result.issues)
        self.assertTrue(all(c.requiredItemId == c.grantedItemId == c.blockedMessage == c.completionMessage == ""
                            for c in result.content.interactables))

    def test_scene_three_component_types(self):
        for target in ("cube_quick", "power_cell", "power_node"):
            original = self.scene.read_text(encoding="utf-8")
            self.scene.write_text(original.replace("configId: " + target + "\n", "configId: unknown\n"), encoding="utf-8")
            self.assert_issue("scene.config_ids")
            self.scene.write_text(original, encoding="utf-8")

    def test_scene_missing_empty_quoted_and_component_boundary(self):
        self.scene.write_text('--- !u!114 &1\nMonoBehaviour:\n'
            '  m_EditorClassIdentifier: Assembly-CSharp::DeviceInteractable\n'
            '--- !u!1 &2\nGameObject:\n  configId: power_node\n', encoding="utf-8")
        self.assert_issue("scene.config_ids")
        self.scene.write_text('--- !u!114 &1\nMonoBehaviour:\n'
            '  m_EditorClassIdentifier: Assembly-CSharp::DeviceInteractable\n'
            '  configId: "power_node"\n', encoding="utf-8")
        self.assertTrue(self.pipeline.validate(self.rules).ok)
        self.scene.write_text(self.scene.read_text().replace('"power_node"', ""), encoding="utf-8")
        self.assert_issue("scene.config_ids")

    def test_missing_scene(self):
        self.scene.unlink()
        self.assert_issue("scene.config_ids")

    def test_only_configured_scene_is_scanned(self):
        (self.scene.parent / "Other.unity").write_text("configId: missing", encoding="utf-8")
        self.assertTrue(self.pipeline.validate(self.rules).ok)

    def test_malformed_csv_cannot_be_disabled(self):
        path = self.pipeline.source_dir / "items.csv"
        cases = ["id,displayName\npower_cell,Power,Cell\n", 'id,displayName\npower_cell,"unclosed\n',
                 "id,displayName\npower_cell\n", "id,id\na,b\n", "", "id,\na,b\n"]
        for content in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = self.pipeline.generate({"version": 1, "rules": []})
                self.assertFalse(result.ok)
                self.assert_issue("parser.integrity", result)

    def test_fail_safe_generation(self):
        original = self.outputs()
        self.change("interactables", "requiredInteractions", "bad")
        self.assertFalse(self.pipeline.generate(self.rules).ok)
        self.assertEqual(original, self.outputs())
        self.rules["rules"][0]["params"] = {"typo": True}
        self.assertFalse(self.pipeline.generate(self.rules).ok)
        self.assertEqual(original, self.outputs())

    def test_contract_guard_when_type_rule_disabled(self):
        self.rule("interactables.boolean")["enabled"] = False
        self.change("interactables", "deactivateOnComplete", "yes")
        self.assert_issue("contract.conversion")
        self.change("interactables", "deactivateOnComplete", "true")
        self.change("interactables", "requiredInteractions", str(2 ** 31))
        self.assert_issue("contract.conversion")

    def test_missing_input_is_structured_error(self):
        (self.pipeline.source_dir / "items.csv").unlink()
        self.assert_issue("parser.integrity")

    def test_scale_fixture_regression(self):
        for path in (ROOT / "QA" / "Fixtures" / "scale_valid").glob("*.csv"):
            shutil.copy2(path, self.pipeline.source_dir / path.name)
        result = self.pipeline.generate()
        self.assertTrue(result.ok, result.issues)
        self.assertEqual((len(result.content.items), len(result.content.objectives),
                          len(result.content.interactables)), (8, 12, 20))
        self.assertEqual(len(self.pipeline.batch().updates), 8)
        self.assertTrue(self.pipeline.batch(apply=True).ok)
        self.assertTrue(self.pipeline.generate().ok)


class ConfigTests(ProjectCase):
    def test_bad_config_shapes(self):
        for value in (None, [], {}, {"version": True, "rules": []}, {"version": 2, "rules": []},
                      {"version": 1, "rules": [None]}, {"version": 1, "rules": [], "extra": 1}):
            with self.subTest(value=value), self.assertRaises(RuleConfigError):
                check_config(value)

    def test_invalid_rule_fields(self):
        cases = [("type", "python"), ("table", "quests"), ("field", "objectiveId"), ("level", "INFO"),
                 ("enabled", "true"), ("id", "bad id"), ("params", []), ("description", {})]
        for field, value in cases:
            with self.subTest(field=field), self.assertRaises(RuleConfigError):
                rules = deepcopy(self.rules)
                rules["rules"][-1][field] = value
                check_config(rules)

    def test_params_rejected_even_disabled(self):
        cases = [({"minimum": 4, "maximum": 1}), {"minimum": True}, {"minimum": "1"},
                 {"minimum": float("nan")}, {"minimum": 10 ** 400}, {"minimum": 1, "typo": 2}, {}]
        for params in cases:
            with self.subTest(params=params), self.assertRaises(RuleConfigError):
                self.rule("interactables.minimum").update(params=params, enabled=False)
                check_config(self.rules)

    def test_invalid_regex_and_reference(self):
        rule = self.rule("interactables.requiredItemId")
        for target in ({"target_table": "missing", "target_field": "id"},
                       {"target_table": "items", "target_field": "missing"},
                       {"target_table": "batch", "target_field": "id"}):
            rule["params"] = target
            with self.assertRaises(RuleConfigError):
                check_config(self.rules)
        rule.update(type="regex", params={"pattern": "["})
        with self.assertRaises(RuleConfigError):
            check_config(self.rules)

    def test_duplicate_id_and_unsafe_scene_path(self):
        self.rules["rules"].append(deepcopy(self.rules["rules"][0]))
        with self.assertRaises(RuleConfigError):
            check_config(self.rules)
        self.rules["rules"].pop()
        for value in ("../Outside.unity", "/Outside.unity", "C:/Outside.unity", "Assets/*.unity"):
            self.rule("scene.config_ids")["params"]["scene"] = value
            with self.assertRaises(RuleConfigError):
                check_config(self.rules)

    def test_strict_json(self):
        for text in ('{"version":1,"version":1,"rules":[]}', '{"n":NaN}', '{"n":Infinity}', '```json\n{}\n```'):
            with self.assertRaises(RuleConfigError):
                strict_json(text)


class BatchTests(ProjectCase):
    def test_preview_and_apply(self):
        path = self.pipeline.source_dir / "interactables.csv"
        original = path.read_bytes()
        before_json = self.outputs()
        result = self.pipeline.batch()
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(len(result.updates), 3)
        self.assertTrue(self.pipeline.batch(apply=True).ok)
        content = self.pipeline.validate().content
        self.assertEqual({c.id: c.requiredInteractions for c in content.interactables},
                         {"cube_quick": 1, "cube_sturdy": 4, "power_cell": 1, "power_node": 2, "control_terminal": 1})
        self.assertEqual(before_json, self.outputs())

    def test_batch_obeys_changed_rule(self):
        # Make all baseline rows satisfy min=3, then reject ONLY staged values below 3.
        self.edit_csv("interactables", lambda rows: [r.__setitem__("requiredInteractions", "3") for r in rows])
        self.rule("interactables.minimum")["params"]["minimum"] = 3
        self.assertTrue(self.pipeline.validate(self.rules).ok)
        self.assertTrue(self.pipeline.generate(self.rules).ok)
        original = (self.pipeline.source_dir / "interactables.csv").read_bytes()
        for apply in (False, True):
            result = self.pipeline.batch(self.rules, apply=apply)
            self.assertFalse(result.ok)
            self.assert_issue("interactables.minimum", result)
            self.assertEqual(original, (self.pipeline.source_dir / "interactables.csv").read_bytes())

    def test_changed_rule_blocks_generate_too(self):
        self.rule("interactables.minimum")["params"]["minimum"] = 3
        original = self.outputs()
        self.assertFalse(self.pipeline.validate(self.rules).ok)
        self.assertFalse(self.pipeline.generate(self.rules).ok)
        self.assertFalse(self.pipeline.batch(self.rules, apply=True).ok)
        self.assertEqual(original, self.outputs())

    def test_batch_checks_untouched_content_and_scene(self):
        self.change("interactables", "grantedItemId", "missing")
        self.assert_issue("interactables.grantedItemId", self.pipeline.batch())
        self.change("interactables", "grantedItemId", "")
        self.scene.unlink()
        self.assert_issue("scene.config_ids", self.pipeline.batch())

    def test_batch_rejects_unknown_duplicate_and_bad_type(self):
        self.change("batch", "id", "missing")
        self.assert_issue("batch.target", self.pipeline.batch())
        self.change("batch", "id", "power_node")
        self.assert_issue("batch.unique_id", self.pipeline.batch())
        self.change("batch", "id", "cube_sturdy")
        self.change("batch", "requiredInteractions", "abc")
        self.assert_issue("batch.integer", self.pipeline.batch())

    def test_batch_malformed_input_never_writes(self):
        original = (self.pipeline.source_dir / "interactables.csv").read_bytes()
        (self.pipeline.source_dir / "batch_interaction_updates.csv").write_text("id,requiredInteractions\na,2,extra\n")
        self.assert_issue("parser.integrity", self.pipeline.batch(apply=True))
        self.assertEqual(original, (self.pipeline.source_dir / "interactables.csv").read_bytes())

    def test_batch_uses_staged_warning(self):
        self.change("batch", "requiredInteractions", "11")
        result = self.pipeline.batch(apply=True)
        self.assertTrue(result.ok)
        self.assert_issue("interactables.recommended_maximum", result, "WARNING")


class AuthoringTests(ProjectCase):
    def proposal_patch(self):
        rule = deepcopy(self.rule("interactables.minimum"))
        rule["params"]["minimum"] = 4
        return {"operations": [{"op": "update", "rule": rule}]}

    def test_fake_provider_complete_flow(self):
        draft = RuleDraft(self.pipeline.rules_path)
        disk = self.pipeline.rules_path.read_bytes()
        provider = FakeProvider(json.dumps(self.proposal_patch()))
        proposal = author_rules(provider, "Set minimum interactions to 4", self.pipeline.headers(), draft.config)
        self.assertIn("Proposed draft", proposal.preview())
        self.assertFalse(draft.dirty)
        self.assertIn("tables_and_headers", provider.requests[0][1])
        self.assertNotIn("rows", provider.requests[0][1])
        draft.apply(proposal)
        self.assertTrue(draft.dirty)
        self.assertFalse(self.pipeline.validate(draft.config).ok)
        self.assertEqual(disk, self.pipeline.rules_path.read_bytes())
        draft.save()
        self.assertFalse(draft.dirty)
        draft.reload()
        self.assertEqual(draft.config, proposal.proposed)

    def test_add_disable_and_patch_atomicity(self):
        new = deepcopy(self.rule("interactables.minimum"))
        new["id"] = "new.minimum"
        proposal = validate_patch({"operations": [{"op": "add", "rule": new},
            {"op": "disable", "id": "interactables.minimum"}]}, self.rules)
        self.assertFalse(next(r for r in proposal.proposed["rules"] if r["id"] == "interactables.minimum")["enabled"])
        baseline = deepcopy(self.rules)
        with self.assertRaises(RuleConfigError):
            validate_patch({"operations": [{"op": "add", "rule": new}, {"op": "disable", "id": "missing"}]}, self.rules)
        self.assertEqual(baseline, self.rules)

    def test_invalid_ai_output(self):
        cases = ["not JSON", "[]", '{"operations":[]}', '{"operations":[{"op":"delete","id":"items.required"}]}',
                 '{"operations":[{"op":"disable","id":"missing"}]}',
                 '{"operations":[{"op":"add","rule":null}]}']
        for value in cases:
            with self.subTest(value=value), self.assertRaises(RuleConfigError):
                author_rules(FakeProvider(value), "request", self.pipeline.headers(), self.rules)

    def test_invalid_ai_rules(self):
        for field, value in (("type", "exec"), ("table", "quests"), ("params", {"minimum": "four"}),
                             ("field", "objectiveId")):
            candidate = self.proposal_patch()
            candidate["operations"][0]["rule"][field] = value
            with self.subTest(field=field), self.assertRaises(RuleConfigError):
                validate_patch(candidate, self.rules)
        candidate = self.proposal_patch()
        candidate["operations"][0]["op"] = "add"
        with self.assertRaises(RuleConfigError):
            validate_patch(candidate, self.rules)

    def test_draft_crud_dirty_reload_and_save(self):
        draft = RuleDraft(self.pipeline.rules_path)
        self.assertFalse(draft.dirty)
        copied = draft.duplicate("interactables.minimum")
        self.assertTrue(draft.dirty)
        draft.toggle(copied)
        self.assertFalse(next(r for r in draft.config["rules"] if r["id"] == copied)["enabled"])
        draft.delete(copied)
        self.assertFalse(draft.dirty)
        changed = deepcopy(self.rule("interactables.minimum"))
        changed["params"]["minimum"] = 4
        draft.put_rule(changed, changed["id"])
        self.assertFalse(self.pipeline.validate(draft.config).ok)
        draft.reload()
        self.assertFalse(draft.dirty)
        self.assertTrue(self.pipeline.validate(draft.config).ok)
        draft.put_rule(changed, changed["id"])
        draft.save()
        self.assertFalse(draft.dirty)
        self.assertEqual(load_config(draft.path), draft.config)

    def test_external_conflict_and_failed_save_keep_draft(self):
        draft = RuleDraft(self.pipeline.rules_path)
        draft.toggle("items.required")
        with patch("pipeline_core.os.replace", side_effect=OSError("locked")):
            with self.assertRaises(OSError):
                draft.save()
        self.assertTrue(draft.dirty)
        self.assertEqual(load_config(draft.path), self.rules)
        self.assertFalse(list(draft.path.parent.glob("*.tmp")))
        draft.path.write_bytes(draft.path.read_bytes() + b"\n")
        with self.assertRaises(RuleConfigError):
            draft.save()

    def test_stale_or_tampered_proposal_rejected(self):
        draft = RuleDraft(self.pipeline.rules_path)
        proposal = validate_patch(self.proposal_patch(), draft.config)
        draft.toggle("items.required")
        with self.assertRaises(RuleConfigError):
            draft.apply(proposal)
        draft.reload()
        proposal.proposed["rules"] = []
        with self.assertRaises(RuleConfigError):
            draft.apply(proposal)

    def test_no_ai_environment_required(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertTrue(self.pipeline.validate().ok)
            self.assertTrue(self.pipeline.generate().ok)
            self.assertTrue(self.pipeline.batch().ok)
            self.assertTrue(self.pipeline.batch(apply=True).ok)
            with self.assertRaisesRegex(RuleConfigError, "OPENAI_API_KEY"):
                OpenAIProvider().propose("request", {})

    def test_openai_transport_and_response_without_network(self):
        envelope = {"status": "completed", "output": [
            {"type": "reasoning"},
            {"type": "message", "content": [{"type": "output_text", "text": json.dumps(self.proposal_patch())}]},
        ]}
        response = io.BytesIO(json.dumps(envelope).encode("utf-8"))
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"}), \
                patch("urllib.request.urlopen", return_value=response) as request:
            proposal = author_rules(OpenAIProvider(), "minimum should be four", self.pipeline.headers(), self.rules)
        minimum_rule = next(r for r in proposal.proposed["rules"] if r["id"] == "interactables.minimum")
        self.assertEqual(minimum_rule["params"]["minimum"], 4)
        sent = json.loads(request.call_args.args[0].data)
        self.assertEqual(sent["model"], "test-model")
        self.assertFalse(sent["store"])
        self.assertEqual(sent["text"]["format"]["type"], "json_object")
        self.assertIn("minimum should be four", sent["input"])
        self.assertNotIn("Power Cell acquired", sent["input"])
        self.assertNotIn("test-key", sent["input"])

    def test_openai_refusal_incomplete_and_bad_envelope(self):
        for envelope in ({"status": "incomplete"}, {"status": "completed", "output": [
                {"type": "message", "content": [{"type": "refusal", "refusal": "No"}]}]},
                {"status": "completed", "output": [None]}):
            with self.subTest(envelope=envelope), \
                    patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}), \
                    patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode())), \
                    self.assertRaises(RuleConfigError):
                OpenAIProvider("test-model").propose("request", {})

    def test_openai_http_errors_do_not_echo_credentials(self):
        from urllib.error import HTTPError
        failure = HTTPError("https://api.openai.com/v1/responses", 401, "test-key", {}, None)
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}), \
                patch("urllib.request.urlopen", side_effect=failure), \
                self.assertRaises(RuleConfigError) as caught:
            OpenAIProvider("test-model").propose("request", {})
        self.assertIn("401", str(caught.exception))
        self.assertNotIn("test-key", str(caught.exception))


class PublicationTests(ProjectCase):
    def test_multi_file_write_failure_rolls_back(self):
        original = self.outputs()
        self.change("objectives", "displayName", "Changed")
        self.change("interactables", "displayName", "Changed")
        import os
        replace = os.replace
        calls = []

        def fail_second(source, destination):
            calls.append(destination)
            if len(calls) == 2:
                raise OSError("simulated second output failure")
            return replace(source, destination)

        with patch("pipeline_core.os.replace", side_effect=fail_second):
            self.assertFalse(self.pipeline.generate().ok)
        self.assertEqual(original, self.outputs())
        self.assertFalse(list(self.pipeline.output_dir.glob("*.tmp")))

    def test_cli_compatibility_and_exit_codes(self):
        for command in ([], ["--help"], ["rules-check"], ["validate"], ["generate"], ["batch-preview"], ["batch-apply"]):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(TOOLS / "config_tool.py"), *command,
                    "--root", str(self.root)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.change("items", "displayName", "")
        result = subprocess.run([sys.executable, str(TOOLS / "config_tool.py"), "validate", "--root", str(self.root)],
                                 capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("items.required", result.stdout)


if __name__ == "__main__":
    unittest.main()
