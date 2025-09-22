"""
Менеджер конфигурации для FoxterAI License Manager
Централизованное управление настройками приложения
"""

import os
import configparser
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ConfigManager:
    """Менеджер конфигурации приложения"""
    
    # Значения по умолчанию
    DEFAULTS = {
        'SERVER': {
            'host': 'localhost',
            'port': '3000',
            'protocol': 'http',
            'timeout': '10',
            'api_key': 'FXA-Kj8$mN2@pQ9#vX5!wY3&zL7*'
        },
        'APP': {
            'auto_refresh': '60',
            'items_per_page': '50',
            'theme': 'dark',
            'window_width': '1400',
            'window_height': '800',
            'language': 'ru'
        },
        'EXPORT': {
            'default_format': 'xlsx',
            'include_hidden': 'false',
            'auto_save': 'true'
        }
    }
    
    def __init__(self, config_path: str = 'config.ini'):
        """
        Инициализация менеджера конфигурации
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        self._loaded = False
        self.load()
    
    def load(self) -> bool:
        """
        Загрузить конфигурацию из файла
        
        Returns:
            bool: True если успешно загружено
        """
        try:
            # Сначала загружаем значения по умолчанию
            self.config.read_dict(self.DEFAULTS)
            
            # Если файл существует, загружаем его поверх дефолтов
            if self.config_path.exists():
                self.config.read(self.config_path, encoding='utf-8')
                self._loaded = True
                return True
            else:
                # Если файла нет, создаём с дефолтами
                self.save()
                self._loaded = True
                return True
                
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            # В случае ошибки используем дефолты
            self.config.read_dict(self.DEFAULTS)
            return False
    
    def save(self) -> bool:
        """
        Сохранить конфигурацию в файл
        
        Returns:
            bool: True если успешно сохранено
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                self.config.write(file)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Получить значение из конфигурации
        
        Args:
            section: Секция конфигурации
            key: Ключ параметра
            default: Значение по умолчанию
            
        Returns:
            Any: Значение параметра
        """
        try:
            value = self.config.get(section, key)
            
            # Преобразуем типы
            if value.lower() in ('true', 'yes', 'on'):
                return True
            elif value.lower() in ('false', 'no', 'off'):
                return False
            elif value.isdigit():
                return int(value)
            elif '.' in value and all(p.isdigit() for p in value.split('.', 1)):
                return float(value)
            else:
                return value
                
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        Установить значение в конфигурации
        
        Args:
            section: Секция конфигурации
            key: Ключ параметра
            value: Значение для установки
            
        Returns:
            bool: True если успешно установлено
        """
        try:
            # Создаём секцию если её нет
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            # Преобразуем значение в строку
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            else:
                value = str(value)
            
            self.config.set(section, key, value)
            return True
            
        except Exception as e:
            print(f"Ошибка установки значения: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Получить всю секцию как словарь
        
        Args:
            section: Название секции
            
        Returns:
            Dict: Словарь параметров секции
        """
        result = {}
        
        if self.config.has_section(section):
            for key, value in self.config.items(section):
                # Преобразуем типы
                if value.lower() in ('true', 'yes', 'on'):
                    result[key] = True
                elif value.lower() in ('false', 'no', 'off'):
                    result[key] = False
                elif value.isdigit():
                    result[key] = int(value)
                elif '.' in value and all(p.isdigit() for p in value.split('.', 1)):
                    result[key] = float(value)
                else:
                    result[key] = value
        
        return result
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию сервера
        
        Returns:
            Dict: Параметры подключения к серверу
        """
        config = self.get_section('SERVER')
        # Обеспечиваем правильные типы
        config['port'] = int(config.get('port', 3000))
        config['timeout'] = int(config.get('timeout', 10))
        return config
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию приложения
        
        Returns:
            Dict: Параметры приложения
        """
        return self.get_section('APP')
    
    def get_export_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию экспорта
        
        Returns:
            Dict: Параметры экспорта
        """
        return self.get_section('EXPORT')
    
    def get_api_url(self) -> str:
        """
        Получить полный URL API сервера
        
        Returns:
            str: URL сервера
        """
        protocol = self.get('SERVER', 'protocol', 'http')
        host = self.get('SERVER', 'host', 'localhost')
        port = self.get('SERVER', 'port', 3000)
        return f"{protocol}://{host}:{port}"
    
    def get_api_key(self) -> str:
        """
        Получить API ключ
        
        Returns:
            str: API ключ
        """
        return self.get('SERVER', 'api_key', '')
    
    def get_window_size(self) -> tuple:
        """
        Получить размеры окна
        
        Returns:
            tuple: (width, height)
        """
        width = self.get('APP', 'window_width', 1400)
        height = self.get('APP', 'window_height', 800)
        return (width, height)
    
    def set_window_size(self, width: int, height: int) -> bool:
        """
        Сохранить размеры окна
        
        Args:
            width: Ширина окна
            height: Высота окна
            
        Returns:
            bool: True если сохранено
        """
        self.set('APP', 'window_width', width)
        self.set('APP', 'window_height', height)
        return self.save()
    
    def get_theme(self) -> str:
        """
        Получить текущую тему
        
        Returns:
            str: Название темы
        """
        return self.get('APP', 'theme', 'dark')
    
    def set_theme(self, theme: str) -> bool:
        """
        Установить тему
        
        Args:
            theme: Название темы
            
        Returns:
            bool: True если сохранено
        """
        self.set('APP', 'theme', theme)
        return self.save()
    
    def get_auto_refresh_interval(self) -> int:
        """
        Получить интервал автообновления
        
        Returns:
            int: Интервал в секундах (0 = отключено)
        """
        return self.get('APP', 'auto_refresh', 60)
    
    def set_auto_refresh_interval(self, seconds: int) -> bool:
        """
        Установить интервал автообновления
        
        Args:
            seconds: Интервал в секундах (0 = отключить)
            
        Returns:
            bool: True если сохранено
        """
        self.set('APP', 'auto_refresh', seconds)
        return self.save()
    
    def get_items_per_page(self) -> int:
        """
        Получить количество элементов на страницу
        
        Returns:
            int: Количество элементов
        """
        return self.get('APP', 'items_per_page', 50)
    
    def get_language(self) -> str:
        """
        Получить язык интерфейса
        
        Returns:
            str: Код языка
        """
        return self.get('APP', 'language', 'ru')
    
    def reset_to_defaults(self) -> bool:
        """
        Сбросить все настройки на значения по умолчанию
        
        Returns:
            bool: True если успешно
        """
        try:
            self.config.read_dict(self.DEFAULTS)
            return self.save()
        except Exception as e:
            print(f"Ошибка сброса настроек: {e}")
            return False
    
    def validate(self) -> bool:
        """
        Проверить корректность конфигурации
        
        Returns:
            bool: True если конфигурация корректна
        """
        try:
            # Проверяем критичные параметры
            if not self.get_api_key():
                print("Предупреждение: API ключ не установлен")
                return False
            
            # Проверяем порт
            port = self.get('SERVER', 'port', 3000)
            if not (1 <= port <= 65535):
                print(f"Ошибка: Некорректный порт {port}")
                return False
            
            # Проверяем протокол
            protocol = self.get('SERVER', 'protocol', 'http')
            if protocol not in ('http', 'https'):
                print(f"Ошибка: Некорректный протокол {protocol}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Ошибка валидации конфигурации: {e}")
            return False
    
    def __str__(self) -> str:
        """Строковое представление"""
        return f"ConfigManager(path={self.config_path}, loaded={self._loaded})"
    
    def __repr__(self) -> str:
        """Отладочное представление"""
        sections = list(self.config.sections())
        return f"<ConfigManager sections={sections}>"


# Глобальный экземпляр
_config_manager = None


def get_config() -> ConfigManager:
    """
    Получить глобальный экземпляр менеджера конфигурации
    
    Returns:
        ConfigManager: Менеджер конфигурации
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
    
    return _config_manager