"""Shared raw tables, typed Unity contract, and structured diagnostics."""
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ItemConfig:
    id: str
    displayName: str


@dataclass
class ObjectiveConfig:
    id: str
    displayName: str
    description: str


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
    objectives: list[ObjectiveConfig]
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
    rule_id: str = ""
    table: str = ""
    row: int | None = None
    field: str = ""


@dataclass
class SourceTable:
    path: Path
    fieldnames: list[str]
    rows: list[dict[str, str | None]]


ERROR = "ERROR"
WARNING = "WARNING"

# These headers describe the existing transport contract, not project validation policy.
TABLE_HEADERS = {
    "items": ["id", "displayName"],
    "objectives": ["id", "displayName", "description"],
    "interactables": [
        "id", "displayName", "interactionType", "requiredInteractions",
        "requiredItemId", "grantedItemId", "blockedMessage",
        "completionMessage", "deactivateOnComplete",
    ],
    "batch": ["id", "requiredInteractions"],
}
TABLE_FILES = {name: name + ".csv" for name in TABLE_HEADERS}
TABLE_FILES["batch"] = "batch_interaction_updates.csv"


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError("Unity boolean must be true or false")
    return normalized == "true"


def unity_int(value: str) -> int:
    number = int(value)
    if not -(2 ** 31) <= number < 2 ** 31:
        raise ValueError("Unity integer must fit Int32")
    return number


def load_items(table: SourceTable) -> list[ItemConfig]:
    items = []

    for row in table.rows:
        item = ItemConfig(
            id=row["id"].strip(),
            displayName=row["displayName"].strip(),
        )

        items.append(item)

    return items


def load_objectives(table: SourceTable) -> list[ObjectiveConfig]:
    objectives = []

    for row in table.rows:
        objective = ObjectiveConfig(
            id=row["id"].strip(),
            displayName=row["displayName"].strip(),
            description=row["description"].strip(),
        )

        objectives.append(objective)

    return objectives


def load_interactables(table: SourceTable) -> list[InteractableConfig]:
    configs = []

    for row in table.rows:
        config = InteractableConfig(
            id=row["id"].strip(),
            displayName=row["displayName"].strip(),
            interactionType=row["interactionType"].strip(),
            requiredInteractions=unity_int(row["requiredInteractions"]),
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
    objective_table: SourceTable,
    interactable_table: SourceTable,
) -> ContentModel:
    return ContentModel(
        items=load_items(item_table),
        objectives=load_objectives(objective_table),
        interactables=load_interactables(interactable_table),
    )


