
import json
from pathlib import Path


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with Path(filepath).open("r", encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}

    if not isinstance(metadata, dict):
        return {}

    return metadata


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with Path(filepath).open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
        )
