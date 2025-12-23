import os
from dotenv import load_dotenv
import json

load_dotenv()

# Конфигурация бота
class Config:
    # Токен и чат
    SGS_TOKEN = os.getenv('SGS_TOKEN')
    SGS_CHAT_ID = os.getenv('SGS_CHAT_ID')
    
    # Пути
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    LOGS_DIR = os.getenv('LOGS_DIR', 'logs')
    TAGS_FILE = os.path.join(DATA_DIR, 'tags.json')
    
    # Лимиты
    MAX_WARN = int(os.getenv('MAX_WARN', 3))
    DEFAULT_BAN_TIME = int(os.getenv('DEFAULT_BAN_TIME', 24))  # часов
    
    # API
    API_URL = os.getenv('API_BASE_URL')
    API_KEY = os.getenv('API_KEY')
    
    # Ранги
    RANK_TEXTS = {
        'operator': '⚡ Оператор',
        'gadmin': '🔧 Глобальный администратор', 
        'ladmin': '🪛 Локальный администратор',
        'user': '👤 Пользователь'
    }
    
    # Поддерживаемые типы контента
    SUPPORTED_CONTENT_TYPES = ['text', 'photo', 'video']
    UNSUPPORTED_CONTENT_TYPES = ['document', 'audio', 'voice', 'sticker', 'location', 'contact']
    
    @classmethod
    def validate(cls):
        """Проверка конфигурации"""
        if not cls.SGS_TOKEN:
            raise ValueError("SGS_TOKEN not found in environment variables")
        if not cls.SGS_CHAT_ID:
            raise ValueError("SGS_CHAT_ID not found in environment variables")
        if not cls.API_KEY:
            print("Warning: API_KEY not found, some features may be limited")
        
        # Создание директорий
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        
        return True