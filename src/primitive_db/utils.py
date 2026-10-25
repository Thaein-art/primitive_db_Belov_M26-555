
"""Helpers for loading and saving database files."""

import json
from pathlib import Path

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Load table schemas from a JSON file."""
    try:
        with Path(filepath).open("r", encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}

    if not isinstance(metadata, dict):
        raise ValueError("Файл метаданных должен содержать JSON-объект.")

    return metadata


def save_metadata(filepath, data):
    """Save table schemas to a JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_data_path(table_name):
    """Return the path to a table's JSON data file."""
    return Path.cwd() / DATA_DIR / f"{table_name}.json"


def load_table_data(table_name):
    """Load rows for a table, returning an empty list if absent."""
    path = get_table_data_path(table_name)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise ValueError(
            f"Файл данных таблицы '{table_name}' должен содержать список."
        )

    return data


def save_table_data(table_name, data):
    """Save rows for a table to its JSON file."""
    path = get_table_data_path(table_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Remove a table's data file if it exists."""
    path = get_table_data_path(table_name)

    if path.exists():
        path.unlink()
