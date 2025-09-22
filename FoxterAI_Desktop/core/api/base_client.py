"""
Базовый HTTP клиент для API
Общая функциональность для всех API модулей
"""

import requests
from typing import Dict, Optional, Any
import json


class BaseAPIClient:
    """Базовый класс для работы с API"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        """
        Инициализация базового клиента
        
        Args:
            base_url: Базовый URL сервера
            api_key: API ключ для авторизации
            timeout: Таймаут запросов
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        # Создаём сессию для переиспользования соединения
        self.session = requests.Session()
        
        # Устанавливаем заголовки по умолчанию
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FoxterAI-Desktop/2.2',
            'X-API-Key': self.api_key
        })
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API
            data: Данные для отправки в теле запроса
            params: Параметры URL
            
        Returns:
            Dict: Ответ сервера в виде словаря
            
        Raises:
            requests.exceptions.RequestException: При ошибке запроса
        """
        # Формируем полный URL
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Выполняем запрос
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Проверяем статус код
            if response.status_code == 401:
                raise ValueError("Неверный API ключ")
            elif response.status_code == 403:
                raise ValueError("Доступ запрещён")
            elif response.status_code == 404:
                raise ValueError(f"Эндпоинт не найден: {endpoint}")
            elif response.status_code >= 500:
                raise ValueError(f"Ошибка сервера: {response.status_code}")
            
            # Проверяем на другие ошибки
            response.raise_for_status()
            
            # Парсим JSON ответ
            return response.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Превышено время ожидания ({self.timeout}с)")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Не удалось подключиться к серверу")
        except json.JSONDecodeError:
            raise ValueError("Некорректный ответ сервера (не JSON)")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        GET запрос
        
        Args:
            endpoint: Конечная точка API
            params: Параметры запроса
            
        Returns:
            Dict: Ответ сервера
        """
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        POST запрос
        
        Args:
            endpoint: Конечная точка API
            data: Данные для отправки
            
        Returns:
            Dict: Ответ сервера
        """
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        PUT запрос
        
        Args:
            endpoint: Конечная точка API
            data: Данные для отправки
            
        Returns:
            Dict: Ответ сервера
        """
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        DELETE запрос
        
        Args:
            endpoint: Конечная точка API
            
        Returns:
            Dict: Ответ сервера
        """
        return self._make_request('DELETE', endpoint)
    
    def close(self):
        """Закрыть сессию"""
        self.session.close()
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.close()