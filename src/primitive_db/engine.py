


import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_assignments,
    parse_condition,
    parse_delete_command,
    parse_insert_command,
    parse_insert_values,
    parse_select_command,
    parse_update_command,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "insert into <таблица> values (<значения>) "
        "- добавить запись"
    )
    print(
        "select from <таблица> [where <столбец> = <значение>] "
        "- прочитать записи"
    )
    print(
        "update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить запись"
    )
    print(
        "delete from <таблица> where <столбец> = <значение> "
        "- удалить запись"
    )
    print("info <таблица> - информация о таблице")
    print("create_table <таблица> <столбец:тип> ...")
    print("list_tables - список таблиц")
    print("drop_table <таблица> - удалить таблицу")
    print("help - справка")
    print("exit - завершить программу\n")


def table_exists(metadata, table_name):

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False

    return True


def print_rows(rows, schema):
  
    table = PrettyTable()
    table.field_names = list(schema)

    for row in rows:
        table.add_row([row.get(column) for column in schema])

    print(table)


def handle_create_table(metadata, args, metadata_path):
    """Handle the create_table command."""
    if len(args) < 2:
        print("Использование: create_table <таблица> <столбец:тип> ...")
        return

    table_name = args[0]
    updated_metadata = create_table(
        metadata,
        table_name,
        args[1:],
    )

    if updated_metadata is None:
        return

    save_metadata(metadata_path, updated_metadata)
    save_table_data(table_name, [])

    schema = updated_metadata[table_name]
    columns_text = ", ".join(
        f"{name}:{column_type}"
        for name, column_type in schema.items()
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_text}"
    )


def handle_drop_table(metadata, args, metadata_path):

    if len(args) != 1:
        print("Использование: drop_table <таблица>")
        return

    table_name = args[0]
    updated_metadata = drop_table(metadata, table_name)

    if updated_metadata is None:
        return

    save_metadata(metadata_path, updated_metadata)
    delete_table_data(table_name)
    print(f'Таблица "{table_name}" успешно удалена.')


def handle_insert(command_text, metadata):

    table_name, raw_values = parse_insert_command(command_text)

    if not table_exists(metadata, table_name):
        return

    table_data = load_table_data(table_name)
    values = parse_insert_values(
        raw_values,
        metadata[table_name],
    )

    updated_data = insert(
        metadata,
        table_name,
        values,
        table_data,
    )

    if updated_data is None:
        return

    save_table_data(table_name, updated_data)
    record_id = updated_data[-1]["ID"]

    print(
        f'Запись с ID={record_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )


def handle_select(command_text, metadata):
  
    table_name, raw_condition = parse_select_command(command_text)

    if not table_exists(metadata, table_name):
        return

    schema = metadata[table_name]
    condition = None

    if raw_condition is not None:
        condition = parse_condition(raw_condition, schema)

    table_data = load_table_data(table_name)
    rows = select(table_data, condition)

    if rows is not None:
        print_rows(rows, schema)


def handle_update(command_text, metadata):

    table_name, raw_set, raw_condition = parse_update_command(
        command_text
    )

    if not table_exists(metadata, table_name):
        return

    schema = metadata[table_name]
    set_clause = parse_assignments(raw_set, schema)
    where_clause = parse_condition(raw_condition, schema)

    table_data = load_table_data(table_name)
    matched_ids = [
        row["ID"]
        for row in table_data
        if all(
            key in row and row[key] == value
            for key, value in where_clause.items()
        )
    ]

    updated_data = update(
        table_data,
        set_clause,
        where_clause,
    )

    if updated_data is None:
        return

    save_table_data(table_name, updated_data)

    if matched_ids:
        for record_id in matched_ids:
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" '
                "успешно обновлена."
            )
    else:
        print("Записей, соответствующих условию, не найдено.")


def handle_delete(command_text, metadata):

    table_name, raw_condition = parse_delete_command(command_text)

    if not table_exists(metadata, table_name):
        return

    schema = metadata[table_name]
    where_clause = parse_condition(raw_condition, schema)
    table_data = load_table_data(table_name)

    matched_ids = [
        row["ID"]
        for row in table_data
        if all(
            key in row and row[key] == value
            for key, value in where_clause.items()
        )
    ]

    updated_data = delete(table_data, where_clause)

    # None means that the confirmation was declined or an error occurred.
    if updated_data is None:
        return

    save_table_data(table_name, updated_data)

    if matched_ids:
        for record_id in matched_ids:
            print(
                f'Запись с ID={record_id} успешно удалена '
                f'из таблицы "{table_name}".'
            )
    else:
        print("Записей, соответствующих условию, не найдено.")


def handle_info(command_text, metadata):

    try:
        args = shlex.split(command_text)
    except ValueError:
        print("Некорректная команда info.")
        return

    if len(args) != 2:
        print("Использование: info <таблица>")
        return

    table_name = args[1]

    if not table_exists(metadata, table_name):
        return

    schema = metadata[table_name]
    rows = load_table_data(table_name)
    columns_text = ", ".join(
        f"{name}:{column_type}"
        for name, column_type in schema.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {len(rows)}")


def run():

    metadata_path = Path.cwd() / META_FILE
    print_help()

    while True:
        metadata = load_metadata(metadata_path)
        user_input = prompt.string("Введите команду: ").strip()

        if not user_input:
            continue

        command = user_input.split(maxsplit=1)[0].lower()

        try:
            if command == "create_table":
                args = shlex.split(user_input)[1:]
                handle_create_table(
                    metadata,
                    args,
                    metadata_path,
                )

            elif command == "drop_table":
                args = shlex.split(user_input)[1:]
                handle_drop_table(
                    metadata,
                    args,
                    metadata_path,
                )

            elif command == "list_tables":
                if len(shlex.split(user_input)) != 1:
                    print("Использование: list_tables")
                    continue

                tables = list_tables(metadata)
                if tables:
                    for table_name in tables:
                        print(f"- {table_name}")
                else:
                    print("Таблиц пока нет.")

            elif command == "insert":
                handle_insert(user_input, metadata)

            elif command == "select":
                handle_select(user_input, metadata)

            elif command == "update":
                handle_update(user_input, metadata)

            elif command == "delete":
                handle_delete(user_input, metadata)

            elif command == "info":
                handle_info(user_input, metadata)

            elif command == "help":
                print_help()

            elif command == "exit":
                print("Выход из программы.")
                return

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except ValueError as error:
            print(str(error))

