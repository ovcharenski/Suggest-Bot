import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # Создаем папку logs если ее нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger('SuggestBot')
    logger.setLevel(logging.INFO)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Логирование в файл с ротацией
    file_handler = RotatingFileHandler(
        'logs/suggest_bot.log',
        maxBytes=1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()