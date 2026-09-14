"""Standalone TD content tool CLI. Business logic is shared with the GUI."""
import argparse
from pathlib import Path

from pipeline_core import Pipeline, ROOT_DIR
from rule_engine import RuleConfigError, load_config


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="TD Pipeline content configuration tool.")
    parser.add_argument("command", nargs="?", default="generate",
                        choices=["generate", "validate", "rules-check", "batch-preview", "batch-apply", "gui"])
    parser.add_argument("--root", type=Path, default=ROOT_DIR, help="Project root (includes active Unity scene)")
    parser.add_argument("--source-dir", type=Path, help="CSV directory; defaults to ROOT/ConfigSource")
    parser.add_argument("--output-dir", type=Path, help="JSON output directory; defaults to ROOT/Assets/Data")
    parser.add_argument("--rules", type=Path, help="Rule config JSON; defaults to ROOT/ConfigSource/validation_rules.json")
    args = parser.parse_args(argv)
    pipeline = Pipeline(args.root, args.source_dir, args.output_dir, args.rules)
    if args.command == "gui":
        try:
            from config_gui import launch
            launch(pipeline)
        except (ImportError, RuntimeError, OSError, ValueError) as exc:
            print(f"[ERROR] Cannot open GUI: {exc}")
            return 1
        return 0
    if args.command == "rules-check":
        try:
            config = load_config(pipeline.rules_path)
        except RuleConfigError as exc:
            print(f"[ERROR] {exc}")
            return 1
        print(f"Rules: PASSED ({len(config['rules'])} rules)")
        return 0
    if args.command.startswith("batch-"):
        result = pipeline.batch(apply=args.command == "batch-apply")
    elif args.command == "validate":
        result = pipeline.validate()
    else:
        result = pipeline.generate()
    for issue in result.issues:
        location = ":".join(str(v) for v in (issue.table, issue.row, issue.field) if v not in (None, ""))
        print(f"[{issue.level}] {issue.rule_id} {location}: {issue.message}")
    for update in result.updates:
        print(f"[BATCH] {update.id}: requiredInteractions {update.oldRequiredInteractions} -> {update.newRequiredInteractions}")
    print(f"Validation: {'PASSED' if result.ok else 'FAILED'}")
    if result.content:
        print(f"Loaded {len(result.content.items)} item configs, {len(result.content.objectives)} objective configs, "
              f"{len(result.content.interactables)} interactable configs.")
    for path in result.written:
        print(f"Written: {path}")
    if args.command == "batch-preview":
        print("No source files were changed.")
    if not result.ok:
        print("Operation failed. Validation errors prevent publishing.")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(run_cli())
