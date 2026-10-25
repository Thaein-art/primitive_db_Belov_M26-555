
import shlex
from pathlib import Path

import prompt

from primitive_db.core import (
    InvalidValueError,
    TableAlreadyExistsError,
    TableNotFoundError,
    create_table,
    drop_table,
    list_tables,
)
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_invalid_value(value):
    """Печатает сообщение о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def run():
    """Запускает основной цикл базы данных."""
    metadata_path = Path.cwd() / "db_meta.json"

    print_help()

    while True:
        # Перечитываем актуальные данные при каждой итерации.
        metadata = load_metadata(metadata_path)

        user_input = prompt.string("Введите команду: ").strip()

        try:
            args = shlex.split(user_input)
        except ValueError:
            print_invalid_value(user_input)
            continue

        if not args:
            continue

        command = args[0].lower()
        command_args = args[1:]

        if command == "create_table":
            if not command_args:
                print_invalid_value("<имя_таблицы>")
                continue

            table_name = command_args[0]
            columns = command_args[1:]

            try:
                metadata = create_table(
                    metadata,
                    table_name,
                    columns,
                )
            except TableAlreadyExistsError:
                print(f'Ошибка: Таблица "{table_name}" уже существует.')
            except InvalidValueError as error:
                print_invalid_value(error.value)
            else:
                save_metadata(metadata_path, metadata)

                schema = metadata[table_name]
                columns_text = ", ".join(
                    f"{name}:{column_type}"
                    for name, column_type in schema.items()
                )

                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {columns_text}"
                )

        elif command == "list_tables":
            if command_args:
                print_invalid_value(" ".join(command_args))
                continue

            tables = list_tables(metadata)

            if tables:
                for table_name in tables:
                    print(f"- {table_name}")
            else:
                print("Таблиц пока нет.")

        elif command == "drop_table":
            if len(command_args) != 1:
                value = (
                    " ".join(command_args)
                    if command_args
                    else "<имя_таблицы>"
                )
                print_invalid_value(value)
                continue

            table_name = command_args[0]

            try:
                metadata = drop_table(metadata, table_name)
            except TableNotFoundError:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
            except InvalidValueError as error:
                print_invalid_value(error.value)
            else:
                save_metadata(metadata_path, metadata)
                print(f'Таблица "{table_name}" успешно удалена.')

        elif command == "help":
            if command_args:
                print_invalid_value(" ".join(command_args))
                continue

            print_help()

        elif command == "exit":
            if command_args:
                print_invalid_value(" ".join(command_args))
                continue

            print("Выход из программы.")
            return

        else:
            print(f"Функции {command} нет. Попробуйте снова.")

