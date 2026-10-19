
import prompt


def welcome():
    """Запускает интерактивный цикл программы."""
    print("Первая попытка запустить проект!")
    print()

    while True:
        print("***")
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ").strip().lower()

        if command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print("Доступные команды:")
            print("  help - справочная информация")
            print("  exit - выйти из программы")

        else:
            print(f"Неизвестная команда: {command}")
            print("Введите help для получения справки.")

        print()
