import logging
import os
from datetime import datetime


# Альтернативная версия с ротацией по дням
class DailyRotatingFileHandler(logging.Handler):
    """Обработчик с автоматической сменой файла каждый день"""

    def __init__(self):
        super().__init__()
        self.log_dir = 'logs'
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_date = datetime.now().strftime("%Y.%m.%d")
        self.setup_file_handler()

    def setup_file_handler(self):
        """Настройка файлового обработчика для текущей даты"""
        log_file = os.path.join(self.log_dir, f"log_{self.current_date}.log")
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

    def emit(self, record):
        try:
            # Проверяем, не изменилась ли дата
            new_date = datetime.now().strftime("%Y.%m.%d")
            if new_date != self.current_date:
                self.current_date = new_date
                self.setup_file_handler()

            # Записываем в файл
            self.file_handler.emit(record)
        except Exception as e:
            print(f"Daily log rotation error: {e}")


def setup_advanced_logger():
    """Продвинутая настройка логгера с ежедневной ротацией"""
    logger = logging.getLogger('SGS-Bot')
    logger.setLevel(logging.INFO)

    # Добавляем daily rotating handler
    daily_handler = DailyRotatingFileHandler()
    logger.addHandler(daily_handler)

    # Консольный вывод
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Используем простую версию для обратной совместимости
logger = setup_advanced_logger()


# Дополнительные утилиты для работы с логами
def get_log_files():
    """Получить список всех лог-файлов"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return []

    log_files = []
    for filename in os.listdir(log_dir):
        if filename.startswith("log_") and filename.endswith(".log"):
            file_path = os.path.join(log_dir, filename)
            stat = os.stat(file_path)
            log_files.append({
                'name': filename,
                'path': file_path,
                'date': filename.replace("log_", "").replace(".log", ""),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })

    return sorted(log_files, key=lambda x: x['date'], reverse=True)


def get_todays_log_file():
    """Получить путь к сегодняшнему лог-файлу"""
    current_date = datetime.now().strftime("%Y.%m.%d")
    return os.path.join('logs', f"log_{current_date}.log")
