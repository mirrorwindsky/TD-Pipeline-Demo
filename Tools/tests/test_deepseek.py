"""DeepSeek adapter contracts; all HTTP calls are mocked."""
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from test_pipeline import ProjectCase
from rule_authoring import DEEPSEEK_DEFAULT_MODEL, DeepSeekProvider, RuleDraft, author_rules
from rule_engine import RuleConfigError


class DeepSeekTests(ProjectCase):
    def envelope(self, content, reason="stop"):
        return {"choices": [{"finish_reason": reason, "message": {"role": "assistant", "content": content}}]}

    def request(self, envelope):
        return patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode("utf-8")))

    def test_full_proposal_flow_and_request_contract(self):
        rule = self.rule("interactables.minimum")
        rule["params"]["minimum"] = 4
        content = json.dumps({"operations": [{"op": "update", "rule": rule}]})
        draft = RuleDraft(self.pipeline.rules_path)
        original = draft.path.read_bytes()
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "deepseek-test-key", "DEEPSEEK_MODEL": "custom-model",
                                     "OPENAI_API_KEY": "different-openai-key"}, clear=True), \
                self.request(self.envelope(content)) as request:
            proposal = author_rules(DeepSeekProvider(), "将最小交互次数改为 4", self.pipeline.headers(), draft.config)
        http = request.call_args.args[0]
        body = json.loads(http.data)
        self.assertEqual(http.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(http.get_header("Authorization"), "Bearer deepseek-test-key")
        self.assertEqual(body["model"], "custom-model")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertFalse(body["stream"])
        self.assertGreater(body["max_tokens"], 0)
        self.assertIn("JSON", body["messages"][0]["content"])
        user = json.loads(body["messages"][1]["content"])
        self.assertEqual(user["request"], "将最小交互次数改为 4")
        self.assertIn("tables_and_headers", user["context"])
        self.assertNotIn("Power Cell acquired", json.dumps(body))
        self.assertNotIn("deepseek-test-key", json.dumps(body))
        self.assertFalse(draft.dirty)
        draft.apply(proposal)
        self.assertFalse(self.pipeline.validate(draft.config).ok)
        self.assertTrue(draft.dirty)
        self.assertEqual(draft.path.read_bytes(), original)

    def test_no_key_and_model_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(DeepSeekProvider().model, DEEPSEEK_DEFAULT_MODEL)
            with patch("urllib.request.urlopen") as request, self.assertRaisesRegex(RuleConfigError, "DEEPSEEK_API_KEY"):
                DeepSeekProvider().propose("request", {})
            request.assert_not_called()
            self.assertTrue(self.pipeline.validate().ok)
        with patch.dict(os.environ, {"DEEPSEEK_MODEL": "env-model"}):
            self.assertEqual(DeepSeekProvider().model, "env-model")
            self.assertEqual(DeepSeekProvider("explicit-model").model, "explicit-model")

    def test_rejects_empty_truncated_refused_and_malformed_responses(self):
        cases = [None, {}, {"choices": []}, {"choices": [None]}, self.envelope(""),
                 self.envelope(None), self.envelope({}), self.envelope("{}", "length"),
                 self.envelope("{}", "content_filter"), self.envelope("{}", "tool_calls")]
        for envelope in cases:
            with self.subTest(envelope=envelope), patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), \
                    self.request(envelope), self.assertRaises(RuleConfigError):
                DeepSeekProvider().propose("request", {})

    def test_invalid_json_and_rule_never_reach_draft(self):
        draft = RuleDraft(self.pipeline.rules_path)
        original = draft.path.read_bytes()
        rule = self.rule("interactables.minimum")
        rule["params"] = {"minimum": "four"}
        for content in ("not JSON", json.dumps({"operations": [{"op": "update", "rule": rule}]})):
            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), self.request(self.envelope(content)), \
                    self.assertRaises(RuleConfigError):
                author_rules(DeepSeekProvider(), "request", self.pipeline.headers(), draft.config)
        self.assertFalse(draft.dirty)
        self.assertEqual(draft.path.read_bytes(), original)

    def test_http_and_connection_errors_do_not_echo_key(self):
        for error in (HTTPError("https://api.deepseek.com/chat/completions", 401, "secret-key", {}, None),
                      URLError("secret-key"), TimeoutError("secret-key"), ValueError("secret-key")):
            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "secret-key"}), \
                    patch("urllib.request.urlopen", side_effect=error), self.assertRaises(RuleConfigError) as caught:
                DeepSeekProvider().propose("request", {})
            self.assertNotIn("secret-key", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
