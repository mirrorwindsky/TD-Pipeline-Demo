"""Key persistence tests use fake stores; native round-trip is opt-in and synthetic."""
import os
import sys
import unittest
from unittest.mock import patch
import uuid

from test_pipeline import ProjectCase
from ai_credentials import CredentialError, KeySettings, WindowsCredentialStore, checked_key
from rule_authoring import DeepSeekProvider, OpenAIProvider


class MemoryStore:
    available = True

    def __init__(self):
        self.values = {}
        self.writes = []

    def read(self, provider):
        return self.values.get(provider)

    def write(self, provider, key):
        if not key:
            raise CredentialError("Enter an API key before remembering it")
        self.values[provider] = key
        self.writes.append(provider)

    def delete(self, provider):
        self.values.pop(provider, None)


class CredentialTests(unittest.TestCase):
    def test_session_remember_reload_forget_and_provider_isolation(self):
        store = MemoryStore()
        settings = KeySettings(store)
        self.assertFalse(settings.get("DeepSeek").remember)
        settings.edit("DeepSeek", "session-key", False)
        self.assertEqual(settings.get("DeepSeek").key, "session-key")
        self.assertFalse(store.writes)
        settings.apply("DeepSeek", "remembered-key", True)
        settings.apply("OpenAI", "different-key", True)
        reloaded = KeySettings(store)
        self.assertEqual(reloaded.get("DeepSeek").key, "remembered-key")
        reloaded.forget("DeepSeek")
        self.assertIsNone(store.read("DeepSeek"))
        self.assertEqual(store.read("OpenAI"), "different-key")
        reloaded.apply("OpenAI", "session-only", False)
        self.assertIsNone(store.read("OpenAI"))
        self.assertEqual(reloaded.get("OpenAI").key, "session-only")
        self.assertNotIn("session-only", repr(reloaded.profiles))

    def test_invalid_key_rejected_without_echo(self):
        for key in ("secret\nheader", "secret key", "密钥", "a" * 2561):
            with self.assertRaises(CredentialError) as caught:
                checked_key(key)
            self.assertNotIn(key, str(caught.exception))
        self.assertEqual(checked_key("  session-key \r\n"), "session-key")

    def test_read_or_write_failure_has_no_plaintext_fallback(self):
        store = MemoryStore()
        settings = KeySettings(store)
        with patch.object(store, "read", side_effect=CredentialError("read failed")), self.assertRaises(CredentialError):
            settings.get("DeepSeek")
        settings.edit("DeepSeek", "session-key", True)
        with patch.object(store, "write", side_effect=CredentialError("write failed")), self.assertRaises(CredentialError):
            settings.apply("DeepSeek", "session-key", True)
        self.assertEqual(settings.get("DeepSeek").key, "session-key")
        self.assertFalse(store.values)

    def test_explicit_key_beats_environment_for_each_provider(self):
        cases = [(OpenAIProvider, {"status": "completed", "output": [{"type": "message", "content": [
                    {"type": "output_text", "text": "{}"}]}]}),
                 (DeepSeekProvider, {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]})]
        for provider, envelope in cases:
            with self.subTest(provider=provider.__name__), patch.dict(os.environ, {
                    "OPENAI_API_KEY": "old-openai", "DEEPSEEK_API_KEY": "old-deepseek"}), \
                    patch("rule_authoring._post_json", return_value=envelope) as request:
                provider("model", api_key="explicit-session-key").propose("request", {})
            self.assertEqual(request.call_args.args[1], "explicit-session-key")
            self.assertNotIn("explicit-session-key", str(request.call_args.args[2]))

    @unittest.skipUnless(sys.platform == "win32" and os.environ.get("TD_TEST_WINDOWS_CREDENTIALS") == "1",
                         "Opt-in native credential test")
    def test_native_round_trip_in_isolated_test_namespace(self):
        store = WindowsCredentialStore("TD-Pipeline-Demo/Test/" + uuid.uuid4().hex)
        try:
            self.assertIsNone(store.read("DeepSeek"))
            store.write("DeepSeek", "synthetic-test-value")
            self.assertEqual(store.read("DeepSeek"), "synthetic-test-value")
            store.write("DeepSeek", "updated-synthetic-value")
            self.assertEqual(store.read("DeepSeek"), "updated-synthetic-value")
        finally:
            store.delete("DeepSeek")
        self.assertIsNone(store.read("DeepSeek"))


if __name__ == "__main__":
    unittest.main()
