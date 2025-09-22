"""
API клиент для работы с сервером лицензий FoxterAI v3.0
ПОЛНЫЙ РАБОЧИЙ ФАЙЛ
"""

import requests
import json
import configparser
from datetime import datetime
from typing import Dict, List, Optional, Any
from .encoding_fix import EncodingFixer


class APIClient:
    """Клиент для работы с API сервера лицензий"""
    
    def __init__(self, host: str, port: int, protocol: str = 'http', timeout: int = 10):
        """
        Инициализация клиента
        
        Args:
            host: IP адрес или домен сервера
            port: Порт сервера
            protocol: Протокол (http/https)
            timeout: Таймаут запросов в секундах
        """
        self.base_url = f"{protocol}://{host}:{port}"
        self.timeout = timeout
        self.session = requests.Session()
        self.encoding_fixer = EncodingFixer()
        
        # Загружаем API ключ напрямую из конфига
        self.api_key = self._load_api_key()
        
        if not self.api_key:
            raise ValueError("API ключ не найден в config.ini! Добавьте api_key в секцию [SERVER]")
        
        # Заголовки по умолчанию с API ключом
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FoxterAI-Desktop/3.0',
            'X-API-Key': self.api_key
        })
    
    def _load_api_key(self) -> str:
        """Загрузить API ключ из config.ini"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            if config.has_section('SERVER'):
                return config.get('SERVER', 'api_key', fallback='')
            return ''
        except:
            return ''
    
    def test_connection(self) -> bool:
        """
        Проверить соединение с сервером
        
        Returns:
            bool: True если сервер доступен и API ключ валиден
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/licenses",
                timeout=self.timeout
            )
            
            # Проверяем статус код
            if response.status_code == 401:
                print("ОШИБКА: Неверный API ключ!")
                print(f"Текущий ключ: {self.api_key}")
                return False
                
            # Если получили ответ - проверяем его структуру
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Проверяем success в ответе
                    if isinstance(data, dict):
                        return data.get('success', False)
                    return True
                except:
                    return True
                    
            return False
            
        except requests.exceptions.ConnectionError:
            print(f"Не удалось подключиться к {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"Превышено время ожидания ({self.timeout}с)")
            return False
        except Exception as e:
            print(f"Ошибка проверки подключения: {e}")
            return False
    
    def get_licenses(self) -> List[Dict]:
        """
        Получить список всех лицензий
        
        Returns:
            List[Dict]: Список лицензий
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/licenses",
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                print("ОШИБКА: Неверный API ключ при получении лицензий")
                return []
                
            response.raise_for_status()
            
            data = response.json()
            
            # Сервер возвращает {success: true, licenses: [...]}
            if isinstance(data, dict):
                if data.get('success', False):
                    licenses = data.get('licenses', [])
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"Ошибка от сервера: {error}")
                    return []
            elif isinstance(data, list):
                # На всякий случай если формат изменится
                licenses = data
            else:
                print(f"Неожиданный формат ответа: {type(data)}")
                return []
            
            # Исправляем кодировку и добавляем вычисляемые поля
            fixed_licenses = []
            for lic in licenses:
                # Исправляем кодировку всего словаря
                fixed_lic = self.encoding_fixer.fix_dict_encoding(lic)
                
                # Специальная обработка поля account_owner (часто приходит в неправильной кодировке из MT4)
                if 'account_owner' in fixed_lic and fixed_lic['account_owner']:
                    owner_raw = fixed_lic['account_owner']
                    
                    if isinstance(owner_raw, str):
                        # Проверяем на признаки неправильной кодировки
                        if any(ord(c) > 127 for c in owner_raw) or any(c in owner_raw for c in ['ï', '¿', '½', 'ð', 'Ð', '$n']):
                            # Пробуем исправить кодировку
                            fixed_owner = None
                            
                            # Попытка 1: UTF-8 интерпретированный как Latin-1
                            try:
                                test = owner_raw.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
                                if test and not any(c in test for c in ['�', 'ï', '¿']):
                                    fixed_owner = test
                            except:
                                pass
                            
                            # Попытка 2: CP1251 интерпретированный как UTF-8
                            if not fixed_owner:
                                try:
                                    test = owner_raw.encode('latin-1', errors='ignore').decode('cp1251', errors='ignore')
                                    if test and not any(c in test for c in ['�', 'ï', '¿']):
                                        fixed_owner = test
                                except:
                                    pass
                            
                            # Попытка 3: Двойная кодировка
                            if not fixed_owner:
                                try:
                                    test = owner_raw.encode('utf-8', errors='ignore').decode('cp1251', errors='ignore')
                                    if test and not any(c in test for c in ['�']):
                                        fixed_owner = test
                                except:
                                    pass
                            
                            # Используем исправленное значение или оставляем очищенное
                            if fixed_owner:
                                # Очищаем от непечатных символов
                                cleaned = ''.join(c for c in fixed_owner if c.isprintable() or c.isspace())
                                fixed_lic['account_owner'] = cleaned.strip()
                            else:
                                # Если не удалось исправить - очищаем мусор
                                cleaned = ''.join(c for c in owner_raw if ord(c) < 128 and (c.isalnum() or c.isspace() or c in '.-_'))
                                fixed_lic['account_owner'] = cleaned.strip() if cleaned.strip() else f"Счет {lic.get('account_number', 'N/A')}"
                        else:
                            # Если нет проблем с кодировкой - просто очищаем пробелы
                            fixed_lic['account_owner'] = owner_raw.strip()
                else:
                    # Если поле отсутствует или пустое
                    fixed_lic['account_owner'] = 'Не активирован'
                
                # Добавляем форматированные даты
                for date_field in ['created_date', 'activation_date', 'expiry_date', 'last_check']:
                    if date_field in fixed_lic and fixed_lic[date_field]:
                        try:
                            dt = datetime.fromisoformat(fixed_lic[date_field].replace('Z', '+00:00'))
                            fixed_lic[f'{date_field}_formatted'] = dt.strftime('%d.%m.%Y %H:%M')
                        except:
                            fixed_lic[f'{date_field}_formatted'] = fixed_lic[date_field]
                
                # ИСПРАВЛЕНО: Вычисляем дни до истечения - ВСЕГДА должно быть число, не None!
                if fixed_lic.get('expiry_date'):
                    try:
                        expiry = datetime.fromisoformat(fixed_lic['expiry_date'].replace('Z', '+00:00'))
                        days_left = (expiry - datetime.now()).days
                        fixed_lic['days_left'] = days_left
                        
                        # Обновляем статус если истек
                        if days_left < 0 and fixed_lic.get('status') == 'active':
                            fixed_lic['status'] = 'expired'
                    except:
                        fixed_lic['days_left'] = 999  # Если не удается вычислить - ставим большое число
                else:
                    fixed_lic['days_left'] = 999  # Если нет даты истечения - ставим большое число
                
                fixed_licenses.append(fixed_lic)
            
            print(f"📦 Тип ответа: {type(licenses)}")
            print(f"✅ ПОЛУЧЕНО {len(fixed_licenses)} ЛИЦЕНЗИЙ!")
            
            return fixed_licenses
            
        except Exception as e:
            print(f"Ошибка получения лицензий: {e}")
            return []
    
    def create_license(self, client_name: str, client_contact: str = None, 
                      client_telegram: str = None, months: int = 1, 
                      notes: str = None) -> Dict:
        """
        Создать новую лицензию
        
        Args:
            client_name: Имя клиента
            client_contact: Контактный телефон
            client_telegram: Telegram клиента
            months: Срок действия в месяцах
            notes: Заметки
            
        Returns:
            Dict: Результат создания
        """
        try:
            data = {
                'client_name': client_name,
                'months': months
            }
            
            if client_contact:
                data['client_contact'] = client_contact
            if client_telegram:
                data['client_telegram'] = client_telegram
            if notes:
                data['notes'] = notes
            
            # Исправляем кодировку
            fixed_data = self.encoding_fixer.fix_dict_encoding(data)
            
            response = self.session.post(
                f"{self.base_url}/api/licenses",
                json=fixed_data,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                return {'success': False, 'error': 'Неверный API ключ'}
                
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Ошибка создания лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_license(self, license_key: str, **kwargs) -> Dict:
        """
        Обновить данные лицензии
        
        Args:
            license_key: Ключ лицензии
            **kwargs: Поля для обновления
            
        Returns:
            Dict: Результат обновления
        """
        try:
            # Исправляем кодировку данных
            fixed_data = self.encoding_fixer.fix_dict_encoding(kwargs)
            
            response = self.session.put(
                f"{self.base_url}/api/licenses/{license_key}",
                json=fixed_data,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                return {'success': False, 'error': 'Неверный API ключ'}
                
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Ошибка обновления лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_license(self, license_key: str) -> Dict:
        """
        Удалить лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Dict: Результат удаления
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/api/licenses/{license_key}",
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                return {'success': False, 'error': 'Неверный API ключ'}
                
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Ошибка удаления лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def block_license(self, license_key: str, reason: str = None) -> Dict:
        """
        Заблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            reason: Причина блокировки
            
        Returns:
            Dict: Результат блокировки
        """
        try:
            data = {'status': 'blocked'}
            if reason:
                data['block_reason'] = reason
            
            return self.update_license(license_key, **data)
            
        except Exception as e:
            print(f"Ошибка блокировки лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def unblock_license(self, license_key: str) -> Dict:
        """
        Разблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Dict: Результат разблокировки
        """
        try:
            return self.update_license(license_key, status='active', block_reason='')
            
        except Exception as e:
            print(f"Ошибка разблокировки лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def extend_license(self, license_key: str, months: int) -> Dict:
        """
        Продлить лицензию
        
        Args:
            license_key: Ключ лицензии
            months: Количество месяцев
            
        Returns:
            Dict: Результат продления
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/licenses/{license_key}/extend",
                json={'months': months},
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                return {'success': False, 'error': 'Неверный API ключ'}
                
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Ошибка продления лицензии: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_statistics(self) -> Dict:
        """
        Получить статистику по лицензиям
        
        Returns:
            Dict: Статистика
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/statistics",
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                print("ОШИБКА: Неверный API ключ для статистики")
                return {}
                
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('statistics', {})
            return {}
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}
    
    def get_events(self, limit: int = 100) -> List[Dict]:
        """
        Получить события
        
        Args:
            limit: Максимальное количество событий
            
        Returns:
            List[Dict]: Список событий
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/events",
                params={'limit': limit},
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                print("ОШИБКА: Неверный API ключ для событий")
                return []
                
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                events = data.get('events', [])
                # Исправляем кодировку
                return [self.encoding_fixer.fix_dict_encoding(event) for event in events]
            return []
            
        except Exception as e:
            print(f"Ошибка получения событий: {e}")
            return []
    
    def activate_license(self, license_key: str, owner_name: str, 
                        account_number: int, broker_server: str,
                        initial_balance: float = 0) -> Dict:
        """
        Активировать лицензию (вызывается роботом)
        
        Args:
            license_key: Ключ лицензии
            owner_name: Имя владельца счета
            account_number: Номер счета
            broker_server: Сервер брокера
            initial_balance: Начальный баланс
            
        Returns:
            Dict: Результат активации
        """
        try:
            data = {
                'key': license_key,
                'account': account_number,
                'broker': broker_server,
                'account_owner': owner_name,
                'balance': initial_balance,
                'robot_version': '1.6',
                'fingerprint': f"{account_number}_{broker_server}"
            }
            
            response = self.session.post(
                f"{self.base_url}/activate",
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Ошибка активации лицензии: {e}")
            return {'success': False, 'error': str(e)}