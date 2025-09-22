"""
Модель лицензии
Представление данных лицензии с методами
ИСПРАВЛЕНО: Корректный расчет оставшихся дней для активных лицензий
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class LicenseStatus(Enum):
    """Статусы лицензии"""
    CREATED = 'created'      # Создана, но не активирована
    ACTIVE = 'active'        # Активна
    EXPIRED = 'expired'      # Истекла
    BLOCKED = 'blocked'      # Заблокирована


class LicenseUrgency(Enum):
    """Уровни срочности"""
    CRITICAL = 'critical'    # Критично (<=3 дня)
    WARNING = 'warning'      # Предупреждение (<=7 дней)
    ATTENTION = 'attention'  # Внимание (<=30 дней)
    NORMAL = 'normal'        # Нормально (>30 дней)
    NONE = 'none'           # Не применимо


class License:
    """Модель лицензии"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Инициализация лицензии
        
        Args:
            data: Словарь с данными лицензии
        """
        # Основные поля
        self.key: str = data.get('license_key', '')
        self.license_key = self.key  # Для совместимости
        self.client_name: str = data.get('client_name', '')
        self.client_contact: str = data.get('client_contact', '')
        self.client_telegram: str = data.get('client_telegram', '')
        self.notes: str = data.get('notes', '')
        
        # Статус
        status_str = data.get('status', 'created')
        try:
            self.status = status_str.lower() if isinstance(status_str, str) else 'created'
        except:
            self.status = 'created'
        
        # Счёт - ИСПРАВЛЕНО: правильная обработка владельца счета
        self.account_number: Optional[str] = str(data.get('account_number', '')) if data.get('account_number') else None
        
        # ИСПРАВЛЕНО: Обработка владельца счета
        owner_raw = data.get('account_owner', '')
        if owner_raw and owner_raw not in ['None', 'null', '', None]:
            # Очищаем от мусора
            self.account_owner = str(owner_raw).strip()
            # Если владелец не был передан роботом, используем placeholder
            if self.account_owner in ['', 'None']:
                self.account_owner = f"Счет {self.account_number}" if self.account_number else "Не указан"
        else:
            # Если счет активирован но владелец не передан
            if self.account_number:
                self.account_owner = f"Счет {self.account_number}"
            else:
                self.account_owner = "Не активирован"
        
        self.broker: str = data.get('broker_name', '')
        self.broker_name = self.broker  # Для совместимости
        self.account_type: str = data.get('account_type', '')
        self.balance: float = float(data.get('last_balance', 0) or 0)
        self.last_balance = self.balance  # Для совместимости
        
        # Даты
        self.created_date = self._parse_date(data.get('created_date'))
        self.activation_date = self._parse_date(data.get('activation_date'))
        self.expiry_date = self._parse_date(data.get('expiry_date'))
        self.last_check = self._parse_date(data.get('last_check'))
        
        # Версии и технические данные
        self.robot_name: str = data.get('robot_name', '')
        self.robot_version: str = data.get('robot_version', '')
        self.terminal_version: str = data.get('terminal_version', '')
        self.activation_ip: str = data.get('activation_ip', '')
        self.last_ip: str = data.get('last_ip', '')
        self.fingerprint: str = data.get('fingerprint', '')
        
        # Статистика
        self.check_count: int = int(data.get('check_count', 0) or 0)
        self.failed_checks: int = int(data.get('failed_checks', 0) or 0)
        self.heartbeat_count: int = int(data.get('heartbeat_count', 0) or 0)
        
        # ИСПРАВЛЕНО: Если days_left уже вычислен на сервере - используем его
        if 'days_left' in data and data['days_left'] is not None:
            self.days_left = int(data['days_left'])
        else:
            self.days_left = -1
        
        # Вычисляемые поля
        self._calculate_fields()
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Парсинг даты из различных форматов"""
        if not date_str:
            return None
        
        if isinstance(date_str, datetime):
            # Если уже datetime и есть timezone - убираем её
            if date_str.tzinfo is not None:
                return date_str.replace(tzinfo=None)
            return date_str
        
        try:
            # ISO формат с timezone
            if 'T' in str(date_str):
                # Убираем микросекунды если есть
                date_str = str(date_str).split('.')[0]
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'
                
                # Пробуем с timezone
                try:
                    dt = datetime.fromisoformat(date_str)
                    # ВАЖНО: убираем timezone
                    if dt.tzinfo is not None:
                        dt = dt.replace(tzinfo=None)
                    return dt
                except:
                    # Пробуем без timezone
                    if '+' in date_str or 'Z' in date_str:
                        date_str = date_str.split('+')[0].split('Z')[0]
                    return datetime.fromisoformat(date_str)
            
            # Другие форматы
            return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
        except:
            # Последняя попытка
            try:
                date_only = str(date_str).split('T')[0].split(' ')[0]
                return datetime.strptime(date_only, '%Y-%m-%d')
            except:
                return None
    
    def _calculate_fields(self):
        """Вычислить дополнительные поля"""
        # Используем timezone-naive datetime для сравнения
        now = datetime.now()
        
        # ИСПРАВЛЕНО: Правильный расчет дней для активных лицензий
        # Если days_left не был установлен ранее - вычисляем
        if self.days_left == -1:
            if self.expiry_date:
                # Убеждаемся, что обе даты timezone-naive
                expiry = self.expiry_date
                if expiry.tzinfo is not None:
                    expiry = expiry.replace(tzinfo=None)
                
                delta = expiry - now
                self.days_left = max(0, delta.days)
            else:
                # Если нет даты истечения
                if self.status == 'created':
                    self.days_left = -1  # Не активирована
                else:
                    self.days_left = 999  # Бессрочная
        
        # Флаги состояния
        self.is_active = self.status == 'active'
        self.is_expired = self.status == 'expired'
        self.is_blocked = self.status == 'blocked'
        self.is_created = self.status == 'created'
        
        # ИСПРАВЛЕНО: Текстовое представление оставшихся дней
        if self.status == 'created':
            self.days_left_text = '(не активирована)'
        elif self.status == 'expired':
            self.days_left_text = 'Истекла'
        elif self.status == 'blocked':
            self.days_left_text = 'Заблокирована'
        elif self.expiry_date and self.is_active:
            if self.days_left == 0:
                self.days_left_text = 'Истекает сегодня!'
            elif self.days_left < 0:
                self.days_left_text = 'Истекла'
            else:
                self.days_left_text = f'{self.days_left} дн.'
        else:
            self.days_left_text = 'Бессрочная'
        
        # Уровень срочности
        if self.is_active:
            if self.days_left <= 3:
                self.urgency = LicenseUrgency.CRITICAL
            elif self.days_left <= 7:
                self.urgency = LicenseUrgency.WARNING
            elif self.days_left <= 30:
                self.urgency = LicenseUrgency.ATTENTION
            else:
                self.urgency = LicenseUrgency.NORMAL
        else:
            self.urgency = LicenseUrgency.NONE
        
        # Проблемы
        self.has_problems = False
        self.problems = []
        
        if self.is_active:
            # Проверка критичного срока
            if self.days_left <= 3:
                self.has_problems = True
                self.problems.append('Срок истекает!')
            
            # Проверка баланса
            if self.balance < 100:
                self.has_problems = True
                self.problems.append('Низкий баланс')
            
            # Проверка активности
            if self.last_check:
                # Убеждаемся, что last_check timezone-naive
                last_check = self.last_check
                if last_check.tzinfo is not None:
                    last_check = last_check.replace(tzinfo=None)
                
                days_since_check = (now - last_check).days
                if days_since_check > 7:
                    self.has_problems = True
                    self.problems.append('Давно не проверялась')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать модель в словарь для совместимости со старым кодом
        
        Returns:
            Dict: Словарь с данными лицензии
        """
        return {
            'license_key': self.key,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'client_telegram': self.client_telegram,
            'account_number': self.account_number,
            'account_owner': self.account_owner,
            'broker_name': self.broker,
            'last_balance': self.balance,
            'status': self.status,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'activation_date': self.activation_date.isoformat() if self.activation_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'days_left': self.days_left,
            'days_left_text': self.days_left_text,  # Добавлено
            'notes': self.notes,
            'robot_name': self.robot_name,
            'robot_version': self.robot_version,
            'terminal_version': self.terminal_version,
            'activation_ip': self.activation_ip,
            'last_ip': self.last_ip,
            'fingerprint': self.fingerprint,
            'check_count': self.check_count,
            'failed_checks': self.failed_checks,
            'heartbeat_count': self.heartbeat_count,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'is_blocked': self.is_blocked,
            'is_created': self.is_created,
            'has_problems': self.has_problems,
            'problems': self.problems,
            'urgency': self.urgency.value if hasattr(self.urgency, 'value') else str(self.urgency)
        }
    
    def get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            'active': 'Активна',
            'expired': 'Истекла',
            'blocked': 'Заблокирована',
            'created': 'Создана'
        }
        return status_map.get(self.status, 'Неизвестно')
    
    def get_urgency_color(self) -> str:
        """Получить цвет для уровня срочности"""
        color_map = {
            LicenseUrgency.CRITICAL: '#ff0040',   # Красный
            LicenseUrgency.WARNING: '#ff6b35',    # Оранжевый
            LicenseUrgency.ATTENTION: '#ffd700',  # Золотой
            LicenseUrgency.NORMAL: '#00ff41',     # Зеленый
            LicenseUrgency.NONE: '#606060'        # Серый
        }
        return color_map.get(self.urgency, '#606060')
    
    def get_days_left_display(self) -> str:
        """Получить отображение оставшихся дней"""
        return self.days_left_text
    
    def can_activate(self) -> bool:
        """Можно ли активировать лицензию"""
        return self.is_created
    
    def can_block(self) -> bool:
        """Можно ли заблокировать лицензию"""
        return self.is_active or self.is_created
    
    def can_unblock(self) -> bool:
        """Можно ли разблокировать лицензию"""
        return self.is_blocked
    
    def can_extend(self) -> bool:
        """Можно ли продлить лицензию"""
        return self.is_active or self.is_expired
    
    def format_balance(self) -> str:
        """Форматировать баланс"""
        if self.balance >= 1000000:
            return f"${self.balance/1000000:.1f}M"
        elif self.balance >= 1000:
            return f"${self.balance/1000:.1f}K"
        else:
            return f"${self.balance:.0f}"
    
    def get_broker_short(self) -> str:
        """Получить сокращенное название брокера"""
        if not self.broker:
            return 'Н/Д'
        
        # Известные брокеры
        broker_map = {
            'Alpari': 'ALP',
            'RoboForex': 'RFX',
            'FXOpen': 'FXO',
            'Exness': 'EXN',
            'XM': 'XM',
            'FBS': 'FBS',
            'InstaForex': 'INS',
            'FXTM': 'FXTM',
            'HotForex': 'HFX',
            'IC Markets': 'ICM'
        }
        
        for full_name, short_name in broker_map.items():
            if full_name.lower() in self.broker.lower():
                return short_name
        
        # Если не нашли, берем первые 3 буквы
        return self.broker[:3].upper() if len(self.broker) >= 3 else self.broker.upper()
    
    def __str__(self) -> str:
        """Строковое представление"""
        return f"License({self.key}, {self.client_name}, {self.status})"
    
    def __repr__(self) -> str:
        """Отладочное представление"""
        return f"<License key={self.key} client={self.client_name} status={self.status}>"