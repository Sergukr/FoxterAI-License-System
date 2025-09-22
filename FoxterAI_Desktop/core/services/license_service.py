"""
Сервисный слой для работы с лицензиями
ИСПРАВЛЕНО: использует рабочий api_client вместо несуществующих модулей
"""

from typing import List, Dict, Optional, Callable, Any
import threading
from datetime import datetime

# Используем СУЩЕСТВУЮЩИЙ API клиент из modules
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from modules.api_client import APIClient
except ImportError:
    print("⚠️ Не найден modules.api_client, пробуем альтернативный путь...")
    try:
        from api_client import APIClient
    except ImportError:
        print("❌ APIClient не найден!")
        APIClient = None


class LicenseService:
    """Сервис для управления лицензиями"""
    
    def __init__(self):
        """Инициализация сервиса"""
        print("🔧 Инициализация LicenseService...")
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        
        # Инициализируем API клиент
        self._init_api_client()
        
        # Данные
        self.licenses: List[Dict] = []
        self.statistics = {}
        
        # Состояние
        self.is_connected = False
        self.last_error = None
        
        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_licenses_loaded: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        print("✅ LicenseService инициализирован")
    
    def _load_config(self) -> Dict:
        """Загрузить конфигурацию из файла"""
        import configparser
        
        print("📖 Загрузка конфигурации из config.ini...")
        
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        conf_dict = {
            'host': config.get('SERVER', 'host', fallback='localhost'),
            'port': config.getint('SERVER', 'port', fallback=3000),
            'protocol': config.get('SERVER', 'protocol', fallback='http'),
            'timeout': config.getint('SERVER', 'timeout', fallback=10),
            'api_key': config.get('SERVER', 'api_key', fallback='')
        }
        
        print(f"📌 Конфигурация: {conf_dict['protocol']}://{conf_dict['host']}:{conf_dict['port']}")
        print(f"📌 API Key: {conf_dict['api_key'][:10]}..." if conf_dict['api_key'] else "⚠️ API Key не установлен!")
        
        return conf_dict
    
    def _init_api_client(self):
        """Инициализировать API клиент"""
        if not APIClient:
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: APIClient не найден!")
            self.api_client = None
            return
        
        try:
            print("🔄 Создание API клиента...")
            
            # Создаем экземпляр API клиента
            self.api_client = APIClient(
                self.config['host'],
                self.config['port'],
                self.config['protocol'],
                self.config['timeout']
            )
            
            print(f"✅ API клиент создан для {self.config['protocol']}://{self.config['host']}:{self.config['port']}")
            
        except Exception as e:
            print(f"❌ Ошибка создания API клиента: {e}")
            self.api_client = None
    
    def set_callbacks(self, on_connected=None, on_disconnected=None,
                      on_licenses_loaded=None, on_error=None):
        """
        Установить callback функции
        
        Args:
            on_connected: Вызывается при успешном подключении
            on_disconnected: Вызывается при отключении
            on_licenses_loaded: Вызывается после загрузки лицензий
            on_error: Вызывается при ошибке
        """
        print("📎 Установка callbacks...")
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.on_licenses_loaded = on_licenses_loaded
        self.on_error = on_error
    
    def connect(self) -> bool:
        """
        Подключиться к серверу
        
        Returns:
            bool: True если подключение успешно
        """
        print("\n🔌 === ПОДКЛЮЧЕНИЕ К СЕРВЕРУ ===")
        
        if not self.api_client:
            print("❌ API клиент не инициализирован")
            self.is_connected = False
            self.last_error = "API клиент не инициализирован"
            
            if self.on_error:
                self.on_error(self.last_error)
            
            return False
        
        try:
            print("🔄 Проверка подключения к серверу...")
            print(f"📡 URL: {self.config['protocol']}://{self.config['host']}:{self.config['port']}")
            print(f"🔑 API Key: {self.config['api_key'][:20]}..." if len(self.config['api_key']) > 20 else f"🔑 API Key: {self.config['api_key']}")
            
            # Проверяем подключение
            connection_result = self.api_client.test_connection()
            print(f"📊 Результат test_connection: {connection_result}")
            
            if connection_result:
                print("✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!")
                self.is_connected = True
                self.last_error = None
                
                if self.on_connected:
                    print("🔔 Вызываем on_connected callback")
                    self.on_connected()
                
                return True
            else:
                print("❌ НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ")
                print("💡 Возможные причины:")
                print("   1. Неверный API ключ")
                print("   2. Сервер не запущен")
                print("   3. Неправильный адрес/порт")
                
                self.is_connected = False
                self.last_error = "Сервер недоступен или неверный API ключ"
                
                if self.on_disconnected:
                    print("🔔 Вызываем on_disconnected callback")
                    self.on_disconnected()
                
                return False
            
        except Exception as e:
            print(f"❌ ИСКЛЮЧЕНИЕ при подключении: {e}")
            import traceback
            traceback.print_exc()
            
            self.is_connected = False
            self.last_error = str(e)
            
            if self.on_error:
                print("🔔 Вызываем on_error callback")
                self.on_error(str(e))
            
            return False
    
    def disconnect(self):
        """Отключиться от сервера"""
        print("🔌 Отключение от сервера")
        self.is_connected = False
        
        if self.on_disconnected:
            self.on_disconnected()
    
    def get_licenses(self) -> List[Dict]:
        """
        Получить список всех лицензий
        
        Returns:
            List[Dict]: Список лицензий
        """
        print("\n📋 === ПОЛУЧЕНИЕ ЛИЦЕНЗИЙ ===")
        
        if not self.api_client:
            print("❌ API клиент не инициализирован")
            return []
        
        if not self.is_connected:
            print("⚠️ Нет подключения к серверу, пытаемся подключиться...")
            if not self.connect():
                print("❌ Не удалось подключиться")
                return []
        
        try:
            print("📡 Отправка запроса на получение лицензий...")
            print(f"🌐 Endpoint: {self.config['protocol']}://{self.config['host']}:{self.config['port']}/api/licenses")
            
            # Получаем лицензии через API
            licenses = self.api_client.get_licenses()
            
            print(f"📦 Тип ответа: {type(licenses)}")
            
            if licenses is not None:
                print(f"✅ ПОЛУЧЕНО {len(licenses)} ЛИЦЕНЗИЙ!")
                
                # Выводим первую лицензию для отладки
                if len(licenses) > 0:
                    print(f"📝 Пример лицензии: {licenses[0]}")
                
                self.licenses = licenses
                
                # Вызываем callback
                if self.on_licenses_loaded:
                    print("🔔 Вызываем on_licenses_loaded callback")
                    self.on_licenses_loaded(licenses)
                
                return licenses
            else:
                print("⚠️ Получен None от API")
                return []
            
        except Exception as e:
            print(f"❌ ИСКЛЮЧЕНИЕ при получении лицензий: {e}")
            import traceback
            traceback.print_exc()
            
            if self.on_error:
                self.on_error(str(e))
            
            return []
    
    def get_statistics(self) -> Dict:
        """
        Получить статистику
        
        Returns:
            Dict: Статистика по лицензиям
        """
        if not self.api_client or not self.is_connected:
            return {}
        
        try:
            print("📊 Получение статистики...")
            stats = self.api_client.get_statistics()
            self.statistics = stats
            print(f"✅ Статистика получена: {stats}")
            return stats
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    def create_license(self, data: Dict) -> Dict:
        """
        Создать новую лицензию
        
        Args:
            data: Данные для создания лицензии
            
        Returns:
            Dict: Результат создания
        """
        if not self.api_client or not self.is_connected:
            return {'success': False, 'error': 'Нет подключения к серверу'}
        
        try:
            print(f"➕ Создание лицензии для {data.get('client_name', 'Unknown')}")
            
            # Сервер принимает только эти параметры при создании
            # owner_name и остальное заполнится при активации роботом
            result = self.api_client.create_license(
                client_name=data.get('client_name', ''),
                client_contact=data.get('phone', ''),
                client_telegram=data.get('telegram', ''),
                months=data.get('months', 1),
                notes=data.get('notes', '')
                # Остальные параметры игнорируются при создании
            )
            
            print(f"📦 Результат создания: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Ошибка создания лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_license(self, license_key: str, updates: Dict) -> bool:
        """
        Обновить лицензию
        
        Args:
            license_key: Ключ лицензии
            updates: Обновления
            
        Returns:
            bool: True если успешно
        """
        if not self.api_client or not self.is_connected:
            return False
        
        try:
            print(f"✏️ Обновление лицензии {license_key[:12]}...")
            result = self.api_client.update_license(license_key, **updates)
            success = result.get('success', False)
            print(f"📦 Результат: {success}")
            return success
        except Exception as e:
            print(f"❌ Ошибка обновления лицензии: {e}")
            return False
    
    def delete_license(self, license_key: str) -> bool:
        """
        Удалить лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            bool: True если успешно
        """
        if not self.api_client or not self.is_connected:
            return False
        
        try:
            print(f"🗑️ Удаление лицензии {license_key[:12]}...")
            result = self.api_client.delete_license(license_key)
            success = result.get('success', False)
            print(f"📦 Результат: {success}")
            return success
        except Exception as e:
            print(f"❌ Ошибка удаления лицензии: {e}")
            return False
    
    def extend_license(self, license_key: str, months: int) -> bool:
        """
        Продлить лицензию
        
        Args:
            license_key: Ключ лицензии
            months: Количество месяцев
            
        Returns:
            bool: True если успешно
        """
        if not self.api_client or not self.is_connected:
            return False
        
        try:
            print(f"⏰ Продление лицензии {license_key[:12]}... на {months} мес.")
            result = self.api_client.extend_license(license_key, months)
            success = result.get('success', False)
            print(f"📦 Результат: {success}")
            return success
        except Exception as e:
            print(f"❌ Ошибка продления лицензии: {e}")
            return False
    
    def block_license(self, license_key: str) -> bool:
        """
        Заблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            bool: True если успешно
        """
        print(f"🔒 Блокировка лицензии {license_key[:12]}...")
        return self.update_license(license_key, {'status': 'blocked'})
    
    def unblock_license(self, license_key: str) -> bool:
        """
        Разблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            bool: True если успешно
        """
        print(f"🔓 Разблокировка лицензии {license_key[:12]}...")
        return self.update_license(license_key, {'status': 'active'})
    
    def get_license_by_key(self, license_key: str) -> Optional[Dict]:
        """
        Получить лицензию по ключу
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Optional[Dict]: Данные лицензии или None
        """
        for license in self.licenses:
            if license.get('license_key') == license_key:
                return license
        return None
    
    def refresh(self):
        """Обновить данные с сервера"""
        print("🔄 Обновление данных...")
        self.get_licenses()
        self.get_statistics()