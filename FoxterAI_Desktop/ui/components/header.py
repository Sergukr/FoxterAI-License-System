"""
Компонент заголовка приложения с премиум дизайном
Изумрудные и золотые акценты согласно дизайн-гайду
"""

import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from themes.dark_theme import DarkTheme


class HeaderPanel(ctk.CTkFrame):
    """Премиум панель заголовка приложения с изумрудными акцентами"""
    
    def __init__(self, parent, on_reconnect_callback: Optional[Callable] = None):
        """
        Инициализация заголовка
        
        Args:
            parent: Родительский виджет
            on_reconnect_callback: Функция для переподключения к серверу
        """
        super().__init__(
            parent, 
            fg_color=DarkTheme.BG_SECONDARY,
            height=70,
            corner_radius=DarkTheme.RADIUS_LARGE
        )
        
        self.on_reconnect = on_reconnect_callback
        self.is_connected = False
        self.animation_active = False
        
        # Не позволяем содержимому менять размер фрейма
        self.pack_propagate(False)
        
        # Создаём элементы
        self._create_widgets()
        
        # Начальное состояние
        self.set_connection_status(False)
        
        # Запуск анимации логотипа
        self._start_logo_pulse()
    
    def _create_widgets(self):
        """Создание виджетов заголовка с премиум дизайном"""
        
        # ===== ЛЕВАЯ ЧАСТЬ - ЛОГОТИП И НАЗВАНИЕ =====
        self.left_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.left_frame.pack(side='left', padx=25, pady=15)
        
        # Контейнер для логотипа с эффектом свечения
        self.logo_container = ctk.CTkFrame(
            self.left_frame,
            fg_color=DarkTheme.DEEP_EMERALD,
            corner_radius=12,
            width=50,
            height=50,
            border_width=2,
            border_color=DarkTheme.JADE_GREEN
        )
        self.logo_container.pack(side='left', padx=(0, 15))
        self.logo_container.pack_propagate(False)
        
        # Логотип (эмодзи лиса или бриллиант для премиум версии)
        self.logo = ctk.CTkLabel(
            self.logo_container,
            text="💎",  # Бриллиант для премиум версии
            font=("Segoe UI Emoji", 24)
        )
        self.logo.pack(expand=True)
        
        # Контейнер для текста
        text_container = ctk.CTkFrame(self.left_frame, fg_color='transparent')
        text_container.pack(side='left')
        
        # Название приложения
        self.title_label = ctk.CTkLabel(
            text_container,
            text="License Manager SD",
            font=("Montserrat", 20, "bold"),
            text_color=DarkTheme.PURE_WHITE
        )
        self.title_label.pack(anchor='w')
        
        # Подзаголовок с версией (золотой текст)
        self.subtitle_label = ctk.CTkLabel(
            text_container,
            text="Premium Edition v2.2",
            font=(DarkTheme.FONT_FAMILY, 12),
            text_color=DarkTheme.CHAMPAGNE_GOLD
        )
        self.subtitle_label.pack(anchor='w')
        
        # ===== ЦЕНТРАЛЬНАЯ ЧАСТЬ - ВРЕМЯ И ДАТА =====
        self.center_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.center_frame.pack(side='left', expand=True, padx=20)
        
        # Время
        self.time_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=("Inter", 16, "bold"),
            text_color=DarkTheme.JADE_GREEN
        )
        self.time_label.pack()
        
        # Дата
        self.date_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=(DarkTheme.FONT_FAMILY, 11),
            text_color=DarkTheme.WARM_GRAY
        )
        self.date_label.pack()
        
        # Запуск обновления времени
        self._update_time()
        
        # ===== ПРАВАЯ ЧАСТЬ - СТАТУС ПОДКЛЮЧЕНИЯ =====
        self.right_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.right_frame.pack(side='right', padx=25, pady=15)
        
        # Внутренний контейнер для статуса
        status_inner = ctk.CTkFrame(
            self.right_frame,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=DarkTheme.RADIUS_NORMAL
        )
        status_inner.pack(padx=10, pady=5, fill='x')
        
        # Индикатор подключения (точка)
        self.connection_dot = ctk.CTkLabel(
            status_inner,
            text="●",
            font=(DarkTheme.FONT_FAMILY, 12),
            text_color=DarkTheme.STATUS_ERROR
        )
        self.connection_dot.pack(side='left', padx=(15, 8))
        
        # Текст статуса
        self.status_text = ctk.CTkLabel(
            status_inner,
            text="Отключено",
            font=(DarkTheme.FONT_FAMILY, 12, "bold"),
            text_color=DarkTheme.WARM_GRAY
        )
        self.status_text.pack(side='left', padx=(0, 15))
        
        # Кнопка переподключения с изумрудным акцентом
        self.reconnect_btn = ctk.CTkButton(
            status_inner,
            text="🔗 Подключить",
            command=self._on_reconnect_click,
            fg_color=DarkTheme.DEEP_EMERALD,
            hover_color=DarkTheme.JADE_GREEN,
            text_color=DarkTheme.PURE_WHITE,
            corner_radius=DarkTheme.RADIUS_SMALL,
            width=120,
            height=28,
            font=(DarkTheme.FONT_FAMILY, 11, "bold")
        )
        self.reconnect_btn.pack(side='left', padx=(0, 15))
    
    def set_connection_status(self, is_connected: bool):
        """
        Установка статуса подключения с анимацией
        
        Args:
            is_connected: True если подключено, False если отключено
        """
        self.is_connected = is_connected
        
        if is_connected:
            # Подключено - зеленый индикатор и золотые акценты
            self.connection_dot.configure(text_color=DarkTheme.JADE_GREEN)
            self.status_text.configure(
                text="✅ Подключено к серверу",
                text_color=DarkTheme.JADE_GREEN
            )
            self.reconnect_btn.configure(
                text="🔄 Обновить",
                fg_color=DarkTheme.CHAMPAGNE_GOLD,
                hover_color=DarkTheme.COPPER_BRONZE,
                text_color=DarkTheme.CHARCOAL_BLACK
            )
            # Запуск анимации пульсации индикатора
            self._start_connection_pulse()
        else:
            # Отключено - красный индикатор
            self.connection_dot.configure(text_color="#D32F2F")
            self.status_text.configure(
                text="❌ Отключено",
                text_color=DarkTheme.WARM_GRAY
            )
            self.reconnect_btn.configure(
                text="🔗 Подключить",
                fg_color=DarkTheme.DEEP_EMERALD,
                hover_color=DarkTheme.JADE_GREEN,
                text_color=DarkTheme.PURE_WHITE
            )
    
    def _on_reconnect_click(self):
        """Обработка клика по кнопке переподключения"""
        if self.on_reconnect:
            # Анимация кнопки
            self._animate_button_click()
            self.on_reconnect()
    
    def _update_time(self):
        """Обновление времени и даты"""
        now = datetime.now()
        
        # Форматирование времени
        time_str = now.strftime("%H:%M:%S")
        self.time_label.configure(text=time_str)
        
        # Форматирование даты
        # Русские названия месяцев
        months_ru = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        
        # Русские названия дней недели
        weekdays_ru = {
            0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг",
            4: "Пятница", 5: "Суббота", 6: "Воскресенье"
        }
        
        weekday = weekdays_ru[now.weekday()]
        month = months_ru[now.month]
        date_str = f"{weekday}, {now.day} {month} {now.year}"
        self.date_label.configure(text=date_str)
        
        # Повторить через 1 секунду
        self.after(1000, self._update_time)
    
    # ===== АНИМАЦИИ =====
    
    def _start_logo_pulse(self):
        """Запуск пульсации логотипа (каждые 4-5 секунд)"""
        if not self.animation_active:
            self.animation_active = True
            self._pulse_logo()
    
    def _pulse_logo(self):
        """Анимация пульсации логотипа"""
        if not self.animation_active:
            return
        
        # Изменяем размер шрифта для эффекта пульсации
        original_size = 24
        
        def grow():
            self.logo.configure(font=("Segoe UI Emoji", 26))
            self.after(200, shrink)
        
        def shrink():
            self.logo.configure(font=("Segoe UI Emoji", original_size))
        
        grow()
        
        # Повторить через 4-5 секунд
        self.after(4500, self._pulse_logo)
    
    def _start_connection_pulse(self):
        """Запуск пульсации индикатора подключения"""
        if self.is_connected:
            self._pulse_connection()
    
    def _pulse_connection(self):
        """Анимация пульсации индикатора"""
        if not self.is_connected:
            return
        
        # Мигание между ярким и приглушенным зеленым
        current_color = self.connection_dot.cget("text_color")
        
        if current_color == DarkTheme.JADE_GREEN:
            self.connection_dot.configure(text_color=DarkTheme.SOFT_MINT)
        else:
            self.connection_dot.configure(text_color=DarkTheme.JADE_GREEN)
        
        # Повторить через 1 секунду
        self.after(1000, self._pulse_connection)
    
    def _animate_button_click(self):
        """Анимация нажатия кнопки"""
        # Временно меняем цвет для эффекта нажатия
        original_fg = self.reconnect_btn.cget("fg_color")
        
        self.reconnect_btn.configure(fg_color=DarkTheme.SOFT_MINT)
        self.after(150, lambda: self.reconnect_btn.configure(fg_color=original_fg))
    
    def update_server_info(self, host: str, port: int):
        """
        Обновление информации о сервере
        
        Args:
            host: Адрес сервера
            port: Порт сервера
        """
        server_text = f"Сервер: {host}:{port}"
        # Можно добавить отображение информации о сервере если нужно
    
    def set_loading_state(self, is_loading: bool):
        """
        Установка состояния загрузки
        
        Args:
            is_loading: True если идет загрузка
        """
        if is_loading:
            self.reconnect_btn.configure(text="⏳ Загрузка...", state="disabled")
        else:
            if self.is_connected:
                self.reconnect_btn.configure(text="🔄 Обновить", state="normal")
            else:
                self.reconnect_btn.configure(text="🔗 Подключить", state="normal")
    
    def destroy(self):
        """Остановка анимаций при уничтожении виджета"""
        self.animation_active = False
        super().destroy()