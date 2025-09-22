"""
Модель статистики
Подсчёт и анализ данных по лицензиям
ИСПРАВЛЕНО: Баланс считается только для реальных счетов
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class Statistics:
    """Модель для статистики лицензий"""
    
    def __init__(self, licenses: List = None):
        """
        Инициализация статистики
        
        Args:
            licenses: Список лицензий для анализа
        """
        self.licenses = licenses or []
        self._stats = self._calculate()
    
    def _calculate(self) -> Dict[str, Any]:
        """Рассчитать всю статистику"""
        stats = {
            # Количество
            'total': len(self.licenses),
            'active': 0,
            'expired': 0,
            'blocked': 0,
            'created': 0,
            
            # Финансы (только реальные счета!)
            'total_balance': 0.0,
            'average_balance': 0.0,
            'max_balance': 0.0,
            'min_balance': float('inf'),
            'real_accounts_count': 0,  # Количество реальных счетов
            'demo_accounts_count': 0,  # Количество демо счетов
            
            # Счета
            'total_accounts': 0,
            'unique_brokers': set(),
            
            # Сроки
            'expiring_soon': 0,      # Истекают в ближайшие 7 дней
            'expiring_critical': 0,   # Истекают в ближайшие 3 дня
            'expired_recently': 0,     # Истекли в последние 30 дней
            
            # Активность
            'activated_this_month': 0,
            'checked_today': 0,
            'never_checked': 0,
            
            # Клиенты
            'unique_clients': set(),
            'clients_with_telegram': 0,
            
            # Проблемы
            'problems': []
        }
        
        if not self.licenses:
            stats['min_balance'] = 0.0
            return stats
        
        real_balances = []  # Балансы только реальных счетов
        all_balances = []   # Все балансы для статистики
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for license in self.licenses:
            # Получаем статус
            if hasattr(license, 'status'):
                status = license.status if isinstance(license.status, str) else str(license.status.value)
            else:
                status = 'unknown'
            
            # Подсчёт по статусам
            if status == 'active':
                stats['active'] += 1
                
                # Проверка сроков
                if hasattr(license, 'days_left') and license.days_left >= 0:
                    if license.days_left <= 3:
                        stats['expiring_critical'] += 1
                        stats['problems'].append({
                            'type': 'critical',
                            'message': f"Лицензия {license.key} истекает через {license.days_left} дн.",
                            'license': license
                        })
                    elif license.days_left <= 7:
                        stats['expiring_soon'] += 1
                        stats['problems'].append({
                            'type': 'warning',
                            'message': f"Лицензия {license.key} истекает через {license.days_left} дн.",
                            'license': license
                        })
                        
            elif status == 'expired':
                stats['expired'] += 1
                
                # Проверка недавно истекших
                if hasattr(license, 'expiry_date') and license.expiry_date:
                    expiry = license.expiry_date
                    if hasattr(expiry, 'tzinfo') and expiry.tzinfo is not None:
                        expiry = expiry.replace(tzinfo=None)
                    
                    delta = now - expiry
                    if delta.days <= 30:
                        stats['expired_recently'] += 1
                        
            elif status == 'blocked':
                stats['blocked'] += 1
                stats['problems'].append({
                    'type': 'info',
                    'message': f"Лицензия {license.key} заблокирована",
                    'license': license
                })
                
            elif status == 'created':
                stats['created'] += 1
            
            # Определяем тип счета
            account_type = getattr(license, 'account_type', 'real')
            if account_type not in ['real', 'demo']:
                # Если тип не указан, определяем по балансу и брокеру
                # Демо счета обычно имеют большие балансы (>100k)
                balance = 0
                if hasattr(license, 'balance'):
                    balance = license.balance or 0
                elif hasattr(license, 'last_balance'):
                    balance = license.last_balance or 0
                
                # Если баланс больше 100k - скорее всего демо
                if balance > 100000:
                    account_type = 'demo'
                else:
                    account_type = 'real'
            
            # Подсчет типов счетов
            if account_type == 'real':
                stats['real_accounts_count'] += 1
            else:
                stats['demo_accounts_count'] += 1
            
            # Финансы
            balance = 0
            if hasattr(license, 'balance'):
                balance = license.balance or 0
            elif hasattr(license, 'last_balance'):
                balance = license.last_balance or 0
            
            if balance > 0:
                all_balances.append(balance)
                
                # ВАЖНО: Добавляем в общий баланс только если это РЕАЛЬНЫЙ счет
                if account_type == 'real':
                    real_balances.append(balance)
                    stats['total_balance'] += balance
                    stats['max_balance'] = max(stats['max_balance'], balance)
                    stats['min_balance'] = min(stats['min_balance'], balance)
                    
                    # Проверка низкого баланса для активных реальных счетов
                    if balance < 100 and status == 'active':
                        stats['problems'].append({
                            'type': 'warning',
                            'message': f"Низкий баланс у {license.client_name}: ${balance:.0f}",
                            'license': license
                        })
            
            # Счета
            if hasattr(license, 'account_number') and license.account_number:
                stats['total_accounts'] += 1
            
            # Брокеры
            broker = None
            if hasattr(license, 'broker'):
                broker = license.broker
            elif hasattr(license, 'broker_name'):
                broker = license.broker_name
                
            if broker:
                stats['unique_brokers'].add(broker)
            
            # Активность
            if hasattr(license, 'activation_date') and license.activation_date:
                activation = license.activation_date
                if hasattr(activation, 'tzinfo') and activation.tzinfo is not None:
                    activation = activation.replace(tzinfo=None)
                
                if activation >= month_ago:
                    stats['activated_this_month'] += 1
            
            if hasattr(license, 'last_check') and license.last_check:
                last_check = license.last_check
                if hasattr(last_check, 'tzinfo') and last_check.tzinfo is not None:
                    last_check = last_check.replace(tzinfo=None)
                
                if last_check >= today_start:
                    stats['checked_today'] += 1
            elif status == 'active':
                stats['never_checked'] += 1
                stats['problems'].append({
                    'type': 'info',
                    'message': f"Лицензия {license.key} не проверялась",
                    'license': license
                })
            
            # Клиенты
            if hasattr(license, 'client_name') and license.client_name:
                stats['unique_clients'].add(license.client_name)
            
            if hasattr(license, 'client_telegram') and license.client_telegram:
                stats['clients_with_telegram'] += 1
        
        # Вычисляем средний баланс только для РЕАЛЬНЫХ счетов
        if real_balances:
            stats['average_balance'] = stats['total_balance'] / len(real_balances)
        else:
            stats['average_balance'] = 0.0
        
        if stats['min_balance'] == float('inf'):
            stats['min_balance'] = 0.0
        
        # Преобразуем множества в количество
        stats['unique_brokers_count'] = len(stats['unique_brokers'])
        stats['unique_clients_count'] = len(stats['unique_clients'])
        
        # Добавляем общий баланс в правильном формате для отображения
        # Это будет использоваться в карточке "ОБЩИЙ БАЛАНС"
        stats['balance'] = stats['total_balance']  # Для совместимости со stats_panel
        
        # Убираем множества из финального результата
        del stats['unique_brokers']
        del stats['unique_clients']
        
        return stats
    
    def update(self, licenses: List):
        """
        Обновить статистику с новым списком лицензий
        
        Args:
            licenses: Новый список лицензий
        """
        self.licenses = licenses
        self._stats = self._calculate()
    
    @property
    def total(self) -> int:
        """Общее количество лицензий"""
        return self._stats.get('total', 0)
    
    @property
    def active(self) -> int:
        """Количество активных лицензий"""
        return self._stats.get('active', 0)
    
    @property
    def expired(self) -> int:
        """Количество истёкших лицензий"""
        return self._stats.get('expired', 0)
    
    @property
    def blocked(self) -> int:
        """Количество заблокированных лицензий"""
        return self._stats.get('blocked', 0)
    
    @property
    def created(self) -> int:
        """Количество не активированных лицензий"""
        return self._stats.get('created', 0)
    
    @property
    def total_balance(self) -> float:
        """Общий баланс (только реальные счета!)"""
        return self._stats.get('total_balance', 0.0)
    
    @property
    def average_balance(self) -> float:
        """Средний баланс (только реальные счета!)"""
        return self._stats.get('average_balance', 0.0)
    
    @property
    def max_balance(self) -> float:
        """Максимальный баланс (только реальные счета!)"""
        return self._stats.get('max_balance', 0.0)
    
    @property
    def min_balance(self) -> float:
        """Минимальный баланс (только реальные счета!)"""
        return self._stats.get('min_balance', 0.0)
    
    @property
    def real_accounts_count(self) -> int:
        """Количество реальных счетов"""
        return self._stats.get('real_accounts_count', 0)
    
    @property
    def demo_accounts_count(self) -> int:
        """Количество демо счетов"""
        return self._stats.get('demo_accounts_count', 0)
    
    @property
    def problems(self) -> List[Dict]:
        """Список проблем"""
        return self._stats.get('problems', [])
    
    @property
    def expiring_soon(self) -> int:
        """Количество скоро истекающих"""
        return self._stats.get('expiring_soon', 0)
    
    @property
    def expiring_critical(self) -> int:
        """Количество критически истекающих"""
        return self._stats.get('expiring_critical', 0)
    
    @property
    def has_critical_problems(self) -> bool:
        """Есть ли критические проблемы"""
        return any(p['type'] == 'critical' for p in self.problems)
    
    @property
    def has_warnings(self) -> bool:
        """Есть ли предупреждения"""
        return any(p['type'] == 'warning' for p in self.problems)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Получить краткую сводку для UI
        
        Returns:
            Dict: Основные показатели
        """
        return {
            'total': self.total,
            'active': self.active,
            'expired': self.expired,
            'blocked': self.blocked,
            'created': self.created,
            'balance': self.total_balance,  # Только реальные!
            'accounts': self._stats.get('total_accounts', 0),
            'real_accounts': self.real_accounts_count,
            'demo_accounts': self.demo_accounts_count,
            'expiring_soon': self.expiring_soon,
            'problems_count': len(self.problems)
        }
    
    def get_detailed(self) -> Dict[str, Any]:
        """
        Получить детальную статистику
        
        Returns:
            Dict: Полная статистика
        """
        return self._stats.copy()
    
    def get_health_score(self) -> float:
        """
        Рассчитать оценку здоровья системы лицензий
        
        Returns:
            float: Оценка от 0 до 100
        """
        if self.total == 0:
            return 100.0
        
        score = 100.0
        
        # Штрафы за проблемы
        score -= self.expiring_critical * 10
        score -= self.expiring_soon * 5
        score -= self._stats.get('expired_recently', 0) * 3
        score -= self._stats.get('never_checked', 0) * 2
        
        # Штраф за долю проблемных лицензий
        if self.total > 0:
            problem_ratio = (self.expired + self.blocked) / self.total
            score -= problem_ratio * 30
        
        # Бонус за активность
        checked_today = self._stats.get('checked_today', 0)
        if checked_today > 0:
            score += min(10, checked_today)
        
        return max(0.0, min(100.0, score))
    
    def get_trends(self) -> Dict[str, str]:
        """
        Получить тренды
        
        Returns:
            Dict: Описание трендов
        """
        trends = {}
        
        # Тренд активации
        activated_this_month = self._stats.get('activated_this_month', 0)
        if self.total > 0 and activated_this_month > self.total * 0.1:
            trends['activation'] = 'growing'
        elif activated_this_month == 0:
            trends['activation'] = 'stagnant'
        else:
            trends['activation'] = 'normal'
        
        # Тренд проблем
        if self.has_critical_problems:
            trends['problems'] = 'critical'
        elif self.has_warnings:
            trends['problems'] = 'warning'
        else:
            trends['problems'] = 'good'
        
        # Тренд использования
        checked_today = self._stats.get('checked_today', 0)
        if self.active > 0:
            usage_ratio = checked_today / self.active
            if usage_ratio > 0.5:
                trends['usage'] = 'high'
            elif usage_ratio > 0:
                trends['usage'] = 'normal'
            else:
                trends['usage'] = 'low'
        else:
            trends['usage'] = 'none'
        
        # Тренд финансов (только реальные счета!)
        if self.average_balance > 10000:
            trends['finance'] = 'excellent'
        elif self.average_balance > 1000:
            trends['finance'] = 'good'
        elif self.average_balance > 100:
            trends['finance'] = 'normal'
        else:
            trends['finance'] = 'low'
        
        return trends
    
    def get_alerts(self) -> List[str]:
        """
        Получить список важных предупреждений
        
        Returns:
            List[str]: Список предупреждений
        """
        alerts = []
        
        if self.expiring_critical > 0:
            alerts.append(f"⚠️ {self.expiring_critical} лицензий истекают в ближайшие 3 дня!")
        
        if self.expiring_soon > 0:
            alerts.append(f"📅 {self.expiring_soon} лицензий истекают в ближайшие 7 дней")
        
        expired_recently = self._stats.get('expired_recently', 0)
        if expired_recently > 0:
            alerts.append(f"❌ {expired_recently} лицензий истекли за последний месяц")
        
        never_checked = self._stats.get('never_checked', 0)
        if never_checked > 0:
            alerts.append(f"❓ {never_checked} лицензий ни разу не проверялись")
        
        # Подсчет проблем с балансом (только реальные счета)
        low_balance_count = sum(1 for p in self.problems 
                                if 'баланс' in p.get('message', '').lower())
        if low_balance_count > 0:
            alerts.append(f"💰 {low_balance_count} реальных счетов с низким балансом")
        
        # Информация о типах счетов
        if self.real_accounts_count > 0 and self.demo_accounts_count > 0:
            alerts.append(f"📊 Реальных: {self.real_accounts_count}, Демо: {self.demo_accounts_count}")
        
        # Проблемы с брокерами
        unique_brokers_count = self._stats.get('unique_brokers_count', 0)
        if unique_brokers_count > 10:
            alerts.append(f"🏦 Используется много разных брокеров: {unique_brokers_count}")
        
        return alerts
    
    def format_balance(self, balance: float = None) -> str:
        """
        Форматировать баланс
        
        Args:
            balance: Сумма для форматирования (если None, берется total_balance)
            
        Returns:
            str: Форматированная сумма
        """
        if balance is None:
            balance = self.total_balance
            
        if balance >= 1000000:
            return f"${balance/1000000:.1f}M"
        elif balance >= 1000:
            return f"${balance/1000:.1f}K"
        else:
            return f"${balance:.0f}"
    
    def get_report(self) -> str:
        """
        Получить текстовый отчет
        
        Returns:
            str: Форматированный отчет
        """
        health = self.get_health_score()
        trends = self.get_trends()
        
        report = f"""
СТАТИСТИКА ЛИЦЕНЗИЙ
{'='*40}
Всего лицензий: {self.total}
  • Активные: {self.active}
  • Истекшие: {self.expired}
  • Заблокированные: {self.blocked}
  • Не активированные: {self.created}

ФИНАНСЫ (ТОЛЬКО РЕАЛЬНЫЕ СЧЕТА)
{'='*40}
Общий баланс: {self.format_balance()}
Средний баланс: {self.format_balance(self.average_balance)}
Максимальный: {self.format_balance(self.max_balance)}
Минимальный: {self.format_balance(self.min_balance)}
Реальных счетов: {self.real_accounts_count}
Демо счетов: {self.demo_accounts_count}

АКТИВНОСТЬ
{'='*40}
Проверено сегодня: {self._stats.get('checked_today', 0)}
Активировано в этом месяце: {self._stats.get('activated_this_month', 0)}
Никогда не проверялись: {self._stats.get('never_checked', 0)}

ПРОБЛЕМЫ
{'='*40}
Истекают в ближайшие 3 дня: {self.expiring_critical}
Истекают в ближайшие 7 дней: {self.expiring_soon}
Истекли за последний месяц: {self._stats.get('expired_recently', 0)}

ОЦЕНКА ЗДОРОВЬЯ
{'='*40}
Общая оценка: {health:.1f}%
Тренд активации: {trends.get('activation', 'normal')}
Тренд использования: {trends.get('usage', 'normal')}
Тренд проблем: {trends.get('problems', 'good')}
"""
        return report
    
    def __str__(self) -> str:
        """Строковое представление"""
        return (f"Statistics(total={self.total}, active={self.active}, "
                f"expired={self.expired}, real_balance={self.format_balance()})")
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"<Statistics licenses={self.total} real_accounts={self.real_accounts_count} health={self.get_health_score():.1f}%>"