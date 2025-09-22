"""
Компонент таблицы лицензий с премиальным дизайном
Изумрудно-золотая стилистика согласно дизайн-гайду
ИСПРАВЛЕНО: Ошибка Item I001 not found
ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Desktop/ui/components/license_table.py
"""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from themes.dark_theme import DarkTheme


class LicenseTable(ctk.CTkFrame):
    """Премиальная таблица лицензий с hover эффектами и анимациями"""
    
    def __init__(self, parent):
        """
        Инициализация таблицы
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent, fg_color='transparent')
        
        # Данные
        self.licenses = []
        self.filtered_licenses = []
        
        # Callbacks
        self.callbacks = {
            'select': None,
            'double_click': None,
            'context_menu': None
        }
        
        # Текущий фильтр и поиск
        self.current_filter = 'Все'
        self.search_query = ''
        
        # Сортировка
        self.sort_column = None
        self.sort_reverse = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание виджетов таблицы с премиальным стилем"""
        # Контейнер таблицы с эффектом свечения
        self.table_container = ctk.CTkFrame(
            self, 
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            border_width=1,
            border_color=DarkTheme.JADE_GREEN
        )
        self.table_container.pack(fill='both', expand=True)
        
        # Внутренний контейнер для Treeview
        self.tree_frame = ctk.CTkFrame(self.table_container, fg_color='transparent')
        self.tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Колонки таблицы
        columns = (
            'Ключ', 'Клиент', 'Телефон', 'Telegram', 
            'Владелец', 'Счёт', 'Брокер', 'Робот', 'Версия',
            'Баланс', 'Тип', 'Создана', 'Истекает', 'Дней',
            'Статус'
        )
        
        self.tree = ttk.Treeview(
            self.tree_frame, 
            columns=columns,
            show='tree headings',
            height=20,
            selectmode='browse'
        )
        
        # Настройка стилей ПОСЛЕ создания tree
        self._setup_styles()
        
        # Скрываем первую колонку дерева
        self.tree.column('#0', width=0, stretch=False)
        
        # Настройка колонок
        column_widths = {
            'Ключ': 150,
            'Клиент': 120,
            'Телефон': 100,
            'Telegram': 100,
            'Владелец': 120,
            'Счёт': 80,
            'Брокер': 80,
            'Робот': 80,
            'Версия': 60,
            'Баланс': 80,
            'Тип': 50,
            'Создана': 90,
            'Истекает': 90,
            'Дней': 50,
            'Статус': 100
        }
        
        for column in columns:
            self.tree.column(column, width=column_widths.get(column, 100), anchor='center')
            self.tree.heading(column, text=column, command=lambda c=column: self._sort_by_column(c))
        
        # Скроллбары
        vsb = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Настройка весов для растягивания
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Привязка событий
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
    
    def _setup_styles(self):
        """Настройка премиальных стилей таблицы"""
        style = ttk.Style()
        
        # Тёмная тема
        style.theme_use('clam')
        
        # Цвета из темы
        bg_primary = DarkTheme.BG_TERTIARY
        bg_hover = DarkTheme.BG_HOVER
        bg_selected = DarkTheme.JADE_GREEN
        text_primary = DarkTheme.PURE_WHITE
        text_secondary = DarkTheme.WARM_GRAY
        border_color = DarkTheme.BORDER_PRIMARY
        
        # Стиль Treeview
        style.configure(
            'Treeview',
            background=bg_primary,
            foreground=text_primary,
            fieldbackground=bg_primary,
            borderwidth=0,
            font=('Inter', 10)
        )
        
        # Стиль заголовков
        style.configure(
            'Treeview.Heading',
            background=DarkTheme.GRAPHITE_GRAY,
            foreground=DarkTheme.CHAMPAGNE_GOLD,
            font=('Inter', 11, 'bold'),
            borderwidth=1,
            relief='flat'
        )
        
        # Hover эффекты
        style.map(
            'Treeview',
            background=[('selected', bg_selected)],
            foreground=[('selected', DarkTheme.CHARCOAL_BLACK)]
        )
        
        style.map(
            'Treeview.Heading',
            background=[('active', bg_hover)]
        )
        
        # Теги для разных статусов
        self.tree.tag_configure('active', foreground=DarkTheme.STATUS_ACTIVE)
        self.tree.tag_configure('expired', foreground=DarkTheme.STATUS_EXPIRED)
        self.tree.tag_configure('blocked', foreground=DarkTheme.STATUS_BLOCKED)
        self.tree.tag_configure('created', foreground=DarkTheme.STATUS_PENDING)
        self.tree.tag_configure('expiring', foreground=DarkTheme.STATUS_WARNING)
    
    def load_licenses(self, licenses: List):
        """
        Загрузить лицензии в таблицу с премиальными эффектами
        
        Args:
            licenses: Список лицензий (License объекты или словари)
        """
        # Очищаем таблицу
        self.tree.delete(*self.tree.get_children())
        
        # Сохраняем данные
        self.licenses = licenses
        self.filtered_licenses = licenses
        
        # Применяем фильтры
        self._apply_filters()
    
    def _apply_filters(self):
        """Применение фильтров и поиска с анимацией"""
        # Фильтруем данные
        filtered = self.licenses
        
        # Фильтр по статусу
        if self.current_filter != 'Все':
            if self.current_filter == 'Активные':
                filtered = [l for l in filtered if self._get_field(l, 'status') == 'active']
            elif self.current_filter == 'Истекшие':
                filtered = [l for l in filtered if self._get_field(l, 'status') == 'expired']
            elif self.current_filter == 'Заблокированные':
                filtered = [l for l in filtered if self._get_field(l, 'status') == 'blocked']
            elif self.current_filter == 'Не активированные':
                filtered = [l for l in filtered if self._get_field(l, 'status') == 'created']
        
        # Поиск
        if self.search_query:
            query = self.search_query.lower()
            filtered = [l for l in filtered if self._search_in_license(l, query)]
        
        self.filtered_licenses = filtered
        
        # Очищаем и заполняем таблицу
        self.tree.delete(*self.tree.get_children())
        
        for license in filtered:
            self._insert_license(license)
    
    def _insert_license(self, license):
        """Вставка лицензии в таблицу с форматированием"""
        # Извлекаем поля в зависимости от типа данных
        key = self._get_field(license, 'license_key', 'N/A')
        client_name = self._get_field(license, 'client_name', '-')
        phone = self._get_field(license, 'client_contact', '-')
        telegram = self._get_field(license, 'client_telegram', '-')
        owner = self._get_field(license, 'account_owner', 'Не активирован')
        account = self._get_field(license, 'account_number', '-')
        broker = self._get_field(license, 'broker_name', '-')
        robot = self._get_field(license, 'robot_name', '-')
        version = self._get_field(license, 'robot_version', '-')
        balance = self._get_field(license, 'last_balance', 0)
        account_type = self._get_field(license, 'account_type', '-')
        created = self._get_field(license, 'created_date_formatted', 
                                 self._format_date(self._get_field(license, 'created_date')))
        expiry = self._get_field(license, 'expiry_date', '-')
        days_left = self._get_field(license, 'days_left', 999)
        status = self._get_field(license, 'status', 'unknown')
        
        # Форматирование значений
        if phone == 'None' or phone is None:
            phone = '-'
        if telegram == 'None' or telegram is None:
            telegram = '-'
        if owner == 'Не активирован' or owner == 'None' or owner is None:
            owner = 'Не активирован'
        if account == 'None' or account is None or account == '-':
            account = '-'
        if broker == 'None' or broker is None:
            broker = '-'
        if robot == 'None' or robot is None:
            robot = '-'
        if version == 'None' or version is None:
            version = '-'
        
        # Форматируем баланс
        if isinstance(balance, (int, float)):
            balance_str = f'${balance:.2f}'
        else:
            balance_str = '-'
        
        # Форматируем дату истечения
        if expiry and expiry != '-':
            expiry_formatted = self._format_date(expiry)
        else:
            expiry_formatted = '-'
        
        # Форматируем дни до истечения
        if isinstance(days_left, int):
            if days_left == 999:
                days_str = '∞'
            elif days_left < 0:
                days_str = 'Истек'
            else:
                days_str = str(days_left) + 'д'
        else:
            days_str = '-'
        
        # Определяем статус для отображения
        status_display = self._get_status_display(status)
        
        # Определяем тег для строки
        tag = self._get_status_tag(status, days_left)
        
        # Вставляем в таблицу
        values = (
            key, client_name, phone, telegram, 
            owner, account, broker, robot, version,
            balance_str, account_type, created, 
            expiry_formatted, days_str, status_display
        )
        
        # ИСПРАВЛЕНО: Не сохраняем item ID, просто вставляем
        self.tree.insert('', 'end', values=values, tags=(tag,))
    
    def _get_field(self, obj, field_name, default='-'):
        """Безопасное получение поля из объекта или словаря"""
        if hasattr(obj, field_name):
            value = getattr(obj, field_name, default)
        elif hasattr(obj, '__dict__'):
            value = obj.__dict__.get(field_name, default)
        elif isinstance(obj, dict):
            value = obj.get(field_name, default)
        else:
            value = default
        
        # Обработка None значений
        if value is None or value == 'None':
            return default
        
        return value
    
    def _format_date(self, date_str):
        """Форматирование даты"""
        if not date_str or date_str == '-' or date_str == 'None':
            return '-'
        
        try:
            # Пробуем разные форматы
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y']:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    return dt.strftime('%d.%m.%Y')
                except:
                    continue
            return str(date_str)
        except:
            return str(date_str)
    
    def _get_status_display(self, status):
        """Получить отображаемый статус"""
        status_map = {
            'active': '✅ Активна',
            'expired': '⏰ Истекла',
            'blocked': '🔒 Заблокирована',
            'created': '⏳ Не активирована'
        }
        return status_map.get(status, status)
    
    def _get_status_tag(self, status, days_left):
        """Получить тег для статуса"""
        if status == 'blocked':
            return 'blocked'
        elif status == 'expired':
            return 'expired'
        elif status == 'active':
            if isinstance(days_left, int) and 0 < days_left <= 7:
                return 'expiring'
            return 'active'
        elif status == 'created':
            return 'created'
        return ''
    
    def _search_in_license(self, license, query):
        """Поиск в лицензии"""
        searchable_fields = [
            'license_key', 'client_name', 'client_contact', 
            'client_telegram', 'account_owner', 'account_number',
            'broker_name', 'robot_name'
        ]
        
        for field in searchable_fields:
            value = self._get_field(license, field, '')
            if str(value).lower().find(query) != -1:
                return True
        return False
    
    def _sort_by_column(self, column):
        """Сортировка по колонке"""
        # Переключаем направление сортировки
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Пересортировка и обновление
        self._apply_filters()
    
    def _on_select(self, event):
        """Обработка выбора лицензии"""
        selection = self.tree.selection()
        if selection and self.callbacks['select']:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Находим оригинальную лицензию по ключу
            if values:
                license_key = values[0]  # Первое значение - это ключ
                for lic in self.filtered_licenses:
                    if self._get_field(lic, 'license_key') == license_key:
                        self.callbacks['select'](lic)
                        break
    
    def _on_double_click(self, event):
        """Обработка двойного клика"""
        if self.callbacks['double_click']:
            license = self.get_selected_license()
            if license:
                self.callbacks['double_click'](license)
    
    def _on_right_click(self, event):
        """Обработка правого клика"""
        if self.callbacks['context_menu']:
            license = self.get_selected_license()
            if license:
                self.callbacks['context_menu'](license, event)
    
    def set_callbacks(self, select=None, double_click=None, context_menu=None):
        """Установка callback функций"""
        if select:
            self.callbacks['select'] = select
        if double_click:
            self.callbacks['double_click'] = double_click
        if context_menu:
            self.callbacks['context_menu'] = context_menu
    
    def get_selected_license(self):
        """Получить выбранную лицензию"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            if values:
                license_key = values[0]
                for lic in self.filtered_licenses:
                    if self._get_field(lic, 'license_key') == license_key:
                        return lic
        return None
    
    def set_filter(self, filter_type: str):
        """Установить фильтр"""
        self.current_filter = filter_type
        self._apply_filters()
    
    def set_search(self, query: str):
        """Установить поисковый запрос"""
        self.search_query = query
        self._apply_filters()
    
    def refresh(self):
        """Обновить отображение таблицы"""
        self._apply_filters()
    
    def clear(self):
        """Очистить таблицу"""
        self.tree.delete(*self.tree.get_children())
        self.licenses = []
        self.filtered_licenses = []
    
    def update_licenses(self, licenses: List):
        """Обновить лицензии (алиас для load_licenses)"""
        self.load_licenses(licenses)
    
    def get_all_licenses(self):
        """Получить все лицензии"""
        return self.licenses
    
    def get_filtered_licenses(self):
        """Получить отфильтрованные лицензии"""
        return self.filtered_licenses
    
    def select_license_by_key(self, key: str):
        """Выбрать лицензию по ключу"""
        for child in self.tree.get_children():
            item_values = self.tree.item(child)['values']
            if item_values and item_values[0] == key:
                self.tree.selection_set(child)
                self.tree.see(child)
                break
    
    def update_license(self, updated_license):
        """Обновить лицензию в таблице"""
        key = self._get_field(updated_license, 'license_key')
        
        # Обновляем в списке
        for i, lic in enumerate(self.licenses):
            if self._get_field(lic, 'license_key') == key:
                self.licenses[i] = updated_license
                break
        
        # Перезагружаем отображение
        self._apply_filters()
    
    def get_statistics(self) -> Dict:
        """Получить статистику по лицензиям"""
        total = len(self.licenses)
        active = len([l for l in self.licenses if self._get_field(l, 'status') == 'active'])
        expired = len([l for l in self.licenses if self._get_field(l, 'status') == 'expired'])
        blocked = len([l for l in self.licenses if self._get_field(l, 'status') == 'blocked'])
        created = len([l for l in self.licenses if self._get_field(l, 'status') == 'created'])
        
        return {
            'total': total,
            'active': active,
            'expired': expired,
            'blocked': blocked,
            'created': created
        }
    
    def export_to_list(self) -> List[Dict]:
        """Экспортировать данные таблицы в список словарей"""
        result = []
        for license in self.filtered_licenses:
            result.append({
                'license_key': self._get_field(license, 'license_key'),
                'client_name': self._get_field(license, 'client_name'),
                'client_contact': self._get_field(license, 'client_contact'),
                'client_telegram': self._get_field(license, 'client_telegram'),
                'account_owner': self._get_field(license, 'account_owner'),
                'account_number': self._get_field(license, 'account_number'),
                'broker_name': self._get_field(license, 'broker_name'),
                'robot_name': self._get_field(license, 'robot_name'),
                'robot_version': self._get_field(license, 'robot_version'),
                'last_balance': self._get_field(license, 'last_balance'),
                'account_type': self._get_field(license, 'account_type'),
                'created_date': self._get_field(license, 'created_date'),
                'expiry_date': self._get_field(license, 'expiry_date'),
                'days_left': self._get_field(license, 'days_left'),
                'status': self._get_field(license, 'status')
            })
        return result