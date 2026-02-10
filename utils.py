import json
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from typing import Dict, List, Optional
from config import Config
import time

class TagManager:
    """Менеджер для работы с тегами"""
    
    def __init__(self):
        self.tags_file = Config.TAGS_FILE
        self._ensure_tags_file()
    
    def _ensure_tags_file(self):
        """Проверка и создание файла тегов"""
        if not os.path.exists(self.tags_file):
            default_tags = {
                "🐛 Баг": "#баг",
                "💡 Идея": "#идея",
                "🚀 Улучшение": "#улучшение",
                "📝 Документация": "#документация",
                "🎨 Дизайн": "#дизайн"
            }
            self.save_tags(default_tags)
    
    def load_tags(self) -> Dict:
        """Загрузить теги из файла"""
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tags: {e}")
            return {}
    
    def save_tags(self, tags_data: Dict) -> bool:
        """Сохранить теги в файл"""
        try:
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(tags_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tags: {e}")
            return False
    
    def create_tags_keyboard(self) -> ReplyKeyboardMarkup:
        """Создать клавиатуру с тегами"""
        tags = self.load_tags()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        if tags:
            tag_buttons = [KeyboardButton(tag_name) for tag_name in tags.keys()]
            
            for i in range(0, len(tag_buttons), 2):
                if i + 1 < len(tag_buttons):
                    keyboard.add(tag_buttons[i], tag_buttons[i + 1])
                else:
                    keyboard.add(tag_buttons[i])
        
        # Кнопка для отправки без тега
        keyboard.add(KeyboardButton("📤 Отправить без тега"))
        return keyboard


class UserValidator:
    """Валидатор пользователей"""
    
    @staticmethod
    def validate_user(message) -> tuple[bool, Optional[str]]:
        """Проверка пользователя"""
        if not message.from_user.username:
            return False, "❌ Для использования бота необходимо иметь username."
        
        if not message.from_user.id:
            return False, "❌ Ошибка: не удалось получить ID пользователя."
        
        return True, None
    
    @staticmethod
    def is_supported_content(message) -> bool:
        """Проверка, поддерживается ли тип контента"""
        return message.content_type in Config.SUPPORTED_CONTENT_TYPES


class SuggestionBuilder:
    """Сборщик предложений"""
    
    def __init__(self):
        self.pending_suggestions = {}  # chat_id -> suggestion_data
    
    def create_suggestion(self, chat_id: int, message, user_data: Dict) -> Dict:
        """Создать структуру предложения"""
        suggestion = {
            'username': message.from_user.username,
            'user_id': message.from_user.id,
            'content_type': message.content_type,
            'timestamp': int(time.time())
        }

        if message.content_type == 'text':
            suggestion['text'] = message.text
        elif message.content_type == 'photo':
            suggestion['photo'] = message.photo[-1].file_id
            suggestion['caption'] = message.caption
        elif message.content_type == 'video':
            suggestion['video'] = message.video.file_id
            suggestion['caption'] = message.caption
        
        self.pending_suggestions[chat_id] = suggestion
        return suggestion
    
    def get_suggestion(self, chat_id: int) -> Optional[Dict]:
        """Получить предложение по ID чата"""
        return self.pending_suggestions.get(chat_id)
    
    def remove_suggestion(self, chat_id: int):
        """Удалить предложение"""
        if chat_id in self.pending_suggestions:
            del self.pending_suggestions[chat_id]
    
    def cleanup_old_suggestions(self, max_age_seconds: int = 3600):
        """Очистка устаревших предложений"""
        current_time = int(time.time())
        expired = []
        
        for chat_id, suggestion in self.pending_suggestions.items():
            if current_time - suggestion['timestamp'] > max_age_seconds:
                expired.append(chat_id)
        
        for chat_id in expired:
            del self.pending_suggestions[chat_id]
        
        return len(expired)


class MessageFormatter:
    """Форматирование сообщений"""
    
    @staticmethod
    def format_suggestion_caption(suggestion: Dict, tag_info: Optional[Dict] = None) -> str:
        """Форматировать подпись для предложения"""
        base = f"💡 Предложение от @{suggestion['username']} (<code>ID: {suggestion['user_id']}</code>)"
        
        if tag_info and tag_info.get('hashtag'):
            base += f"\n🏷️ Тег: {tag_info['hashtag']}"
        
        if suggestion.get('caption'):
            base += f"\n\n{suggestion['caption']}"
        
        return base
    
    @staticmethod
    def format_user_info(user_data: Dict) -> str:
        """Форматировать информацию о пользователе"""
        username = user_data.get('username', 'N/A')
        user_id = user_data.get('user_id', 'N/A')
        first_name = user_data.get('first_name', 'N/A')
        rank = user_data.get('rank', 'user')
        rank_text = Config.RANK_TEXTS.get(rank, '👤 Пользователь')
        banned = "❌ Забанен" if user_data.get('banned') else "✅ Активен"
        warns = user_data.get('warns', 0)

        response = (f"👤 Информация о пользователе\n\n"
                    f"📧 Username: @{username}\n"
                    f"👨‍💼 Ранг: {rank_text}\n"
                    f"🆔 ID: <code>{user_id}</code>\n"
                    f"📛 Имя: {first_name}")
        if rank not in ['gadmin', 'operator']:
            response += (
                f"\n📊 Ограничения: {banned}\n"
                f"💢 Предупреждения: {warns}/{Config.MAX_WARN}")
        
        return response