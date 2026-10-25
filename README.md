# primitive_db


Программа `primitive_db` — консольная база данных,
которая хранит метаданные таблиц в JSON-файле.
=======
Учебная консольная база данных на Python.
Схемы таблиц и записи хранятся в JSON-файлах.


## Установка и запуск

Установите зависимости и синхронизируйте окружение:

```bash
uv sync
```

Запустите приложение из корня проекта:

```bash
uv run database
```

## Управление таблицами

| Команда | Описание |
| --- | --- |
| `create_table <имя> <столбец:тип> ...` | Создаёт таблицу |
| `list_tables` | Показывает список таблиц |
| `drop_table <имя>` | Удаляет таблицу |
| `help` | Показывает справку |
| `exit` | Завершает программу |

Поддерживаемые типы столбцов: `int`, `str`, `bool`, `float`.
Столбец `ID:int` создаётся автоматически и располагается первым.

### Пример использования

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
=======
Создание таблицы:

```text
create_table users name:str age:int is_active:bool
```

Автоматически добавляется столбец `ID:int`.

Список таблиц:

```text
list_tables
```

Удаление таблицы:

```text
drop_table users
```

Удаление требует подтверждения `y`.

## CRUD-операции

Добавление записи:

```text
insert into users values ("Sergei", 28, true)
```

Чтение всех записей:

```text
select from users
```

Чтение по условию:

```text
select from users where age = 28
```

Обновление записи:

```text
update users set age = 29 where name = "Sergei"
```

Удаление записи:

```text
delete from users where ID = 1
```

Удаление требует подтверждения `y`.

Информация о таблице:

```text
info users
```

Допустимые типы столбцов: `int`, `str`, `bool`.
Строковые значения необходимо заключать в двойные кавычки.
Все пользовательские поля обязательны.

## Хранение

Метаданные хранятся в `db_meta.json`.
Данные каждой таблицы хранятся отдельно в каталоге `data/`,
например `data/users.json`.

Установка собранного пакета как CLI-инструмента:

```bash
uv tool install --force dist/primitive_db-0.1.0-py3-none-any.whl
```

Запуск установленной программы:

```bash
database
```

=======

## Проверка качества кода

```bash
uv run ruff check .
```

