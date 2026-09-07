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


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def print_issues(issues: list[ValidationIssue]) -> None:
    for issue in issues:
        print(f"[{issue.level}] {issue.message}")


def validate_schema(csv_path: Path) -> list[ValidationIssue]:    # 验证CSV文件的结构和必需字段
    issues = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:    # 检查CSV文件是否有表头
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{csv_path.name}: CSV header is missing."
                )
            )
            return issues

        for field in REQUIRED_FIELDS:    # 检查必需的字段是否存在于表头中
            if field not in reader.fieldnames:
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{csv_path.name}: missing required column '{field}'."
                    )
                )

        for row_number, row in enumerate(reader, start=2):
            for field in REQUIRED_FIELDS:    # 检查每一行的必需字段是否有值
                if field not in row:
                    continue

                value = row[field]

                if value is None or not value.strip():    # 检查字段值是否为空或仅包含空白字符
                    issues.append(
                        ValidationIssue(
                            ERROR,
                            f"{csv_path.name} row {row_number} "
                            f"field '{field}': value is required."
                        )
                    )

    return issues


def validate_values(csv_path: Path) -> list[ValidationIssue]:    #
    issues = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            required_interactions_raw = row["requiredInteractions"].strip()
            deactivate_raw = row["deactivateOnComplete"].strip().lower()

            try:
                required_interactions = int(required_interactions_raw)
            except ValueError:    # 检查'requiredInteractions'字段是否为整数
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{csv_path.name} row {row_number} "
                        f"field 'requiredInteractions': "
                        f"expected integer, got "
                        f"'{required_interactions_raw}'."
                    )
                )
            else:    # 检查'requiredInteractions'字段的值是否在有效范围内
                if required_interactions < MIN_REQUIRED_INTERACTIONS:    # 检查值是否小于最小值，若小于则添加错误信息
                    issues.append(
                        ValidationIssue(
                            ERROR,
                            f"{csv_path.name} row {row_number} "
                            f"field 'requiredInteractions': "
                            f"must be >= {MIN_REQUIRED_INTERACTIONS}, "
                            f"got {required_interactions}."
                        )
                    )

                elif required_interactions > RECOMMENDED_MAX_INTERACTIONS:    # 检查值是否大于推荐最大值，若大于则添加警告信息
                    issues.append(
                        ValidationIssue(
                            WARNING,
                            f"{csv_path.name} row {row_number} "
                            f"field 'requiredInteractions': "
                            f"value {required_interactions} is unusually high "
                            f"for the current interaction design."
                        )
                    )

            if deactivate_raw not in {"true", "false"}:    # 检查'deactivateOnComplete'字段的值是否为'true'或'false'
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{csv_path.name} row {row_number} "
                        f"field 'deactivateOnComplete': "
                        f"expected 'true' or 'false', "
                        f"got '{row['deactivateOnComplete']}'."
                    )
                )

    return issues


def validate_duplicate_ids(csv_path: Path) -> list[ValidationIssue]:
    issues = []
    seen_ids = set()

    # 检查CSV文件中是否有重复的'id'字段值
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            config_id = row["id"].strip()

            if config_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        ERROR,
                        f"{csv_path.name} row {row_number} "
                        f"field 'id': duplicate id '{config_id}'."
                    )
                )
            else:
                seen_ids.add(config_id)

    return issues


def validate_references(
    csv_path: Path,
    scene_path: Path,
) -> list[ValidationIssue]:
    issues = []

    valid_ids = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            valid_ids.add(row["id"].strip())

    if not scene_path.exists():    # 检查场景文件是否存在
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
        if "Assembly-CSharp::ConfigurableInteractable" not in block:    # 检查是否包含ConfigurableInteractable组件
            continue

        match = re.search(
            r"^[ \t]*configId:[ \t]*(.*?)[ \t]*$",    # 匹配configId字段的正则表达式，形如 "configId: some_id"
            block,
            re.MULTILINE,
        )

        if match is None:    # 检查是否匹配到configId字段
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable is missing 'configId'."
                )
            )
            continue

        config_id = match.group(1).strip()

        if not config_id:    # 检查configId字段是否为空
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable has an empty 'configId'."
                )
            )
            continue

        if config_id not in valid_ids:    # 检查configId字段的值是否在有效的id集合中
            issues.append(
                ValidationIssue(
                    ERROR,
                    f"{scene_path.name}: "
                    f"ConfigurableInteractable references unknown "
                    f"config id '{config_id}'."
                )
            )

    return issues


def load_configs(csv_path: Path) -> list[InteractableConfig]:
    configs = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            config = InteractableConfig(
                id=row["id"].strip(),
                displayName=row["displayName"].strip(),
                interactionType=row["interactionType"].strip(),
                requiredInteractions=int(row["requiredInteractions"]),
                requiredItemId=row.get("requiredItemId", "").strip(),
                grantedItemId=row.get("grantedItemId", "").strip(),
                blockedMessage=row.get("blockedMessage", "").strip(),
                completionMessage=row.get("completionMessage", "").strip(),
                deactivateOnComplete=parse_bool(
                    row["deactivateOnComplete"]
                ),
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
    issues = validate_schema(SOURCE_PATH)

    if not any(issue.level == ERROR for issue in issues):
        issues.extend(validate_values(SOURCE_PATH))
        issues.extend(validate_duplicate_ids(SOURCE_PATH))
        issues.extend(
            validate_references(
                SOURCE_PATH,
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

    configs = load_configs(SOURCE_PATH)
    write_json(configs, OUTPUT_PATH)

    print(f"Loaded {len(configs)} interactable configs.")
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()