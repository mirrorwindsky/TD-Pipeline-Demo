"""Explicit draft persistence and optional AI proposals; never execute generated code."""
from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Protocol

from pipeline_core import atomic_write_many, json_bytes
from ai_credentials import checked_key
from rule_engine import RULE_TYPES, RuleConfigError, check_config, strict_json


@dataclass
class RuleProposal:
    base: dict
    patch: dict
    proposed: dict

    def preview(self, before="Current draft", after="Proposed draft"):
        import difflib
        return "".join(difflib.unified_diff(
            json.dumps(self.base, indent=2, ensure_ascii=False).splitlines(True),
            json.dumps(self.proposed, indent=2, ensure_ascii=False).splitlines(True),
            fromfile=before, tofile=after))


def validate_patch(raw, base):
    """Build a fully checked candidate without mutating the supplied draft."""
    check_config(base)
    patch = strict_json(raw) if isinstance(raw, str) else deepcopy(raw)
    if (not isinstance(patch, dict) or set(patch) != {"operations"}
            or not isinstance(patch["operations"], list) or not patch["operations"]):
        raise RuleConfigError("RulePatch must contain a nonempty operations array")
    candidate = deepcopy(base)
    touched = set()
    for operation in patch["operations"]:
        if not isinstance(operation, dict):
            raise RuleConfigError("Patch operation must be an object")
        op = operation.get("op")
        if not isinstance(op, str) or op not in {"add", "update", "disable"}:
            raise RuleConfigError("Only add, update and disable operations are supported")
        keys = {"op", "id"} if op == "disable" else {"op", "rule"}
        if set(operation) != keys:
            raise RuleConfigError(f"{op} requires exactly {sorted(keys)}")
        rule = operation.get("rule")
        rid = operation.get("id") if op == "disable" else rule.get("id") if isinstance(rule, dict) else None
        if not isinstance(rid, str) or not rid or rid in touched:
            raise RuleConfigError("Every operation must target a distinct rule id")
        touched.add(rid)
        existing = next((r for r in candidate["rules"] if r["id"] == rid), None)
        if op == "add":
            if existing is not None:
                raise RuleConfigError(f"Rule id already exists: {rid}")
            candidate["rules"].append(deepcopy(rule))
        else:
            if existing is None:
                raise RuleConfigError(f"Update target does not exist: {rid}")
            if op == "disable":
                existing["enabled"] = False
            else:
                candidate["rules"][candidate["rules"].index(existing)] = deepcopy(rule)
    check_config(candidate)
    return RuleProposal(deepcopy(base), patch, candidate)


class RuleDraft:
    def __init__(self, path):
        self.path = Path(path)
        self.reload()

    @property
    def config(self):
        return deepcopy(self._config)

    @property
    def dirty(self):
        return self._config != self._saved

    def reload(self):
        # Read one snapshot so external writes cannot desynchronize config and conflict detection.
        snapshot = self.path.read_bytes()
        config = check_config(strict_json(snapshot.decode("utf-8-sig")))
        self._config = config
        self._saved = deepcopy(config)
        self._disk = snapshot

    def replace(self, config):
        self._config = deepcopy(check_config(config))

    def put_rule(self, rule, target=None):
        config = self.config
        if target is None:
            config["rules"].append(deepcopy(rule))
        else:
            index = next((i for i, r in enumerate(config["rules"]) if r["id"] == target), None)
            if index is None:
                raise RuleConfigError(f"Rule does not exist: {target}")
            config["rules"][index] = deepcopy(rule)
        self.replace(config)

    def delete(self, rid):
        config = self.config
        if not any(r["id"] == rid for r in config["rules"]):
            raise RuleConfigError(f"Rule does not exist: {rid}")
        config["rules"] = [r for r in config["rules"] if r["id"] != rid]
        self.replace(config)

    def duplicate(self, rid):
        source = next((r for r in self.config["rules"] if r["id"] == rid), None)
        if source is None:
            raise RuleConfigError(f"Rule does not exist: {rid}")
        ids = {r["id"] for r in self._config["rules"]}
        new_id, suffix = rid + "_copy", 2
        while new_id in ids:
            new_id = rid + f"_copy{suffix}"
            suffix += 1
        source["id"] = new_id
        self.put_rule(source)
        return new_id

    def toggle(self, rid):
        rule = next((r for r in self.config["rules"] if r["id"] == rid), None)
        if rule is None:
            raise RuleConfigError(f"Rule does not exist: {rid}")
        rule["enabled"] = not rule["enabled"]
        self.put_rule(rule, rid)

    def apply(self, proposal):
        if proposal.base != self._config:
            raise RuleConfigError("Draft changed since proposal creation; generate a new proposal")
        # Recheck even a programmatically constructed or subsequently modified proposal.
        checked = validate_patch(proposal.patch, self._config)
        if checked.proposed != proposal.proposed:
            raise RuleConfigError("Proposal preview does not match patch")
        self.replace(checked.proposed)

    def save(self):
        check_config(self._config)
        if self.path.read_bytes() != self._disk:
            raise RuleConfigError("Rule file changed outside this tool. Reload before saving")
        payload = json_bytes(self._config) + b"\n"
        atomic_write_many({self.path: payload})
        self._disk = payload
        self._saved = self.config


class RuleProvider(Protocol):
    def propose(self, request: str, context: dict) -> str: ...


def author_rules(provider: RuleProvider, request, headers, rules):
    if not isinstance(request, str) or not request.strip():
        raise RuleConfigError("Describe the rule you want to add or change")
    base = deepcopy(check_config(rules))
    context = {
        "tables_and_headers": deepcopy(headers),
        "supported_rule_types_and_param_examples": deepcopy(RULE_TYPES),
        "current_rule_set": deepcopy(base),
        "patch_format": {
            "operations": [{"op": "add or update", "rule": "complete RuleSpec object"},
                           {"op": "disable", "id": "existing rule id"}],
        },
        "rule_spec": {"id": "stable unique string", "type": "supported rule type",
                      "table": "existing table", "field": "existing field (empty for columns/required)",
                      "params": "type-specific object", "enabled": True, "level": "ERROR or WARNING",
                      "description": "optional text"},
        "semantics": "regex uses fullmatch; allow_empty defaults false; range bounds are inclusive; "
                     "batch changes are validated by all interactables rules after staging. "
                     "Optional reference fields may be empty. Never introduce new gameplay fields.",
    }
    return validate_patch(provider.propose(request, context), base)


class FakeProvider:
    """Deterministic test double; records authoring input and returns supplied JSON."""
    def __init__(self, response):
        self.response = response
        self.requests = []

    def propose(self, request, context):
        self.requests.append((request, deepcopy(context)))
        return self.response


AUTHORING_INSTRUCTIONS = (
    "Translate the user's validation policy into a JSON RulePatch. "
    "Return only an object with operations. Allowed ops: add, update (complete rule), disable. "
    "Never delete, write files, generate Python, or judge CSV content. "
    "Use only the supplied tables, headers, RuleSpec and supported types. "
    'Example JSON: {"operations": [{"op": "disable", "id": "existing.rule.id"}]}. '
    'Return {"operations": []} if the request cannot be represented.'
)
DEEPSEEK_DEFAULT_MODEL = "deepseek-flash"


def _post_json(url, key, payload):
    # Lazy stdlib transport shared by providers. No SDK dependency or persisted credentials.
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen

    request = Request(url, data=json_bytes(payload),
                      headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=45) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise RuleConfigError("AI response is too large")
        return strict_json(raw.decode("utf-8"))
    except HTTPError as exc:
        code = exc.code
        exc.close()
        raise RuleConfigError(f"AI request failed (HTTP {code}); check model/access/quota") from None
    except (URLError, OSError, UnicodeError) as exc:
        raise RuleConfigError(f"AI connection failed ({type(exc).__name__}); try again") from None
    except ValueError as exc:
        if isinstance(exc, RuleConfigError):
            raise
        # Invalid header values can contain credentials; do not echo them.
        raise RuleConfigError("Invalid AI request configuration") from None


class OpenAIProvider:
    """Optional provider using stdlib HTTPS; no SDK installation or import required."""
    def __init__(self, model=None, api_key=None):
        self.model = model or os.environ.get("OPENAI_MODEL", "")
        self._api_key = api_key

    def propose(self, request, context):
        # Explicit GUI key takes precedence; environment variables remain a compatibility fallback.
        key = checked_key(self._api_key if self._api_key is not None else os.environ.get("OPENAI_API_KEY", ""))
        if not key:
            raise RuleConfigError("AI unavailable: set OPENAI_API_KEY in the environment")
        if not self.model.strip():
            raise RuleConfigError("Enter an OpenAI model ID or set OPENAI_MODEL")
        payload = {
            "model": self.model.strip(), "store": False,
            "instructions": AUTHORING_INSTRUCTIONS,
            "input": json.dumps({"request": request, "context": context}, ensure_ascii=False),
            "text": {"format": {"type": "json_object"}},
        }
        data = _post_json("https://api.openai.com/v1/responses", key, payload)
        if not isinstance(data, dict) or data.get("status") != "completed":
            raise RuleConfigError("AI response was incomplete or refused; no proposal was applied")
        try:
            output = "".join(part["text"] for item in data.get("output", [])
                             if item.get("type") == "message" for part in item.get("content", [])
                             if part.get("type") == "output_text")
        except (KeyError, TypeError, AttributeError):
            raise RuleConfigError("Malformed AI response envelope") from None
        if not output:
            raise RuleConfigError("AI returned no rule proposal")
        return output


class DeepSeekProvider:
    """DeepSeek Chat Completions JSON mode, followed by the same local RulePatch checks."""
    def __init__(self, model=None, api_key=None):
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
        self._api_key = api_key

    def propose(self, request, context):
        key = checked_key(self._api_key if self._api_key is not None else os.environ.get("DEEPSEEK_API_KEY", ""))
        if not key:
            raise RuleConfigError("AI unavailable: set DEEPSEEK_API_KEY in the environment")
        if not self.model.strip():
            raise RuleConfigError("Enter a DeepSeek model ID or set DEEPSEEK_MODEL")
        payload = {
            "model": self.model.strip(),
            "messages": [
                {"role": "system", "content": AUTHORING_INSTRUCTIONS},
                {"role": "user", "content": json.dumps({"request": request, "context": context}, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "max_tokens": 4096,
            "stream": False,
        }
        data = _post_json("https://api.deepseek.com/chat/completions", key, payload)
        try:
            choices = data["choices"]
            if not isinstance(choices, list) or len(choices) != 1:
                raise RuleConfigError("Malformed AI response envelope")
            choice = choices[0]
            if choice.get("finish_reason") != "stop" or choice["message"].get("refusal"):
                raise RuleConfigError("AI response was incomplete or refused; no proposal was applied")
            output = choice["message"]["content"]
        except (KeyError, TypeError, AttributeError):
            raise RuleConfigError("Malformed AI response envelope") from None
        if not isinstance(output, str) or not output.strip():
            raise RuleConfigError("AI returned no rule proposal")
        return output
