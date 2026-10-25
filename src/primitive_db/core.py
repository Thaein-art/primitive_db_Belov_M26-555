import re

from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SELECT_CACHE = create_cacher()



def validate_identifier(value):

    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(
            f"Некорректное значение: {value}. Попробуйте снова."
        )


def require_table(metadata, table_name):

    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')


def _validate_type(value, expected_type):

    valid = (
        (expected_type == "int" and type(value) is int)
        or (expected_type == "str" and isinstance(value, str))
        or (expected_type == "bool" and type(value) is bool)
        or (expected_type == "float" and type(value) is float)
    )

    if not valid:
        raise ValueError(
            f"Некорректное значение: {value}. "
            f"Ожидается тип {expected_type}."
        )


def _matches(row, where_clause):

    return all(
        key in row and row[key] == value
        for key, value in where_clause.items()
    )


@handle_db_errors
def create_table(metadata, table_name, columns):

    validate_identifier(table_name)

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать хотя бы один столбец.")

    schema = {}

    for definition in columns:
        if definition.count(":") != 1:
            raise ValueError(
                f"Некорректное значение: {definition}. "
                "Ожидается формат имя:тип."
            )

        column_name, column_type = definition.split(":", 1)
        validate_identifier(column_name)

        if column_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректное значение: {definition}. "
                "Допустимые типы: int, str, bool."
            )

        if column_name == "ID":
            if column_type != "int" or "ID" in schema:
                raise ValueError("Столбец ID должен иметь тип int.")
            continue

        if column_name in schema:
            raise ValueError(
                f"Некорректное значение: повтор столбца {column_name}."
            )

        schema[column_name] = column_type

    metadata[table_name] = {"ID": "int", **schema}
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):

    validate_identifier(table_name)
    require_table(metadata, table_name)

    del metadata[table_name]
    return metadata


def list_tables(metadata):

    return sorted(metadata)


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data=None):
    require_table(metadata, table_name)

    if table_data is None:
        table_data = load_table_data(table_name)

    schema = metadata[table_name]
    columns = [name for name in schema if name != "ID"]

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидается {len(columns)} значений, "
            f"получено {len(values)}."
        )

    record = {}

    for column_name, value in zip(columns, values):
        _validate_type(value, schema[column_name])
        record[column_name] = value

    existing_ids = [
        row["ID"]
        for row in table_data
        if type(row.get("ID")) is int
    ]
    new_id = max(existing_ids, default=0) + 1

    table_data.append({"ID": new_id, **record})
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):

    if where_clause is None:
        where_clause = {}

    key = (repr(table_data), repr(where_clause))

    return SELECT_CACHE(
        key,
        lambda: [
            row.copy()
            for row in table_data
            if _matches(row, where_clause)
        ],
    )


@handle_db_errors
def update(table_data, set_clause, where_clause):

    if not set_clause:
        raise ValueError("Не указаны поля для обновления.")

    for row in table_data:
        if _matches(row, where_clause):
            row.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):

    table_data[:] = [
        row for row in table_data
        if not _matches(row, where_clause)
    ]

    return table_data
