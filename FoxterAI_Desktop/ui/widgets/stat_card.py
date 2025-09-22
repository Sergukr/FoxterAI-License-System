"""
Виджет карточки статистики
Отображение одного показателя статистики
"""

import customtkinter as ctk
from typing import Any, Dict, Optional
from themes.dark_theme import DarkTheme


class StatCard(ctk.CTkFrame):
    """Карточка для отображения одного показателя статистики"""
    
    def __init__(self, parent, title: str, value: Any = 0,
                 icon: str = "", color_scheme: Dict = None,
                 is_currency: bool = False):
        """
        Инициализация карточки
        
        Args:
            parent: Родительский виджет
            title: Заголовок карточки
            value: Значение для отображения
            icon: Иконка (эмодзи)
            color_scheme: Цветовая схема
            is_currency: Отображать как валюту
        """
        # Цветовая схема по умолчанию
        self.color_scheme = color_scheme or {
            'bg': DarkTheme.BG_TERTIARY,
            'text': DarkTheme.TEXT_SECONDARY,
            'value': DarkTheme.TEXT_PRIMARY,
            'border': DarkTheme.BORDER_PRIMARY
        }
        
        super().__init__(
            parent,
            fg_color=self.color_scheme['bg'],
            corner_radius=DarkTheme.RADIUS_MEDIUM,
            border_width=1,
            border_color=self.color_scheme['border'],
            height=90
        )
        
        self.title = title
        self.value = value
        self.icon = icon
        self.is_currency = is_currency
        self.is_highlighted = False
        self.has_alert = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса карточки"""
        # Главный контейнер
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Верхняя часть с иконкой и заголовком
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 5))
        
        # Иконка
        if self.icon:
            self.icon_label = ctk.CTkLabel(
                self.header_frame,
                text=self.icon,
                font=(DarkTheme.FONT_FAMILY, 20),
                text_color=self.color_scheme['value']
            )
            self.icon_label.pack(side="left", padx=(0, 8))
        
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.title,
            font=(DarkTheme.FONT_FAMILY, 11, "bold"),
            text_color=self.color_scheme['text']
        )
        self.title_label.pack(side="left")
        
        # Индикатор предупреждения (изначально скрыт)
        self.alert_indicator = ctk.CTkLabel(
            self.header_frame,
            text="⚠",
            font=(DarkTheme.FONT_FAMILY, 16),
            text_color="#f59e0b"
        )
        
        # Значение
        self.value_label = ctk.CTkLabel(
            self.container,
            text=self._format_value(self.value),
            font=(DarkTheme.FONT_FAMILY, 28, "bold"),
            text_color=self.color_scheme['value']
        )
        self.value_label.pack(fill="x")
        
        # Индикатор загрузки (изначально скрыт)
        self.loading_indicator = ctk.CTkProgressBar(
            self.container,
            mode="indeterminate",
            height=2,
            progress_color=self.color_scheme['value']
        )
    
    def _format_value(self, value: Any) -> str:
        """
        Форматировать значение для отображения
        
        Args:
            value: Значение для форматирования
            
        Returns:
            str: Отформатированное значение
        """
        if self.is_currency:
            if isinstance(value, str):
                return value  # Уже отформатировано
            elif isinstance(value, (int, float)):
                if value >= 1000000:
                    return f"${value/1000000:.1f}M"
                elif value >= 1000:
                    return f"${value/1000:.1f}K"
                else:
                    return f"${value:.0f}"
        return str(value)
    
    def update_value(self, value: Any):
        """
        Обновить отображаемое значение
        
        Args:
            value: Новое значение
        """
        self.value = value
        formatted = self._format_value(value)
        self.value_label.configure(text=formatted)
        
        # Анимация обновления
        self._pulse_animation()
    
    def _pulse_animation(self):
        """Анимация пульсации при обновлении значения"""
        # Временно увеличиваем шрифт
        self.value_label.configure(
            font=(DarkTheme.FONT_FAMILY, 30, "bold")
        )
        # Возвращаем обратно через 100мс
        self.after(100, lambda: self.value_label.configure(
            font=(DarkTheme.FONT_FAMILY, 28, "bold")
        ))
    
    def set_alert_state(self, has_alert: bool, color: str = "#f59e0b"):
        """
        Установить состояние предупреждения
        
        Args:
            has_alert: Есть ли предупреждение
            color: Цвет предупреждения
        """
        self.has_alert = has_alert
        
        if has_alert:
            # Показываем индикатор
            self.alert_indicator.configure(text_color=color)
            self.alert_indicator.pack(side="right", padx=(5, 0))
            # Меняем границу
            self.configure(border_color=color, border_width=2)
        else:
            # Скрываем индикатор
            self.alert_indicator.pack_forget()
            # Возвращаем обычную границу
            self.configure(
                border_color=self.color_scheme['border'],
                border_width=1
            )
    
    def highlight(self):
        """Подсветить карточку"""
        if not self.is_highlighted:
            self.is_highlighted = True
            self.configure(fg_color=DarkTheme.BG_HOVER)
    
    def reset_highlight(self):
        """Сбросить подсветку карточки"""
        if self.is_highlighted:
            self.is_highlighted = False
            self.configure(fg_color=self.color_scheme['bg'])
    
    def set_loading_state(self, is_loading: bool):
        """
        Установить состояние загрузки
        
        Args:
            is_loading: True если идет загрузка
        """
        if is_loading:
            # Скрываем значение, показываем индикатор
            self.value_label.pack_forget()
            self.loading_indicator.pack(fill="x", pady=(10, 0))
            self.loading_indicator.start()
        else:
            # Скрываем индикатор, показываем значение
            self.loading_indicator.stop()
            self.loading_indicator.pack_forget()
            self.value_label.pack(fill="x")
    
    def set_color_scheme(self, color_scheme: Dict):
        """
        Изменить цветовую схему карточки
        
        Args:
            color_scheme: Новая цветовая схема
        """
        self.color_scheme = color_scheme
        
        # Обновляем цвета
        self.configure(
            fg_color=color_scheme.get('bg', DarkTheme.BG_TERTIARY),
            border_color=color_scheme.get('border', DarkTheme.BORDER_PRIMARY)
        )
        
        self.title_label.configure(
            text_color=color_scheme.get('text', DarkTheme.TEXT_SECONDARY)
        )
        
        self.value_label.configure(
            text_color=color_scheme.get('value', DarkTheme.TEXT_PRIMARY)
        )
        
        if self.icon_label:
            self.icon_label.configure(
                text_color=color_scheme.get('value', DarkTheme.TEXT_PRIMARY)
            )
    
    def get_value(self) -> Any:
        """
        Получить текущее значение
        
        Returns:
            Any: Текущее значение
        """
        return self.value
    
    def set_tooltip(self, text: str):
        """
        Установить всплывающую подсказку
        
        Args:
            text: Текст подсказки
        """
        # CustomTkinter не имеет встроенных тултипов,
        # но можно добавить обработчики событий
        self.bind("<Enter>", lambda e: self._show_tooltip(text))
        self.bind("<Leave>", lambda e: self._hide_tooltip())
    
    def _show_tooltip(self, text: str):
        """Показать всплывающую подсказку (заглушка)"""
        # Можно реализовать кастомный тултип если нужно
        pass
    
    def _hide_tooltip(self):
        """Скрыть всплывающую подсказку (заглушка)"""
        pass