from pathlib import Path
import csv
import json
from dataclasses import dataclass, asdict


@dataclass
class InteractableConfig:
    id: str
    displayName: str
    requiredInteractions: int
    deactivateOnComplete: bool


ROOT_DIR = Path(__file__).resolve().parent.parent

SOURCE_PATH = ROOT_DIR / "ConfigSource" / "interactables.csv"
OUTPUT_PATH = ROOT_DIR / "Assets" / "Data" / "interactables.json"


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_configs(csv_path: Path) -> list[InteractableConfig]:
    configs = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            config = InteractableConfig(
                id=row["id"],
                displayName=row["displayName"],
                requiredInteractions=int(row["requiredInteractions"]),
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
    configs = load_configs(SOURCE_PATH)
    write_json(configs, OUTPUT_PATH)

    print(f"Loaded {len(configs)} interactable configs.")
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()