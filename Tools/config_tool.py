from pathlib import Path
import csv
import json
from dataclasses import dataclass, asdict
import re


@dataclass
class InteractableConfig:
    id: str
    displayName: str
    interactionType: str
    requiredInteractions: int
    requiredItemId: str
    grantedItemId: str
    blockedMessage: str
    completionMessage: str
    deactivateOnComplete: bool


@dataclass
class ValidationIssue:
    level: str
    message: str


@dataclass
class SourceTable:
    path: Path
    fieldnames: list[str]
    rows: list[dict[str, str | None]]


ERROR = "ERROR"
WARNING = "WARNING"

ROOT_DIR = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = [
    "id",
    "displayName",
    "interactionType",
    "requiredInteractions",
    "deactivateOnComplete",
]

MIN_REQUIRED_INTERACTIONS = 1
RECOMMENDED_MAX_INTERACTIONS = 10

SOURCE_PATH = ROOT_DIR / "ConfigSource" / "interactables.csv"
OUTPUT_PATH = ROOT_DIR / "Assets" / "Data" / "interactables.json"
SCENE_PATH = ROOT_DIR / "Assets" / "Scenes" / "Prototype_01.unity"


def parse_csv_table(csv_path: Path) -> SourceTable:
    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames or []
        rows = list(reader)

    return SourceTable(
        path=csv_path,
        fieldnames=fieldnames,
        rows=rows,
    )


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def print_issues(issues: list[ValidationIssue]) -> None:
    for issue in issues:
        print(f"[{issue.level}] {issue.message}")


def validate_schema(table: SourceTable) -> list[ValidationIssue]:
    issues = []

    if not table.fieldnames:
        issues.append(
            ValidationIssue(
                ERROR,
                f"{table.path.name}: CSV header is missing."
            )
        )
        return issues

    for field in REQUIRED_FIELDS:
        if field not in table.fieldnames:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name}: missing required column '{field}'."
                )
            )

    for row_number, row in enumerate(table.rows, start=2):
        for field in REQUIRED_FIELDS:
            if field not in row:
                continue

            value = row[field]

            if value is None or not value.strip():
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{table.path.name} row {row_number} "
                        f"field '{field}': value is required."
                    )
                )

    return issues


def validate_values(table: SourceTable) -> list[ValidationIssue]:
    issues = []

    for row_number, row in enumerate(table.rows, start=2):
        required_interactions_raw = row["requiredInteractions"].strip()
        deactivate_raw = row["deactivateOnComplete"].strip().lower()

        try:
            required_interactions = int(required_interactions_raw)
        except ValueError:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name} row {row_number} "
                    f"field 'requiredInteractions': "
                    f"expected integer, got '{required_interactions_raw}'."
                )
            )
        else:
            if required_interactions < MIN_REQUIRED_INTERACTIONS:
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{table.path.name} row {row_number} "
                        f"field 'requiredInteractions': "
                        f"must be >= {MIN_REQUIRED_INTERACTIONS}, "
                        f"got {required_interactions}."
                    )
                )

            elif required_interactions > RECOMMENDED_MAX_INTERACTIONS:
                issues.append(
                    ValidationIssue(
                        WARNING,
                        f"{table.path.name} row {row_number} "
                        f"field 'requiredInteractions': "
                        f"value {required_interactions} is unusually high "
                        f"for the current interaction design."
                    )
                )

        if deactivate_raw not in {"true", "false"}:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name} row {row_number} "
                    f"field 'deactivateOnComplete': "
                    f"expected 'true' or 'false', "
                    f"got '{row['deactivateOnComplete']}'."
                )
            )

    return issues


def validate_duplicate_ids(table: SourceTable) -> list[ValidationIssue]:
    issues = []
    seen_ids = set()

    for row_number, row in enumerate(table.rows, start=2):
        config_id = row["id"].strip()

        if config_id in seen_ids:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name} row {row_number} "
                    f"field 'id': duplicate id '{config_id}'."
                )
            )
        else:
            seen_ids.add(config_id)

    return issues


def validate_references(
    table: SourceTable,
    scene_path: Path,
) -> list[ValidationIssue]:
    issues = []

    valid_ids = {
        row["id"].strip()
        for row in table.rows
    }

    if not scene_path.exists():
        issues.append(
            ValidationIssue(
                ERROR,
                f"{scene_path.name}: scene file not found."
            )
        )
        return issues

    scene_text = scene_path.read_text(encoding="utf-8")

    component_blocks = scene_text.split("--- !u!114")

    for block in component_blocks:
        if "Assembly-CSharp::ConfigurableInteractable" not in block:
            continue

        match = re.search(
            r"^[ \t]*configId:[ \t]*(.*?)[ \t]*$",
            block,
            re.MULTILINE,
        )

        if match is None:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable is missing 'configId'."
                )
            )
            continue

        config_id = match.group(1).strip()

        if not config_id:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable has an empty 'configId'."
                )
            )
            continue

        if config_id not in valid_ids:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable references unknown "
                    f"config id '{config_id}'."
                )
            )

    return issues


def load_configs(table: SourceTable) -> list[InteractableConfig]:
    configs = []

    for row in table.rows:
        config = InteractableConfig(
            id=row["id"].strip(),
            displayName=row["displayName"].strip(),
            interactionType=row["interactionType"].strip(),
            requiredInteractions=int(row["requiredInteractions"]),
            requiredItemId=(row.get("requiredItemId") or "").strip(),
            grantedItemId=(row.get("grantedItemId") or "").strip(),
            blockedMessage=(row.get("blockedMessage") or "").strip(),
            completionMessage=(row.get("completionMessage") or "").strip(),
            deactivateOnComplete=parse_bool(row["deactivateOnComplete"]),
        )

        configs.append(config)

    return configs


def write_json(
    configs: list[InteractableConfig],
    output_path: Path,
) -> None:
    data = {
        "interactables": [
            asdict(config)
            for config in configs
        ]
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main():
    interactable_table = parse_csv_table(SOURCE_PATH)

    issues = validate_schema(interactable_table)

    if not any(issue.level == ERROR for issue in issues):
        issues.extend(validate_values(interactable_table))
        issues.extend(validate_duplicate_ids(interactable_table))
        issues.extend(
            validate_references(
                interactable_table,
                SCENE_PATH,
            )
        )

    print_issues(issues)

    has_errors = any(
        issue.level == ERROR
        for issue in issues
    )

    if has_errors:
        print("Validation failed. JSON was not generated.")
        return

    configs = load_configs(interactable_table)
    write_json(configs, OUTPUT_PATH)

    print(f"Loaded {len(configs)} interactable configs.")
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()