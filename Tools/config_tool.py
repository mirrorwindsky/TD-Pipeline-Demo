from pathlib import Path
import csv
import json
from dataclasses import dataclass, asdict
import re


@dataclass
class ItemConfig:
    id: str
    displayName: str


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
class ContentModel:
    items: list[ItemConfig]
    interactables: list[InteractableConfig]


@dataclass
class BatchInteractionUpdate:
    id: str
    oldRequiredInteractions: int
    newRequiredInteractions: int


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

ITEM_REQUIRED_FIELDS = [
    "id",
    "displayName",
]

INTERACTABLE_REQUIRED_FIELDS = [
    "id",
    "displayName",
    "interactionType",
    "requiredInteractions",
    "deactivateOnComplete",
]

BATCH_UPDATE_REQUIRED_FIELDS = [
    "id",
    "requiredInteractions",
]

MIN_REQUIRED_INTERACTIONS = 1
RECOMMENDED_MAX_INTERACTIONS = 10

VALID_INTERACTION_TYPES = {
    "Pickup",
    "Device",
}

ITEMS_SOURCE_PATH = ROOT_DIR / "ConfigSource" / "items.csv"
INTERACTABLES_SOURCE_PATH = ROOT_DIR / "ConfigSource" / "interactables.csv"
OUTPUT_PATH = ROOT_DIR / "Assets" / "Data" / "interactables.json"
SCENE_PATH = ROOT_DIR / "Assets" / "Scenes" / "Prototype_01.unity"
BATCH_UPDATE_PATH = ROOT_DIR / "ConfigSource" / "batch_interaction_updates.csv"


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


def validate_schema(
    table: SourceTable,
    required_fields: list[str],
) -> list[ValidationIssue]:
    issues = []

    if not table.fieldnames:
        issues.append(
            ValidationIssue(
                ERROR,
                f"{table.path.name}: CSV header is missing."
            )
        )
        return issues

    for field in required_fields:
        if field not in table.fieldnames:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name}: missing required column '{field}'."
                )
            )

    for row_number, row in enumerate(table.rows, start=2):
        for field in required_fields:
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


def validate_interaction_types(
    table: SourceTable,
) -> list[ValidationIssue]:
    issues = []

    for row_number, row in enumerate(table.rows, start=2):
        interaction_type = (row.get("interactionType") or "").strip()

        if not interaction_type:
            continue

        if interaction_type not in VALID_INTERACTION_TYPES:
            valid_values = ", ".join(sorted(VALID_INTERACTION_TYPES))

            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{table.path.name} row {row_number} "
                    f"field 'interactionType': "
                    f"unknown value '{interaction_type}'. "
                    f"Expected one of: {valid_values}."
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


def validate_item_references(
    content: ContentModel,
    source_path: Path,
) -> list[ValidationIssue]:
    issues = []

    valid_item_ids = {
        item.id
        for item in content.items
    }

    for row_number, config in enumerate(
        content.interactables,
        start=2,
    ):
        references = [
            ("requiredItemId", config.requiredItemId),
            ("grantedItemId", config.grantedItemId),
        ]

        for field_name, item_id in references:
            if not item_id:
                continue

            if item_id not in valid_item_ids:
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{source_path.name} row {row_number} "
                        f"field '{field_name}': "
                        f"unknown item id '{item_id}'."
                    )
                )

    return issues


def prepare_batch_interaction_updates(
    update_table: SourceTable,
    content: ContentModel,
) -> tuple[list[BatchInteractionUpdate], list[ValidationIssue]]:
    updates = []
    issues = []

    interactable_by_id = {
        config.id: config
        for config in content.interactables
    }

    for row_number, row in enumerate(update_table.rows, start=2):
        config_id = row["id"].strip()
        value_raw = row["requiredInteractions"].strip()

        if config_id not in interactable_by_id:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{update_table.path.name} row {row_number} "
                    f"field 'id': unknown interactable id '{config_id}'."
                )
            )
            continue

        try:
            new_value = int(value_raw)
        except ValueError:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{update_table.path.name} row {row_number} "
                    f"field 'requiredInteractions': "
                    f"expected integer, got '{value_raw}'."
                )
            )
            continue

        if new_value < MIN_REQUIRED_INTERACTIONS:
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{update_table.path.name} row {row_number} "
                    f"field 'requiredInteractions': "
                    f"must be >= {MIN_REQUIRED_INTERACTIONS}, "
                    f"got {new_value}."
                )
            )
            continue

        config = interactable_by_id[config_id]

        updates.append(
            BatchInteractionUpdate(
                id=config_id,
                oldRequiredInteractions=config.requiredInteractions,
                newRequiredInteractions=new_value,
            )
        )

    return updates, issues


def print_batch_preview(
    updates: list[BatchInteractionUpdate],
) -> None:
    for update in updates:
        print(
            f"[BATCH] {update.id}: "
            f"requiredInteractions "
            f"{update.oldRequiredInteractions} "
            f"-> {update.newRequiredInteractions}"
        )


def load_items(table: SourceTable) -> list[ItemConfig]:
    items = []

    for row in table.rows:
        item = ItemConfig(
            id=row["id"].strip(),
            displayName=row["displayName"].strip(),
        )

        items.append(item)

    return items


def load_interactables(table: SourceTable) -> list[InteractableConfig]:
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


def build_content_model(
    item_table: SourceTable,
    interactable_table: SourceTable,
) -> ContentModel:
    return ContentModel(
        items=load_items(item_table),
        interactables=load_interactables(interactable_table),
    )


def write_json(
    content: ContentModel,
    output_path: Path,
) -> None:
    data = {
        "interactables": [
            asdict(config)
            for config in content.interactables
        ]
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def run_batch_preview():
    update_table = parse_csv_table(BATCH_UPDATE_PATH)
    interactable_table = parse_csv_table(INTERACTABLES_SOURCE_PATH)

    issues = validate_schema(
        update_table,
        BATCH_UPDATE_REQUIRED_FIELDS,
    )

    if not any(issue.level == ERROR for issue in issues):
        issues.extend(validate_duplicate_ids(update_table))

    if any(issue.level == ERROR for issue in issues):
        print_issues(issues)
        print("Batch preview failed. No changes were made.")
        return

    item_table = parse_csv_table(ITEMS_SOURCE_PATH)

    content = build_content_model(
        item_table,
        interactable_table,
    )

    updates, batch_issues = prepare_batch_interaction_updates(
        update_table,
        content,
    )

    issues.extend(batch_issues)

    if any(issue.level == ERROR for issue in issues):
        print_issues(issues)
        print("Batch preview failed. No changes were made.")
        return

    print_batch_preview(updates)


def main():
    item_table = parse_csv_table(ITEMS_SOURCE_PATH)
    interactable_table = parse_csv_table(INTERACTABLES_SOURCE_PATH)

    issues = []

    item_schema_issues = validate_schema(
        item_table,
        ITEM_REQUIRED_FIELDS,
    )
    interactable_schema_issues = validate_schema(
        interactable_table,
        INTERACTABLE_REQUIRED_FIELDS,
    )

    issues.extend(item_schema_issues)
    issues.extend(interactable_schema_issues)

    if not any(issue.level == ERROR for issue in item_schema_issues):
        issues.extend(validate_duplicate_ids(item_table))

    if not any(issue.level == ERROR for issue in interactable_schema_issues):
        issues.extend(validate_values(interactable_table))
        issues.extend(validate_interaction_types(interactable_table))
        issues.extend(validate_duplicate_ids(interactable_table))
        issues.extend(
            validate_references(
                interactable_table,
                SCENE_PATH,
            )
        )

    if any(issue.level == ERROR for issue in issues):
        print_issues(issues)
        print("Validation failed. JSON was not generated.")
        return

    content = build_content_model(
        item_table,
        interactable_table,
    )

    issues.extend(
        validate_item_references(
            content,
            INTERACTABLES_SOURCE_PATH,
        )
    )

    print_issues(issues)

    if any(issue.level == ERROR for issue in issues):
        print("Validation failed. JSON was not generated.")
        return

    write_json(content, OUTPUT_PATH)

    print(f"Loaded {len(content.items)} item configs.")
    print(
        f"Loaded {len(content.interactables)} "
        f"interactable configs."
    )
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()