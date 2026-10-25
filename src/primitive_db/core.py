
import re
import time
from functools import wraps

SUPPORTED_TYPES = {'int', 'str', 'bool', 'float'}
IDENTIFIER_PATTER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class InvalidValueError(Exception):
    """Ошибка при некорректном значении команды."""

    def __init__(self, value):
        self.value = value
        super().__init__(str(value))


class TableAlreadyExistsError(Exception):
    """Попытка создать уже существующую таблицу."""


class TableNotFoundError(Exception):
    """Обращение к несуществующей таблице."""


def validate_identifier(value):
    """Проверяет имя таблицы или столбца."""
    if not IDENTIFIER_PATTER.fullmatch(value):
        raise InvalidValueError(value)


def create_table(metadata, table_name, columns):
    """Создаёт таблицу и возвращает обновлённые метаданные."""
    validate_identifier(table_name)

    if table_name in metadata:
        raise TableAlreadyExistsError(table_name)

    schema = {}

    for definition in columns:
        if definition.count(":") != 1:
            raise InvalidValueError(definition)

        column_name, column_type = definition.split(":", 1)

        if not IDENTIFIER_PATTER.fullmatch(column_name):
            raise InvalidValueError(definition)

        if column_type not in SUPPORTED_TYPES:
            raise InvalidValueError(definition)

        if column_name == "ID":
            if column_type != "int" or "ID" in schema:
                raise InvalidValueError(definition)
            continue

        if column_name in schema:
            raise InvalidValueError(definition)

        schema[column_name] = column_type

    metadata[table_name] = {"ID": "int", **schema}

    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    validate_identifier(table_name)

    if table_name not in metadata:
        raise TableNotFoundError(table_name)

    metadata[table_name] = {}

    return metadata[table_name]


def list_tables(metadata):
    """Возвращает отсортированный список имён таблиц."""
    return sorted(metadata.keys())



def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением функции."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить '
                f'"{action_name}"? [y/n]: '
            ).strip().lower()

            if answer != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(
                f"Функция {func.__name__} "
                f"выполнилась за {elapsed:.4f} секунд."
            )

    return wrapper


def create_cacher():
    """Создаёт кэш с помощью замыкания."""

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
