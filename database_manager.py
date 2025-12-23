import requests
import json
import time
from typing import Optional, Dict, List, Any
from config import Config

class DatabaseManager:
    """Менеджер для работы с базой данных через API"""
    
    def __init__(self):
        self.api_url = Config.API_URL
        self.api_key = Config.API_KEY
        self.headers = {'X-API-Key': self.api_key} if self.api_key else {}
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Выполнить запрос к API"""
        try:
            url = f"{self.api_url}{endpoint}"
            response = requests.request(method, url, headers=self.headers, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("API: Unauthorized - check API_KEY")
            elif response.status_code == 404:
                return None
            else:
                print(f"API: Error {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"API: Connection error - {e}")
            
        return None
    
    # ===== USERS =====
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return self._make_request('GET', f'/api/users/id/{user_id}')
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Получить пользователя по username"""
        return self._make_request('GET', f'/api/users/{username}')
    
    def create_user(self, user_data: Dict) -> bool:
        """Создать нового пользователя"""
        response = self._make_request('POST', '/api/users', json=user_data)
        return response is not None and 'message' in response
    
    def update_user(self, user_id: int, update_data: Dict) -> bool:
        """Обновить данные пользователя"""
        response = self._make_request('PUT', f'/api/users/{user_id}', json=update_data)
        return response is not None and 'message' in response
    
    def get_user_rank(self, user_id: int) -> str:
        """Получить ранг пользователя"""
        user = self.get_user(user_id)
        return user.get('rank', 'user') if user else 'user'
    
    # ===== BANS =====
    def get_ban(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о бане пользователя"""
        return self._make_request('GET', f'/api/bans/{user_id}')
    
    def is_user_banned(self, user_id: int) -> bool:
        """Проверка, забанен ли пользователь"""
        ban = self.get_ban(user_id)
        if not ban:
            return False
        
        banned_at = ban.get('banned_at', 0)
        ban_time = ban.get('ban_time', 0)
        
        if ban_time == 0:  # Перманентный бан
            return True
        
        # Проверяем, не истек ли временный бан
        current_time = int(time.time())
        return current_time < banned_at + (ban_time * 3600)
    
    # ===== ROLES =====
    def is_operator(self, user_id: int) -> bool:
        """Проверка, является ли пользователь оператором"""
        response = self._make_request('GET', f'/api/operators/{user_id}')
        return response is not None and 'user_id' in response
    
    def is_global_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь глобальным админом"""
        response = self._make_request('GET', f'/api/global_admins/{user_id}')
        return response is not None and 'user_id' in response
    
    def is_local_admin(self, user_id: int, bot_name: str = None) -> bool:
        """Проверка, является ли пользователь локальным админом"""
        # Для текущего бота можно определить по имени бота
        # Здесь упрощенная проверка - через ранг пользователя
        user = self.get_user(user_id)
        if user and user.get('rank') == 'ladmin':
            return True
        return False
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь админом любого уровня"""
        return (self.is_operator(user_id) or 
                self.is_global_admin(user_id) or 
                self.is_local_admin(user_id))
    
    # ===== SYSTEM =====
    def health_check(self) -> bool:
        """Проверка здоровья API"""
        response = self._make_request('GET', '/api/health')
        return response is not None and response.get('status') == 'healthy'
    
    # ===== AUTH CODES =====
    def create_auth_code(self, code: str, user_id: int) -> bool:
        """Создать код авторизации"""
        data = {
            'code': code,
            'user_id': user_id,
            'created_at': int(time.time())
        }
        response = self._make_request('POST', '/api/auth_codes', json=data)
        return response is not None and 'message' in response
    
    def use_auth_code(self, code: str) -> Optional[Dict]:
        """Использовать код авторизации"""
        response = self._make_request('POST', f'/api/auth_codes/{code}/use')
        return response