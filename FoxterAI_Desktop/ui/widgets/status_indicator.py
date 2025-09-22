"""
Виджет индикатора статуса подключения
Отображает состояние связи с сервером
"""

import customtkinter as ctk
from typing import Optional, Tuple
from enum import Enum
from datetime import datetime
from themes.dark_theme import DarkTheme


class ConnectionStatus(Enum):
    """Статусы подключения"""
    CONNECTED = ('🟢', 'Подключено', DarkTheme.STATUS_ACTIVE)     # Используем зеленый
    CONNECTING = ('🟡', 'Подключение...', DarkTheme.STATUS_WARNING)  # Желтый
    DISCONNECTED = ('🔴', 'Отключено', DarkTheme.STATUS_EXPIRED)  # Красный
    ERROR = ('⚠️', 'Ошибка', DarkTheme.STATUS_EXPIRED)           # Красный для ошибок


class StatusIndicator(ctk.CTkFrame):
    """Индикатор статуса подключения к серверу"""
    
    def __init__(self, parent, initial_status: ConnectionStatus = ConnectionStatus.DISCONNECTED):
        """
        Инициализация индикатора
        
        Args:
            parent: Родительский виджет
            initial_status: Начальный статус
        """
        super().__init__(parent, fg_color="transparent", height=30)
        
        self.current_status = initial_status
        self.last_update = datetime.now()
        self.server_info = {}
        
        self._setup_ui()
        self.set_status(initial_status)
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Контейнер для индикатора
        self.container = ctk.CTkFrame(
            self,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=DarkTheme.RADIUS_MEDIUM,
            height=30
        )
        self.container.pack(fill="x", padx=5, pady=2)
        
        # Иконка статуса
        self.icon_label = ctk.CTkLabel(
            self.container,
            text="",
            font=(DarkTheme.FONT_FAMILY, 14),
            width=30
        )
        self.icon_label.pack(side="left", padx=(10, 5))
        
        # Текст статуса
        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_SMALL),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left", padx=(0, 10))
        
        # Дополнительная информация
        self.info_label = ctk.CTkLabel(
            self.container,
            text="",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
            text_color=DarkTheme.TEXT_MUTED
        )
        self.info_label.pack(side="right", padx=(0, 10))
        
        # Анимация загрузки (изначально скрыта)
        self.loading_bar = ctk.CTkProgressBar(
            self.container,
            mode="indeterminate",
            height=2,
            progress_color=DarkTheme.GREEN_PRIMARY
        )
    
    def set_status(self, status: ConnectionStatus, info: str = ""):
        """
        Установить статус подключения
        
        Args:
            status: Новый статус
            info: Дополнительная информация
        """
        self.current_status = status
        self.last_update = datetime.now()
        
        # Получаем данные статуса
        icon, text, color = status.value
        
        # Обновляем UI
        self.icon_label.configure(text=icon)
        self.status_label.configure(text=text, text_color=color)
        
        # Обновляем цвет контейнера в зависимости от статуса
        if status == ConnectionStatus.CONNECTED:
            self.container.configure(
                fg_color=DarkTheme.BG_TERTIARY,
                border_width=1,
                border_color=color
            )
        elif status == ConnectionStatus.ERROR or status == ConnectionStatus.DISCONNECTED:
            self.container.configure(
                fg_color="#450a0a",  # Темно-красный фон
                border_width=1,
                border_color=color
            )
        else:
            self.container.configure(
                fg_color=DarkTheme.BG_TERTIARY,
                border_width=1,
                border_color=DarkTheme.BORDER_PRIMARY
            )
        
        # Показываем/скрываем анимацию
        if status == ConnectionStatus.CONNECTING:
            self.show_loading()
        else:
            self.hide_loading()
        
        # Обновляем информацию
        if info:
            self.info_label.configure(text=info)
        else:
            self._update_info()
    
    def _update_info(self):
        """Обновить информационную строку"""
        if self.current_status == ConnectionStatus.CONNECTED:
            # Показываем время последнего обновления
            time_str = self.last_update.strftime("%H:%M:%S")
            self.info_label.configure(text=f"Обновлено: {time_str}")
        elif self.current_status == ConnectionStatus.ERROR:
            # Показываем время ошибки
            self.info_label.configure(text="Проверьте подключение")
        else:
            self.info_label.configure(text="")
    
    def show_loading(self):
        """Показать анимацию загрузки"""
        self.loading_bar.pack(side="bottom", fill="x", padx=0, pady=0)
        self.loading_bar.start()
    
    def hide_loading(self):
        """Скрыть анимацию загрузки"""
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
    
    def set_server_info(self, host: str, port: int):
        """
        Установить информацию о сервере
        
        Args:
            host: Адрес сервера
            port: Порт сервера
        """
        self.server_info = {
            'host': host,
            'port': port
        }
        
        if self.current_status == ConnectionStatus.CONNECTED:
            self.info_label.configure(text=f"{host}:{port}")
    
    def pulse_animation(self):
        """Анимация пульсации для привлечения внимания"""
        original_color = self.container.cget("fg_color")
        
        # Мигаем 3 раза
        for i in range(3):
            self.after(i * 400, lambda: self.container.configure(
                fg_color=DarkTheme.BG_HOVER))
            self.after(i * 400 + 200, lambda c=original_color: 
                      self.container.configure(fg_color=c))
    
    def get_status(self) -> ConnectionStatus:
        """
        Получить текущий статус
        
        Returns:
            ConnectionStatus: Текущий статус
        """
        return self.current_status
    
    def is_connected(self) -> bool:
        """
        Проверить, подключен ли к серверу
        
        Returns:
            bool: True если подключен
        """
        return self.current_status == ConnectionStatus.CONNECTED
    
    def get_uptime(self) -> str:
        """
        Получить время работы
        
        Returns:
            str: Время работы в формате HH:MM:SS
        """
        if not self.is_connected():
            return "00:00:00"
        
        delta = datetime.now() - self.last_update
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class QuickStatusBar(ctk.CTkFrame):
    """Быстрая панель статуса для нижней части окна"""
    
    def __init__(self, parent):
        """
        Инициализация панели статуса
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent, fg_color=DarkTheme.BG_SECONDARY, height=25)
        
        self.indicators = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Левая часть - статус подключения
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", padx=10)
        
        self.connection_dot = ctk.CTkLabel(
            self.left_frame,
            text="●",
            font=(DarkTheme.FONT_FAMILY, 10),
            text_color=DarkTheme.STATUS_EXPIRED
        )
        self.connection_dot.pack(side="left", padx=(0, 5))
        
        self.connection_text = ctk.CTkLabel(
            self.left_frame,
            text="Отключено",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
            text_color=DarkTheme.TEXT_MUTED
        )
        self.connection_text.pack(side="left")
        
        # Разделитель
        self.separator1 = ctk.CTkLabel(
            self,
            text="|",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
            text_color=DarkTheme.TEXT_MUTED
        )
        self.separator1.pack(side="left", padx=10)
        
        # Центральная часть - статистика
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(side="left", expand=True)
        
        self.stats_text = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
            text_color=DarkTheme.TEXT_MUTED
        )
        self.stats_text.pack()
        
        # Правая часть - время
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", padx=10)
        
        self.time_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
            text_color=DarkTheme.TEXT_MUTED
        )
        self.time_label.pack()
        
        # Обновляем время каждую секунду
        self._update_time()
    
    def _update_time(self):
        """Обновить отображение времени"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)
    
    def set_connection_status(self, connected: bool, text: str = ""):
        """
        Установить статус подключения
        
        Args:
            connected: True если подключен
            text: Текст статуса
        """
        if connected:
            self.connection_dot.configure(text_color=DarkTheme.STATUS_ACTIVE)
            self.connection_text.configure(
                text=text or "Подключено",
                text_color=DarkTheme.TEXT_SECONDARY
            )
        else:
            self.connection_dot.configure(text_color=DarkTheme.STATUS_EXPIRED)
            self.connection_text.configure(
                text=text or "Отключено",
                text_color=DarkTheme.TEXT_MUTED
            )
    
    def set_stats(self, active: int = 0, total: int = 0):
        """
        Установить статистику
        
        Args:
            active: Количество активных
            total: Общее количество
        """
        self.stats_text.configure(
            text=f"Активные: {active} / Всего: {total}"
        )
    
    def add_indicator(self, key: str, text: str, color: str = None):
        """
        Добавить индикатор
        
        Args:
            key: Ключ индикатора
            text: Текст
            color: Цвет текста
        """
        if key not in self.indicators:
            # Создаем разделитель
            separator = ctk.CTkLabel(
                self,
                text="|",
                font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
                text_color=DarkTheme.TEXT_MUTED
            )
            separator.pack(side="left", padx=5)
            
            # Создаем индикатор
            indicator = ctk.CTkLabel(
                self,
                text=text,
                font=(DarkTheme.FONT_FAMILY, DarkTheme.FONT_SIZE_TINY),
                text_color=color or DarkTheme.TEXT_MUTED
            )
            indicator.pack(side="left", padx=5)
            
            self.indicators[key] = {
                'separator': separator,
                'label': indicator
            }
        else:
            # Обновляем существующий
            self.indicators[key]['label'].configure(
                text=text,
                text_color=color or DarkTheme.TEXT_MUTED
            )
    
    def remove_indicator(self, key: str):
        """
        Удалить индикатор
        
        Args:
            key: Ключ индикатора
        """
        if key in self.indicators:
            self.indicators[key]['separator'].destroy()
            self.indicators[key]['label'].destroy()
            del self.indicators[key]