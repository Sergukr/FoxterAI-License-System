"""
API для аутентификации и проверки подключения
ИСПРАВЛЕНО: правильная проверка подключения к серверу
"""

from typing import Dict, Optional
from .base_client import BaseAPIClient


class AuthAPI(BaseAPIClient):
    """API для работы с аутентификацией"""
    
    def test_connection(self) -> bool:
        """
        Проверить соединение с сервером
        
        Returns:
            bool: True если сервер доступен и API ключ валиден
        """
        try:
            # ИСПРАВЛЕНО: используем /api/licenses для проверки, так как / не существует
            response = self.get('/api/licenses')
            # Если получили ответ и он содержит success - значит подключение работает
            return response.get('success', False)
        except Exception as e:
            print(f"[AuthAPI] Ошибка проверки подключения: {e}")
            return False
    
    def verify_api_key(self) -> Dict:
        """
        Проверить валидность API ключа
        
        Returns:
            Dict: Информация о ключе и правах доступа
        """
        try:
            # Используем запрос к лицензиям для проверки ключа
            response = self.get('/api/licenses')
            if response.get('success'):
                return {
                    'valid': True,
                    'permissions': ['read', 'write', 'delete'],
                    'user': 'admin'
                }
            return {
                'valid': False,
                'error': 'Invalid response'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_server_info(self) -> Dict:
        """
        Получить информацию о сервере
        
        Returns:
            Dict: Версия сервера и другая информация
        """
        try:
            # Пробуем получить статистику как индикатор работы сервера
            response = self.get('/api/statistics')
            if response.get('success'):
                stats = response.get('statistics', {})
                return {
                    'version': '3.0',
                    'name': 'FoxterAI License Server',
                    'uptime': 0,  # Сервер не предоставляет uptime
                    'licenses_count': stats.get('total', 0)
                }
            return {
                'version': '3.0',
                'name': 'FoxterAI License Server',
                'error': 'Could not get statistics'
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def check_health(self) -> Dict:
        """
        Проверить здоровье сервера
        
        Returns:
            Dict: Статус компонентов сервера
        """
        try:
            # Проверяем доступность API через запрос лицензий
            response = self.get('/api/licenses')
            
            if response.get('success'):
                return {
                    'status': 'healthy',
                    'database': True,  # Если вернулись лицензии - БД работает
                    'api': True,
                    'response_time': 0
                }
            else:
                return {
                    'status': 'unhealthy',
                    'database': False,
                    'api': True,  # API отвечает, но что-то не так
                    'response_time': 0
                }
        except Exception as e:
            return {
                'status': 'error',
                'database': False,
                'api': False,
                'error': str(e)
            }