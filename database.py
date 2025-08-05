import csv
import os
from logger import logger

FILE_MAP = {
    "admin": "data/adminList.csv",
    "banned": "data/bannedList.csv",
    "reg": "data/regList.csv"
}

def ensure_data_directory():
    if not os.path.exists('data'):
        os.makedirs('data')
        logger.info("Created data directory")


def readcsv(listname):
    """Чтение CSV файла с обработкой ошибок"""
    filename = FILE_MAP.get(listname)
    if not filename:
        logger.error(f"Invalid listname: {listname}")
        return {}
    
    ensure_data_directory()
    diction = {}

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                if not line or line[0] == "username":
                    continue
                try:
                    diction[line[0]] = [line[1], int(line[2])]
                except (IndexError, ValueError) as e:
                    logger.error(f"Error processing line: {line}. Error: {e}")
    except FileNotFoundError:
        logger.warning(f"File {filename} not found, creating new one")
        # Создаем файл с заголовком
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["username", "first_name", "user_id"])
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
    
    return diction


def changecsv(listname, message):
    """Добавление пользователя в CSV с обработкой ошибок"""
    filename = FILE_MAP.get(listname)
    if not filename:
        logger.error(f"Invalid listname: {listname}")
        return False

    ensure_data_directory()
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.id
            ])
        logger.info(f"Added user @{message.from_user.username} to {listname} list")
        return True
    except Exception as e:
        logger.error(f"Error writing to {filename}: {e}")
        return False


def adduser(listname, username, first_name=None, user_id=None):
    """
    Добавляет пользователя в указанный CSV файл

    Args:
        listname: Название списка ('admin', 'banned', 'reg')
        username: Имя пользователя (обязательное)
        first_name: Имя (опциональное)
        user_id: ID пользователя (опциональное)

    Returns:
        bool: True если операция успешна, False если произошла ошибка
    """
    filename = FILE_MAP.get(listname)
    if not filename:
        logger.error(f"Invalid listname: {listname}")
        return False

    if not username:
        logger.error("Username is required")
        return False

    try:
        ensure_data_directory()

        # Проверяем, существует ли уже пользователь
        existing_users = readcsv(listname)
        if username in existing_users:
            logger.warning(f"User @{username} already exists in {listname} list")
            return False

        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, first_name, user_id or 0000000])

        logger.info(f"Added user @{username} to {listname} list")
        return True

    except Exception as e:
        logger.error(f"Failed to add user @{username} to {listname} list: {e}")
        return False


def deluser(listname, username):
    """
    Удаляет пользователя из указанного CSV файла

    Args:
        listname: Название списка ('admin', 'banned', 'reg')
        username: Имя пользователя для удаления

    Returns:
        bool: True если пользователь удален, False если ошибка или пользователь не найден
    """
    filename = FILE_MAP.get(listname)
    if not filename:
        logger.error(f"Invalid listname: {listname}")
        return False

    if not username:
        logger.error("Username is required")
        return False

    try:
        ensure_data_directory()

        # Проверяем существование файла
        if not os.path.exists(filename):
            logger.warning(f"File {filename} does not exist")
            return False

        # Читаем все строки
        with open(filename, 'r', encoding='utf-8') as file:
            rows = list(csv.reader(file))

        # Фильтруем строки
        original_count = len(rows)
        filtered_rows = [row for row in rows if not row or row[0] != username]

        # Если ничего не изменилось
        if len(filtered_rows) == original_count:
            logger.info(f"User @{username} not found in {listname} list")
            return False

        # Записываем обратно
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(filtered_rows)

        logger.info(f"Removed user @{username} from {listname} list")
        return True

    except csv.Error as e:
        logger.error(f"CSV error while deleting user @{username}: {e}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied when accessing {filename}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting user @{username}: {e}")
        return False
