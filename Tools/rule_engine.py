"""Strict RuleSpec checking and deterministic validation over SourceTable strings."""
import json
import math
from pathlib import Path, PurePosixPath
import re

from pipeline_model import ERROR, TABLE_HEADERS, ValidationIssue


# Both the editor and AI provider use these examples as the supported vocabulary.
RULE_TYPES = {
    "columns": {"fields": ["id"]},
    "required": {"fields": ["id"]},
    "type": {"value_type": "integer", "allow_empty": False},
    "range": {"minimum": 1, "maximum": 10, "allow_empty": False},
    "enum": {"values": ["Pickup", "Device"], "allow_empty": False},
    "unique": {"allow_empty": False},
    "regex": {"pattern": "^[a-z][a-z0-9_]*$", "allow_empty": False},
    "reference": {"target_table": "items", "target_field": "id", "allow_empty": True},
    "scene_reference": {
        "scene": "Assets/Scenes/VerticalSlice_01.unity",
        "components": ["Assembly-CSharp::ConfigurableInteractable"],
        "source_field": "configId",
    },
}


class RuleConfigError(ValueError):
    pass


def strict_json(text):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise RuleConfigError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise RuleConfigError(f"Invalid JSON number: {value}")

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, TypeError, RecursionError) as exc:
        raise RuleConfigError(f"Invalid JSON: {exc}") from exc


def _require(condition, message):
    if not condition:
        raise RuleConfigError(message)


def _strings(value):
    return (isinstance(value, list) and bool(value)
            and all(isinstance(v, str) and bool(v.strip()) for v in value)
            and len(set(value)) == len(value))


def _finite_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def check_config(config):
    """Reject typos and invalid disabled rules too; no mutation or file access."""
    _require(isinstance(config, dict) and set(config) == {"version", "rules"},
             "Rule config must contain only version and rules")
    _require(type(config["version"]) is int and config["version"] == 1,
             "Unsupported RuleSpec version (expected 1)")
    _require(isinstance(config["rules"], list), "rules must be an array")
    seen = set()
    for rule in config["rules"]:
        _require(isinstance(rule, dict), "Each rule must be an object")
        required = {"id", "type", "table", "field", "params", "level", "enabled"}
        _require(required <= set(rule) <= required | {"description"},
                 "Rule keys must be id/type/table/field/params/level/enabled and optional description")
        rid = rule["id"]
        _require(isinstance(rid, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]*", rid),
                 "Rule id must be a stable identifier")
        _require(rid not in seen, f"Duplicate rule id: {rid}")
        seen.add(rid)
        kind, table, field, params = (rule[k] for k in ("type", "table", "field", "params"))
        _require(isinstance(kind, str) and kind in RULE_TYPES, f"{rid}: unknown rule type")
        _require(isinstance(table, str) and table in TABLE_HEADERS, f"{rid}: unknown table")
        _require(isinstance(field, str), f"{rid}: field must be a string")
        _require(isinstance(rule["level"], str) and rule["level"] in {"ERROR", "WARNING"},
                 f"{rid}: level must be ERROR or WARNING")
        _require(type(rule["enabled"]) is bool, f"{rid}: enabled must be boolean")
        _require(isinstance(rule.get("description", ""), str), f"{rid}: description must be text")
        _require(isinstance(params, dict), f"{rid}: params must be an object")
        allowed = set(RULE_TYPES[kind])
        mandatory = allowed - {"allow_empty"}
        if kind == "range":
            mandatory = set()
        _require(mandatory <= set(params) <= allowed, f"{rid}: invalid params for {kind}")
        if "allow_empty" in params:
            _require(type(params["allow_empty"]) is bool, f"{rid}: allow_empty must be boolean")
        if kind in {"columns", "required"}:
            _require(field == "", f"{rid}: columns/required use params.fields, field must be empty")
            _require(_strings(params["fields"]), f"{rid}: fields must be a nonempty unique string array")
            _require(all(f in TABLE_HEADERS[table] for f in params["fields"]), f"{rid}: unknown field")
        else:
            _require(field in TABLE_HEADERS[table], f"{rid}: unknown field {field}")
        if kind == "type":
            _require(isinstance(params["value_type"], str)
                     and params["value_type"] in {"integer", "boolean", "string"},
                     f"{rid}: value_type must be integer, boolean or string")
        elif kind == "range":
            _require("minimum" in params or "maximum" in params, f"{rid}: range needs a bound")
            for key in ("minimum", "maximum"):
                if key in params:
                    _require(_finite_number(params[key]),
                             f"{rid}: {key} must be a finite number")
            if "minimum" in params and "maximum" in params:
                _require(params["minimum"] <= params["maximum"], f"{rid}: reversed range")
        elif kind == "enum":
            _require(_strings(params["values"]), f"{rid}: values must be a nonempty unique string array")
        elif kind == "regex":
            _require(isinstance(params["pattern"], str) and len(params["pattern"]) <= 512,
                     f"{rid}: pattern must be a string of at most 512 characters")
            try:
                re.compile(params["pattern"])
            except (re.error, RecursionError) as exc:
                raise RuleConfigError(f"{rid}: invalid regex: {exc}") from exc
        elif kind == "reference":
            target = params["target_table"]
            _require(isinstance(target, str) and target in TABLE_HEADERS, f"{rid}: unknown reference table")
            _require(params["target_field"] in TABLE_HEADERS[target], f"{rid}: unknown reference field")
            _require(table == "batch" or target != "batch", f"{rid}: content cannot depend on optional batch input")
        elif kind == "scene_reference":
            scene = params["scene"]
            _require(isinstance(scene, str) and bool(scene), f"{rid}: scene must be a relative Unity path")
            path = PurePosixPath(scene)
            _require(not path.is_absolute() and ".." not in path.parts and ":" not in scene
                     and "\\" not in scene and not any(c in scene for c in "*?[]")
                     and path.suffix == ".unity", f"{rid}: invalid scene path")
            _require(_strings(params["components"]), f"{rid}: components must be a string array")
            _require(isinstance(params["source_field"], str)
                     and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", params["source_field"]),
                     f"{rid}: invalid source_field")
            _require(table != "batch", f"{rid}: scene cannot reference batch")
    return config


def load_config(path):
    try:
        return check_config(strict_json(Path(path).read_text(encoding="utf-8-sig")))
    except (OSError, UnicodeError) as exc:
        raise RuleConfigError(f"Cannot read rules: {exc}") from exc


def _scene_issues(rule, table, root):
    params = rule["params"]
    path = (root / params["scene"]).resolve()
    if not path.is_relative_to(root.resolve()):
        return [(None, "Scene path escapes project root")]
    try:
        scene = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [(None, f"Cannot read scene {params['scene']}: {exc}")]
    ids = {(row.get(rule["field"]) or "").strip() for row in table.rows}
    issues = []
    # Bound each YAML object so another component cannot supply a missing configId.
    for block in re.split(r"(?m)^--- !u!", scene):
        if not block.startswith("114 "):
            continue
        identifier = re.search(r"(?m)^\s*m_EditorClassIdentifier:[ \t]*([^\r\n]*)", block)
        if not identifier or identifier.group(1).strip() not in params["components"]:
            continue
        match = re.search(r"(?m)^[ \t]*" + re.escape(params["source_field"])
                          + r":[ \t]*([^\r\n]*)", block)
        value = match.group(1).strip() if match else ""
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                pass
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        if not isinstance(value, str) or not value or value not in ids:
            issues.append((None, f"{params['scene']}: {identifier.group(1).strip()} "
                           f"has missing/unknown {params['source_field']}: {value!r}"))
    return issues


def validate_tables(tables, config, root, only=None):
    """Run one checked rule set. Batch rules run only when batch is loaded."""
    check_config(config)
    issues = []
    for rule in config["rules"]:
        name = rule["table"]
        if not rule["enabled"] or name not in tables or (only is not None and name not in only):
            continue
        table, kind, field, params = tables[name], rule["type"], rule["field"], rule["params"]

        def emit(row, message, issue_field=field):
            issues.append(ValidationIssue(rule["level"], message, rule["id"], name, row, issue_field))

        if kind == "scene_reference":
            for number, message in _scene_issues(rule, table, Path(root)):
                emit(number, message)
            continue
        fields = params["fields"] if kind in {"columns", "required"} else [field]
        missing = [f for f in fields if f not in table.fieldnames]
        # Optional source fields historically may be omitted from the CSV header.
        # A columns rule can still explicitly require their presence.
        if missing and params.get("allow_empty", False):
            continue
        for f in missing:
            emit(None, f"Missing column '{f}'", f)
        if kind == "columns":
            continue
        seen = set()
        target_values = set()
        if kind == "reference":
            target = tables.get(params["target_table"])
            if target is None or params["target_field"] not in target.fieldnames:
                emit(None, "Reference target table/column is unavailable")
                continue
            target_values = {(r.get(params["target_field"]) or "").strip() for r in target.rows}
        for number, row in enumerate(table.rows, 2):
            if kind == "required":
                for f in fields:
                    if f not in missing and not (row.get(f) or "").strip():
                        emit(number, "Value is required", f)
                continue
            if missing:
                continue
            value = (row.get(field) or "").strip()
            if not value and params.get("allow_empty", False):
                continue
            if kind == "type":
                value_type = params["value_type"]
                valid = True
                if value_type == "integer":
                    try:
                        int(value)
                    except ValueError:
                        valid = False
                elif value_type == "boolean":
                    valid = value.lower() in {"true", "false"}
                if not valid:
                    emit(number, f"Expected {value_type}, got {value!r}")
            elif kind == "range":
                try:
                    number_value = float(value)
                except ValueError:
                    number_value = math.nan
                if not math.isfinite(number_value):
                    emit(number, f"Expected finite number, got {value!r}")
                elif (("minimum" in params and number_value < params["minimum"])
                      or ("maximum" in params and number_value > params["maximum"])):
                    emit(number, f"Value {value} outside range "
                         f"[{params.get('minimum', '-inf')}, {params.get('maximum', 'inf')}]")
            elif kind == "enum" and value not in params["values"]:
                emit(number, f"Expected one of {params['values']}, got {value!r}")
            elif kind == "unique":
                if value in seen:
                    emit(number, f"Duplicate value {value!r}")
                seen.add(value)
            elif kind == "regex" and not re.fullmatch(params["pattern"], value):
                emit(number, f"Value {value!r} does not match {params['pattern']!r}")
            elif kind == "reference" and (not value or value not in target_values):
                emit(number, f"Unknown reference {value!r} to {params['target_table']}.{params['target_field']}")
    return issues
