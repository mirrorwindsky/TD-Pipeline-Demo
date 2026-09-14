"""Shared CLI/GUI services: parse, validate, stage, and publish."""
from copy import deepcopy
import csv
from dataclasses import asdict, dataclass, field
import io
import json
import os
from pathlib import Path
import tempfile

from pipeline_model import (
    ERROR, BatchInteractionUpdate, ContentModel, SourceTable, TABLE_FILES,
    ValidationIssue, build_content_model,
)
from rule_engine import RuleConfigError, check_config, load_config, validate_tables

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_RULES = ROOT_DIR / "ConfigSource" / "validation_rules.json"


@dataclass
class PipelineResult:
    issues: list[ValidationIssue] = field(default_factory=list)
    content: ContentModel | None = None
    updates: list[BatchInteractionUpdate] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)

    @property
    def ok(self):
        return not any(issue.level == ERROR for issue in self.issues)


class SourceError(ValueError):
    pass


def parse_csv_table(path):
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            headers = reader.fieldnames or []
            if not headers or any(not name.strip() for name in headers):
                raise SourceError(f"{path.name}: CSV header is missing or empty")
            if len(set(headers)) != len(headers):
                raise SourceError(f"{path.name}: duplicate CSV header")
            rows = []
            for number, row in enumerate(reader, 2):
                if None in row:
                    raise SourceError(f"{path.name} row {number}: unexpected extra column value(s)")
                if any(value is None for value in row.values()):
                    raise SourceError(f"{path.name} row {number}: mismatched column count")
                if any("\x00" in value for value in row.values()):
                    raise SourceError(f"{path.name} row {number}: NUL byte in CSV")
                rows.append(row)
        return SourceTable(path, headers, rows)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise SourceError(f"{path.name}: cannot parse CSV: {exc}") from exc


def atomic_write_many(payloads):
    """Stage every file before replacing any. Roll back earlier replacements on I/O failure.

    Each replacement is atomic; the set is not a crash-atomic filesystem transaction.
    """
    staged, originals, replaced = {}, {}, []
    try:
        for path, payload in payloads.items():
            path = Path(path)
            originals[path] = path.read_bytes() if path.exists() else None
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".",
                                             suffix=".tmp", delete=False) as stream:
                staged[path] = Path(stream.name)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        for path, temporary in staged.items():
            os.replace(temporary, path)
            replaced.append(path)
    except OSError:
        for path in reversed(replaced):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write_many({path: originals[path]})
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def json_bytes(data):
    # Match existing generated JSON, including no trailing newline.
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


class Pipeline:
    def __init__(self, root=ROOT_DIR, source_dir=None, output_dir=None, rules_path=None):
        self.root = Path(root).resolve()
        self.source_dir = Path(source_dir) if source_dir else self.root / "ConfigSource"
        self.output_dir = Path(output_dir) if output_dir else self.root / "Assets" / "Data"
        self.rules_path = Path(rules_path) if rules_path else self.root / "ConfigSource" / "validation_rules.json"

    def _rules(self, rules):
        return check_config(deepcopy(rules)) if rules is not None else load_config(self.rules_path)

    def _load(self, batch=False):
        tables, issues = {}, []
        for name, filename in TABLE_FILES.items():
            if name == "batch" and not batch:
                continue
            try:
                tables[name] = parse_csv_table(self.source_dir / filename)
            except SourceError as exc:
                issues.append(ValidationIssue(ERROR, str(exc), "parser.integrity", name))
        return tables, issues

    def headers(self):
        tables, _ = self._load(batch=True)
        return {name: table.fieldnames for name, table in tables.items()}

    def _validate(self, tables, rules, result):
        result.issues.extend(validate_tables(tables, rules, self.root))
        if result.ok:
            try:
                result.content = build_content_model(tables["items"], tables["objectives"],
                                                     tables["interactables"])
            except (KeyError, ValueError, TypeError, AttributeError) as exc:
                result.issues.append(ValidationIssue(
                    ERROR, f"Cannot convert to Unity JSON contract: {exc}", "contract.conversion"))
        return result

    def validate(self, rules=None):
        result = PipelineResult()
        try:
            rules = self._rules(rules)
        except RuleConfigError as exc:
            result.issues.append(ValidationIssue(ERROR, str(exc), "rules.config"))
            return result
        tables, result.issues = self._load()
        if result.ok:
            self._validate(tables, rules, result)
        return result

    def generate(self, rules=None):
        result = self.validate(rules)
        if not result.ok:
            return result
        content = result.content
        payloads = {
            self.output_dir / "interactables.json": json_bytes({
                "interactables": [asdict(value) for value in content.interactables]}),
            self.output_dir / "objectives.json": json_bytes({
                "objectives": [asdict(value) for value in content.objectives]}),
        }
        try:
            # Preserve the checked-in newline convention when publishing on another platform.
            for path, payload in payloads.items():
                newline = b"\r\n" if path.exists() and b"\r\n" in path.read_bytes() else b"\n"
                payloads[path] = payload.replace(b"\n", newline)
            atomic_write_many(payloads)
            result.written = list(payloads)
        except OSError as exc:
            result.issues.append(ValidationIssue(ERROR, f"JSON write failed: {exc}", "io.write"))
        return result

    def batch(self, rules=None, apply=False):
        result = PipelineResult()
        try:
            rules = self._rules(rules)
        except RuleConfigError as exc:
            result.issues.append(ValidationIssue(ERROR, str(exc), "rules.config"))
            return result
        tables, result.issues = self._load(batch=True)
        if not result.ok:
            return result
        result.issues.extend(validate_tables(tables, rules, self.root, only={"batch"}))
        if not result.ok:
            return result
        staged = deepcopy(tables)
        target_table = staged["interactables"]
        by_id = {}
        for row in target_table.rows:
            by_id.setdefault((row.get("id") or "").strip(), []).append(row)
        for number, row in enumerate(staged["batch"].rows, 2):
            target = (row.get("id") or "").strip()
            matches = by_id.get(target, [])
            # An operation must address exactly one row even if reference/unique rules are disabled.
            if len(matches) != 1:
                result.issues.append(ValidationIssue(ERROR, f"Batch target {target!r} is missing or ambiguous",
                                                     "batch.operation", "batch", number, "id"))
                continue
            source = matches[0]
            try:
                update = BatchInteractionUpdate(target, int(source["requiredInteractions"]),
                                                int(row["requiredInteractions"]))
            except (KeyError, ValueError, TypeError) as exc:
                result.issues.append(ValidationIssue(ERROR, f"Cannot stage batch integer: {exc}",
                                                     "batch.operation", "batch", number, "requiredInteractions"))
                continue
            source["requiredInteractions"] = row["requiredInteractions"].strip()
            result.updates.append(update)
        if not result.ok:
            return result
        # Content rules run against every staged row, including untouched rows and scene references.
        del staged["batch"]
        self._validate(staged, rules, result)
        if result.ok and apply:
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(stream, fieldnames=target_table.fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(target_table.rows)
            try:
                atomic_write_many({target_table.path: stream.getvalue().encode("utf-8")})
                result.written = [target_table.path]
            except OSError as exc:
                result.issues.append(ValidationIssue(ERROR, f"Batch write failed: {exc}", "io.write"))
        return result
