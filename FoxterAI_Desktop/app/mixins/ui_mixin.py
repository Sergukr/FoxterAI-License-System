"""
Миксин для UI операций с премиальным дизайном
Изумрудные и золотые акценты согласно дизайн-гайду FoxterAI
ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Desktop/app/mixins/ui_mixin.py
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from typing import List, Dict, Any

# Импорт компонентов UI
from ui.components.header import HeaderPanel
from ui.components.stats_panel import StatsPanel
from ui.components.license_table import LicenseTable

# Импорт темы
from themes.dark_theme import DarkTheme


class UIMixin:
    """Методы для управления премиальным интерфейсом"""
    
    def _setup_window(self):
        """Настройка окна приложения с премиальным дизайном"""
        # Заголовок и размер
        self.title("🦊 License Manager SD v2.2 - Premium Edition")
        
        # Размеры окна из конфига или по умолчанию
        width = self.config.get('APP', 'window_width', 1400)
        height = self.config.get('APP', 'window_height', 800)
        
        self.center_window(width, height)
        self.minsize(1200, 700)
        
        # Премиальная тема
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Обработчик закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Стиль окна с угольно-черным фоном
        self.configure(fg_color=DarkTheme.CHARCOAL_BLACK)
    
    def _build_ui(self):
        """Построение премиального интерфейса с градиентами и эффектами"""
        # Главный контейнер
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=DarkTheme.CHARCOAL_BLACK,
            corner_radius=0
        )
        self.main_container.pack(fill='both', expand=True)
        
        # Компоненты интерфейса
        self._build_header()
        self._build_stats_panel()
        self._build_control_panel()
        self._build_license_table()
        self._build_status_bar()
    
    def _build_header(self):
        """Создание заголовка с изумрудно-золотыми акцентами"""
        self.header = HeaderPanel(
            self.main_container,
            on_reconnect_callback=self.connect_to_server
        )
        self.header.pack(fill='x', padx=10, pady=(10, 5))
        
        # Доступ к тексту статуса
        self.status_text = self.header.status_text
    
    def _build_stats_panel(self):
        """Создание панели статистики с 3D карточками"""
        self.stats_panel = StatsPanel(self.main_container)
        self.stats_panel.pack(fill='x', padx=10, pady=5)
    
    def _build_control_panel(self):
        """Создание панели управления с премиальными кнопками"""
        # Контейнер панели управления
        control_container = ctk.CTkFrame(
            self.main_container,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            corner_radius=DarkTheme.RADIUS_LARGE,
            height=60
        )
        control_container.pack(fill='x', padx=10, pady=5)
        control_container.pack_propagate(False)
        
        # Левая часть - кнопки действий
        left_frame = ctk.CTkFrame(control_container, fg_color='transparent')
        left_frame.pack(side='left', fill='y', padx=15, pady=10)
        
        # Кнопка создания лицензии (изумрудная)
        self.create_btn = ctk.CTkButton(
            left_frame,
            text="➕ Создать лицензию",
            command=self.create_license_dialog,
            fg_color=DarkTheme.DEEP_EMERALD,
            hover_color=DarkTheme.JADE_GREEN,
            text_color=DarkTheme.PURE_WHITE,
            width=160,
            height=35,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            font=("Inter", 12, "bold")
        )
        self.create_btn.pack(side='left', padx=(0, 10))
        
        # Кнопка обновления (золотая)
        self.refresh_btn = ctk.CTkButton(
            left_frame,
            text="🔄 Обновить",
            command=self.load_licenses,
            fg_color=DarkTheme.CHAMPAGNE_GOLD,
            hover_color=DarkTheme.COPPER_BRONZE,
            text_color=DarkTheme.CHARCOAL_BLACK,
            width=110,
            height=35,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            font=("Inter", 11, "bold")
        )
        self.refresh_btn.pack(side='left', padx=(0, 10))
        
        # Кнопка экспорта
        self.export_btn = ctk.CTkButton(
            left_frame,
            text="📤 Экспорт",
            command=self.export_licenses,
            fg_color=DarkTheme.BG_TERTIARY,
            hover_color=DarkTheme.BG_HOVER,
            text_color=DarkTheme.WARM_GRAY,
            width=100,
            height=35,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            font=("Inter", 11)
        )
        self.export_btn.pack(side='left')
        
        # Правая часть - фильтры и поиск
        right_frame = ctk.CTkFrame(control_container, fg_color='transparent')
        right_frame.pack(side='right', fill='y', padx=15, pady=10)
        
        # Фильтр по статусу
        self.status_filter = ctk.CTkOptionMenu(
            right_frame,
            values=['Все', 'Активные', 'Истекшие', 'Заблокированные', 'Не активированные'],
            command=self._on_filter_change,
            fg_color=DarkTheme.BG_TERTIARY,
            button_color=DarkTheme.DEEP_EMERALD,
            button_hover_color=DarkTheme.JADE_GREEN,
            dropdown_fg_color=DarkTheme.BG_TERTIARY,
            dropdown_hover_color=DarkTheme.BG_HOVER,
            text_color=DarkTheme.PURE_WHITE,
            dropdown_text_color=DarkTheme.WARM_GRAY,
            width=180,
            height=35,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            font=("Inter", 11)
        )
        self.status_filter.set('Все')
        self.status_filter.pack(side='right', padx=5)
        
        # Поиск с мятным акцентом
        self.search_entry = ctk.CTkEntry(
            right_frame,
            placeholder_text="🔍 Поиск лицензии...",
            width=250,
            height=35,
            fg_color=DarkTheme.BG_TERTIARY,
            border_color=DarkTheme.SOFT_MINT,
            border_width=1,
            text_color=DarkTheme.PURE_WHITE,
            placeholder_text_color=DarkTheme.WARM_GRAY,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            font=("Inter", 11)
        )
        self.search_entry.pack(side='right', padx=5)
        self.search_entry.bind('<KeyRelease>', self._on_search)
    
    def _build_license_table(self):
        """Создание таблицы лицензий с премиальным дизайном"""
        # Контейнер для таблицы
        table_container = ctk.CTkFrame(
            self.main_container,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            corner_radius=DarkTheme.RADIUS_LARGE
        )
        table_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Заголовок секции
        table_header = ctk.CTkFrame(table_container, fg_color='transparent')
        table_header.pack(fill='x', padx=15, pady=(15, 5))
        
        table_title = ctk.CTkLabel(
            table_header,
            text="📋 Список лицензий",
            font=("Montserrat", 16, "bold"),
            text_color=DarkTheme.PURE_WHITE
        )
        table_title.pack(side='left')
        
        # Индикатор количества
        self.license_count = ctk.CTkLabel(
            table_header,
            text="Всего: 0",
            font=("Inter", 12),
            text_color=DarkTheme.CHAMPAGNE_GOLD
        )
        self.license_count.pack(side='right')
        
        # Таблица с премиальным дизайном
        self.license_table = LicenseTable(table_container)
        self.license_table.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # Устанавливаем callbacks для таблицы
        self.license_table.set_callbacks(
            select=self._on_license_select,
            double_click=self.show_license_details,
            context_menu=self._show_context_menu
        )
    
    def _build_status_bar(self):
        """Создание статусной строки с градиентом"""
        status_container = ctk.CTkFrame(
            self.main_container,
            fg_color=DarkTheme.BG_TERTIARY,
            height=30
        )
        status_container.pack(fill='x', side='bottom')
        
        # Текст статуса
        self.status_bar = ctk.CTkLabel(
            status_container,
            text="⚡ Готов к работе",
            font=("Inter", 10),
            text_color=DarkTheme.WARM_GRAY,
            anchor='w'
        )
        self.status_bar.pack(side='left', padx=15, pady=5)
        
        # Версия
        version_label = ctk.CTkLabel(
            status_container,
            text="v2.2 Premium",
            font=("Inter", 9),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        version_label.pack(side='right', padx=15, pady=5)
    
    # ==================== ОБРАБОТЧИКИ СОБЫТИЙ ====================
    
    def _on_filter_change(self, choice):
        """Обработка изменения фильтра"""
        if self.license_table:
            self.license_table.set_filter(choice)
            self._update_license_count()
    
    def _on_search(self, event):
        """Обработка поиска"""
        query = self.search_entry.get()
        if self.license_table:
            self.license_table.set_search(query)
            self._update_license_count()
    
    def _on_license_select(self, license):
        """Обработка выбора лицензии"""
        # Можно добавить дополнительную логику при выборе
        pass
    
    def _show_context_menu(self, license, event):
        """Показ контекстного меню для лицензии"""
        # Создаем премиальное контекстное меню
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.configure(fg_color=DarkTheme.GRAPHITE_GRAY)
        
        # Позиционирование
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        menu.geometry(f"160x200+{x}+{y}")
        
        # Пункты меню
        menu_items = [
            ("🔍 Детали", lambda: self.show_license_details(license)),
            ("✏️ Редактировать", lambda: self.edit_license_dialog(license)),
            ("⏰ Продлить", lambda: self.extend_license_dialog(license)),
            ("🔒 Заблокировать", lambda: self.block_license(license)),
            ("🗑️ Удалить", lambda: self.delete_license(license))
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                menu,
                text=text,
                command=lambda cmd=command: [cmd(), menu.destroy()],
                fg_color="transparent",
                hover_color=DarkTheme.JADE_GREEN,
                text_color=DarkTheme.PURE_WHITE,
                anchor="w",
                width=150,
                height=30,
                font=("Inter", 11)
            )
            btn.pack(fill='x', padx=5, pady=2)
        
        # Закрытие по клику вне меню
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_force()
    
    # ==================== МЕТОДЫ ОБНОВЛЕНИЯ UI ====================
    
    def update_statistics(self, stats: Dict[str, Any] = None):
        """Обновление статистики с анимацией"""
        if stats is None:
            # Если статистика не передана, вычисляем из лицензий
            stats = self._calculate_statistics()
        
        if self.stats_panel:
            self.stats_panel.update_stats(stats)
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Вычислить статистику из списка лицензий"""
        stats = {
            'total': len(self.licenses),
            'active': 0,
            'expired': 0,
            'blocked': 0,
            'inactive': 0,
            'balance': 0.0
        }
        
        for license in self.licenses:
            if hasattr(license, '__dict__'):
                status = getattr(license, 'status', 'created')
                balance = getattr(license, 'last_balance', 0)
                account_type = getattr(license, 'account_type', 'Real')
            else:
                status = license.get('status', 'created')
                balance = license.get('last_balance', 0)
                account_type = license.get('account_type', 'Real')
            
            if status == 'active':
                stats['active'] += 1
            elif status == 'expired':
                stats['expired'] += 1
            elif status == 'blocked':
                stats['blocked'] += 1
            else:
                stats['inactive'] += 1
            
            # Считаем баланс только для реальных счетов
            if account_type == 'Real':
                try:
                    stats['balance'] += float(balance)
                except:
                    pass
        
        return stats
    
    def _update_license_count(self):
        """Обновить счетчик лицензий"""
        if hasattr(self, 'license_count') and self.license_table:
            filtered = len(self.license_table.filtered_licenses)
            total = len(self.license_table.licenses)
            
            if filtered < total:
                text = f"Показано: {filtered} из {total}"
            else:
                text = f"Всего: {total}"
            
            self.license_count.configure(text=text)
    
    def _enable_controls(self, enabled: bool):
        """Включить/выключить элементы управления"""
        state = 'normal' if enabled else 'disabled'
        
        controls = ['refresh_btn', 'create_btn', 'export_btn']
        for control_name in controls:
            if hasattr(self, control_name):
                control = getattr(self, control_name)
                if hasattr(control, 'configure'):
                    try:
                        control.configure(state=state)
                    except:
                        pass
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def center_window(self, width: int, height: int):
        """Центрирование окна на экране"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def set_status(self, text: str, status_type: str = "info"):
        """
        Установить текст в статусной строке
        
        Args:
            text: Текст статуса
            status_type: Тип статуса (info, success, error, loading)
        """
        if hasattr(self, 'status_bar'):
            # Выбор цвета по типу
            color_map = {
                'info': DarkTheme.WARM_GRAY,
                'success': DarkTheme.JADE_GREEN,
                'error': '#FF6B6B',
                'warning': DarkTheme.COPPER_BRONZE,
                'loading': DarkTheme.SOFT_MINT
            }
            
            color = color_map.get(status_type, DarkTheme.WARM_GRAY)
            self.status_bar.configure(text=text, text_color=color)
        
        # Также выводим в консоль для отладки
        print(f"[STATUS] {text}")
    
    def show_loading(self, show: bool):
        """
        Показать/скрыть индикатор загрузки
        
        Args:
            show: True для показа, False для скрытия
        """
        self.is_loading = show
        
        # Обновляем индикатор в заголовке если есть
        if hasattr(self, 'header') and self.header:
            if hasattr(self.header, 'set_loading_state'):
                self.header.set_loading_state(show)
        
        # Обновляем курсор
        if show:
            self.configure(cursor="wait")
        else:
            self.configure(cursor="")
        
        # Блокируем/разблокируем элементы управления
        self._enable_controls(not show)
    
    def show_notification(self, title: str, message: str, notif_type: str = "info"):
        """
        Показать уведомление
        
        Args:
            title: Заголовок уведомления
            message: Текст сообщения
            notif_type: Тип уведомления (info, success, error, warning)
        """
        # Простая реализация через messagebox
        # Можно заменить на кастомное премиальное окно уведомления
        if notif_type == "error":
            messagebox.showerror(title, message)
        elif notif_type == "warning":
            messagebox.showwarning(title, message)
        elif notif_type == "success":
            messagebox.showinfo(f"✅ {title}", message)
        else:
            messagebox.showinfo(title, message)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        # Сохраняем размер окна
        if hasattr(self, 'config'):
            width = self.winfo_width()
            height = self.winfo_height()
            self.config.set_window_size(width, height)
            self.config.save()
        
        # Отключаемся от сервера
        if hasattr(self, 'license_service') and self.license_service:
            if hasattr(self.license_service, 'disconnect'):
                self.license_service.disconnect()
        
        # Закрываем окно
        self.destroy()
        
        # Выходим из приложения
        import sys
        sys.exit(0)