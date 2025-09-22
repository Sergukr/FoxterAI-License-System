"""
API для работы с лицензиями
"""

from typing import List, Dict, Optional
from datetime import datetime
from .base_client import BaseAPIClient


class LicensesAPI(BaseAPIClient):
    """API для управления лицензиями"""
    
    def get_all(self) -> List[Dict]:
        """
        Получить все лицензии
        
        Returns:
            List[Dict]: Список всех лицензий
        """
        try:
            response = self.get('/api/licenses')
            if response.get('success'):
                licenses = response.get('licenses', [])
                # Добавляем вычисляемые поля
                return [self._enrich_license(lic) for lic in licenses]
            return []
        except Exception as e:
            print(f"Ошибка получения лицензий: {e}")
            return []
    
    def get_by_key(self, license_key: str) -> Optional[Dict]:
        """
        Получить лицензию по ключу
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Optional[Dict]: Данные лицензии или None
        """
        try:
            response = self.get(f'/api/licenses/{license_key}')
            if response.get('success'):
                return self._enrich_license(response.get('license'))
            return None
        except Exception:
            return None
    
    def create(self, client_name: str, client_contact: str = '',
               client_telegram: str = '', months: int = 1,
               notes: str = '') -> Dict:
        """
        Создать новую лицензию
        
        Args:
            client_name: Имя клиента
            client_contact: Контакт клиента
            client_telegram: Telegram клиента
            months: Количество месяцев
            notes: Заметки
            
        Returns:
            Dict: Результат создания с ключом лицензии
        """
        data = {
            'client_name': client_name,
            'client_contact': client_contact,
            'client_telegram': client_telegram,
            'months': months,
            'notes': notes
        }
        
        try:
            response = self.post('/api/licenses/create', data)
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update(self, license_key: str, **fields) -> Dict:
        """
        Обновить данные лицензии
        
        Args:
            license_key: Ключ лицензии
            **fields: Поля для обновления
            
        Returns:
            Dict: Результат обновления
        """
        # Разрешённые поля для обновления
        allowed = [
            'client_name', 'client_contact', 'client_telegram',
            'notes', 'status'
        ]
        
        # Фильтруем только разрешённые поля
        data = {k: v for k, v in fields.items() if k in allowed}
        
        if not data:
            return {
                'success': False,
                'error': 'Нет полей для обновления'
            }
        
        try:
            response = self.put(f'/api/licenses/{license_key}', data)
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete(self, license_key: str) -> Dict:
        """
        Удалить лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Dict: Результат удаления
        """
        try:
            response = self.delete(f'/api/licenses/{license_key}')
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def block(self, license_key: str) -> Dict:
        """
        Заблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Dict: Результат блокировки
        """
        return self.update(license_key, status='blocked')
    
    def unblock(self, license_key: str) -> Dict:
        """
        Разблокировать лицензию
        
        Args:
            license_key: Ключ лицензии
            
        Returns:
            Dict: Результат разблокировки
        """
        return self.update(license_key, status='active')
    
    def extend(self, license_key: str, months: int) -> Dict:
        """
        Продлить лицензию
        
        Args:
            license_key: Ключ лицензии
            months: На сколько месяцев продлить
            
        Returns:
            Dict: Результат продления
        """
        try:
            response = self.post(f'/api/licenses/{license_key}/extend', 
                                {'months': months})
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check(self, license_key: str, account_number: int,
              balance: float = 0, robot_version: str = '1.6') -> Dict:
        """
        Проверка лицензии (вызывается из MT4)
        
        Args:
            license_key: Ключ лицензии
            account_number: Номер торгового счёта
            balance: Текущий баланс
            robot_version: Версия робота
            
        Returns:
            Dict: Результат проверки
        """
        data = {
            'account_number': account_number,
            'balance': balance,
            'robot_version': robot_version
        }
        
        try:
            response = self.post(f'/api/licenses/{license_key}/check', data)
            return response
        except Exception as e:
            return {
                'success': False,
                'valid': False,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict:
        """
        Получить статистику по лицензиям
        
        Returns:
            Dict: Статистика
        """
        licenses = self.get_all()
        
        stats = {
            'total': len(licenses),
            'active': 0,
            'expired': 0,
            'blocked': 0,
            'created': 0,
            'total_balance': 0,
            'average_balance': 0,
            'total_accounts': 0
        }
        
        for license in licenses:
            status = license.get('status', '').lower()
            
            if status == 'active':
                stats['active'] += 1
            elif status == 'expired':
                stats['expired'] += 1
            elif status == 'blocked':
                stats['blocked'] += 1
            elif status == 'created':
                stats['created'] += 1
            
            balance = license.get('last_balance', 0)
            if balance > 0:
                stats['total_balance'] += balance
            
            if license.get('account_number'):
                stats['total_accounts'] += 1
        
        if stats['total_accounts'] > 0:
            stats['average_balance'] = stats['total_balance'] / stats['total_accounts']
        
        return stats
    
    def search(self, query: str) -> List[Dict]:
        """
        Поиск лицензий
        
        Args:
            query: Поисковый запрос
            
        Returns:
            List[Dict]: Найденные лицензии
        """
        all_licenses = self.get_all()
        query_lower = query.lower()
        
        results = []
        for license in all_licenses:
            # Поиск по основным полям
            search_fields = [
                'license_key', 'client_name', 'client_contact',
                'client_telegram', 'account_number', 'broker_name'
            ]
            
            for field in search_fields:
                value = str(license.get(field, '')).lower()
                if query_lower in value:
                    results.append(license)
                    break
        
        return results
    
    def _enrich_license(self, license: Dict) -> Dict:
        """
        Добавить вычисляемые поля к лицензии
        
        Args:
            license: Данные лицензии
            
        Returns:
            Dict: Обогащённые данные
        """
        # Копируем оригинальные данные
        enriched = license.copy()
        
        # Добавляем форматированные даты
        date_fields = ['created_date', 'activation_date', 'expiry_date', 'last_check']
        for field in date_fields:
            if enriched.get(field):
                # Сохраняем оригинал
                enriched[f'{field}_raw'] = enriched[field]
                # Добавляем форматированную версию
                enriched[f'{field}_formatted'] = self._format_datetime(enriched[field])
                # Добавляем короткую версию (только дата)
                enriched[f'{field}_short'] = self._format_date(enriched[field])
        
        # Вычисляем дни до истечения
        if enriched.get('expiry_date') and enriched.get('status') == 'active':
            days_left = self._calculate_days_left(enriched['expiry_date'])
            enriched['days_left'] = days_left
            
            # Добавляем уровень критичности
            if days_left <= 3:
                enriched['urgency'] = 'critical'
            elif days_left <= 7:
                enriched['urgency'] = 'warning'
            elif days_left <= 30:
                enriched['urgency'] = 'attention'
            else:
                enriched['urgency'] = 'normal'
        else:
            enriched['days_left'] = -1
            enriched['urgency'] = 'none'
        
        return enriched
    
    def _format_datetime(self, date_str: str) -> str:
        """Форматировать дату и время"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        except:
            return date_str
    
    def _format_date(self, date_str: str) -> str:
        """Форматировать только дату"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y')
        except:
            if 'T' in date_str:
                return date_str.split('T')[0]
            return date_str[:10] if len(date_str) >= 10 else date_str
    
    def _calculate_days_left(self, expiry_date: str) -> int:
        """Вычислить дни до истечения"""
        try:
            # Парсим дату
            expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            # ВАЖНО: убираем timezone если есть
            if expiry.tzinfo is not None:
                expiry = expiry.replace(tzinfo=None)
            
            now = datetime.now()
            delta = expiry - now
            return max(0, delta.days)
        except:
            return -1