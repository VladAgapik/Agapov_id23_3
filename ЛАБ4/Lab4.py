import os
import shutil
import json

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("Ошибка: Файл конфигурации config.json не найден!")
    exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

BASE_DIR = os.getcwd()
current_dir = BASE_DIR

if not os.path.exists(CONFIG_FILE):
    print("Ошибка: Файл конфигурации config.json не найден!")
    exit(1)

def get_full_path(name):
    path = os.path.abspath(os.path.join(current_dir, name))
    if path.startswith(BASE_DIR):
        return path
    else:
        print("Ошибка: выход за пределы рабочей папки запрещен!")
        return None

def create_folder(name):
    path = get_full_path(name)
    if path:
        os.makedirs(path, exist_ok=True)
        print(f"Папка '{name}' создана.")

def remove_folder(name):
    path = get_full_path(name)
    if path and os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Папка '{name}' удалена.")
    else:
        print(f"Ошибка: папка '{name}' не существует.")

def change_directory(name):
    global current_dir
    if name == "..":
        if current_dir != BASE_DIR:  # Не позволяем выйти за пределы BASE_DIR
            current_dir = os.path.dirname(current_dir)
    else:
        path = get_full_path(name)
        if path and os.path.isdir(path):
            current_dir = path
        else:
            print(f"Ошибка: папка '{name}' не найдена.")

    print(f"Текущая директория: {current_dir}")

def create_file(name):
    path = get_full_path(name)
    if path:
        with open(path, "w") as file:
            pass
        print(f"Файл '{name}' создан.")

def write_to_file(name, text):
    path = get_full_path(name)
    if path and os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Текст записан в файл '{name}'.")
    else:
        print(f"Ошибка: файл '{name}' не существует.")

def read_file(name):
    path = get_full_path(name)
    if path and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as file:
            print(f"Содержимое файла '{name}':\n")
            print(file.read())
    else:
        print(f"Ошибка: файл '{name}' не найден.")

def delete_file(name):
    path = get_full_path(name)
    if path and os.path.isfile(path):
        os.remove(path)
        print(f"Файл '{name}' удален.")
    else:
        print(f"Ошибка: файл '{name}' не существует.")

def copy_file(src, dest):
    src_path = get_full_path(src)
    dest_path = get_full_path(dest)
    if src_path and dest_path and os.path.isfile(src_path):
        shutil.copy2(src_path, dest_path)
        print(f"Файл '{src}' скопирован в '{dest}'.")
    else:
        print(f"Ошибка: файл '{src}' не найден или путь назначения некорректен.")

def move_file(src, dest):
    src_path = get_full_path(src)
    dest_path = get_full_path(dest)
    if src_path and dest_path and os.path.isfile(src_path):
        shutil.move(src_path, dest_path)
        print(f"Файл '{src}' перемещен в '{dest}'.")
    else:
        print(f"Ошибка: файл '{src}' не найден или путь назначения некорректен.")

def rename_file(old_name, new_name):
    old_path = get_full_path(old_name)
    new_path = get_full_path(new_name)
    if old_path and new_path and os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"'{old_name}' переименован в '{new_name}'.")
    else:
        print(f"Ошибка: '{old_name}' не найден.")

def list_directory():
    print(f"Содержимое папки '{current_dir}':")
    for item in os.listdir(current_dir):
        print(item)

def main():
    while True:
        command = input("\nВведите команду (help для справки): ").strip().split(" ", 1)
        action = command[0].lower()
        args = command[1] if len(command) > 1 else ""

        if action == "help":
            print("\nДоступные команды:")
            print("  mkdir <имя>       - создать папку")
            print("  rmdir <имя>       - удалить папку")
            print("  cd <имя>          - перейти в папку")
            print("  cd ..             - выйти на уровень вверх")
            print("  touch <имя>       - создать пустой файл")
            print("  write <имя>       - записать текст в файл")
            print("  read <имя>        - вывести содержимое файла")
            print("  rm <имя>          - удалить файл")
            print("  cp <ист> <цель>   - копировать файл")
            print("  mv <ист> <цель>   - переместить файл")
            print("  rename <стар> <нов> - переименовать файл/папку")
            print("  ls                - показать содержимое текущей папки")
            print("  exit              - выйти из программы")

        elif action == "mkdir":
            create_folder(args)
        elif action == "rmdir":
            remove_folder(args)
        elif action == "cd":
            change_directory(args)
        elif action == "touch":
            create_file(args)
        elif action == "write":
            text = input("Введите текст: ")
            write_to_file(args, text)
        elif action == "read":
            read_file(args)
        elif action == "rm":
            delete_file(args)
        elif action == "cp":
            src, dest = args.split(" ", 1)
            copy_file(src, dest)
        elif action == "mv":
            src, dest = args.split(" ", 1)
            move_file(src, dest)
        elif action == "rename":
            old_name, new_name = args.split(" ", 1)
            rename_file(old_name, new_name)
        elif action == "ls":
            list_directory()
        elif action == "exit":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Введите 'help' для списка команд.")

if __name__ == "__main__":
    main()
