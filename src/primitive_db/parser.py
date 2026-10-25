
"""Parsers for database commands and typed values."""

import json
import re

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _invalid(value):
    """Raise a consistent error for invalid command values."""
    raise ValueError(
        f"Некорректное значение: {value}. Попробуйте снова."
    )


def split_comma_values(text):

    if not text.strip():
        return []

    values = []
    current = []
    in_quotes = False
    escaped = False

    for char in text:
        if in_quotes:
            current.append(char)

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_quotes = False
        elif char == '"':
            in_quotes = True
            current.append(char)
        elif char == ",":
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if in_quotes:
        _invalid(text)

    values.append("".join(current).strip())

    if any(not value for value in values):
        _invalid(text)

    return values


def split_assignment(text):

    in_quotes = False
    escaped = False

    for index, char in enumerate(text):
        if in_quotes:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_quotes = False
        elif char == '"':
            in_quotes = True
        elif char == "=":
            column = text[:index].strip()
            value = text[index + 1:].strip()

            if not column or not value:
                _invalid(text)

            return column, value

    _invalid(text)


def parse_value(raw_value, expected_type):

    value = raw_value.strip()

    if expected_type == "str":
        if not (value.startswith('"') and value.endswith('"')):
            _invalid(value)

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            _invalid(value)

        if not isinstance(parsed, str):
            _invalid(value)

        return parsed

    if expected_type == "int":
        if not re.fullmatch(r"[+-]?\d+", value):
            _invalid(value)

        return int(value)

    if expected_type == "bool":
        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        _invalid(value)

    _invalid(value)


def parse_insert_command(command_text):

    match = re.fullmatch(
        r"insert\s+into\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"\s+values\s*\((.*)\)\s*",
        command_text,
        flags=re.IGNORECASE,
    )

    if not match:
        _invalid(command_text)

    table_name, raw_values = match.groups()
    return table_name, split_comma_values(raw_values)


def parse_insert_values(raw_values, schema):

    columns = [name for name in schema if name != "ID"]

    if len(raw_values) != len(columns):
        raise ValueError(
            f"Ожидается {len(columns)} значений, "
            f"получено {len(raw_values)}."
        )

    return [
        parse_value(raw_value, schema[column_name])
        for column_name, raw_value in zip(columns, raw_values)
    ]


def parse_condition(text, schema):

    column_name, raw_value = split_assignment(text)

    if column_name not in schema:
        _invalid(column_name)

    return {
        column_name: parse_value(raw_value, schema[column_name])
    }


def parse_select_command(command_text):

    match = re.fullmatch(
        r"select\s+from\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s+where\s+(.+))?",
        command_text,
        flags=re.IGNORECASE,
    )

    if not match:
        _invalid(command_text)

    return match.group(1), match.group(2)


def parse_update_command(command_text):

    match = re.fullmatch(
        r"update\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"\s+set\s+(.+?)\s+where\s+(.+)",
        command_text,
        flags=re.IGNORECASE,
    )

    if not match:
        _invalid(command_text)

    return match.group(1), match.group(2), match.group(3)


def parse_assignments(text, schema):

    assignments = {}

    for item in split_comma_values(text):
        column_name, raw_value = split_assignment(item)

        if column_name not in schema:
            _invalid(column_name)

        if column_name == "ID":
            raise ValueError("Изменять поле ID запрещено.")

        if column_name in assignments:
            _invalid(column_name)

        assignments[column_name] = parse_value(
            raw_value,
            schema[column_name],
        )

    if not assignments:
        _invalid(text)

    return assignments


def parse_delete_command(command_text):
    """Parse a DELETE command with a WHERE condition."""
    match = re.fullmatch(
        r"delete\s+from\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"\s+where\s+(.+)",
        command_text,
        flags=re.IGNORECASE,
    )

    if not match:
        _invalid(command_text)

    return match.group(1), match.group(2)
