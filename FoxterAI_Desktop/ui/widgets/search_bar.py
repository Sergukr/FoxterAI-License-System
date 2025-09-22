"""
Виджет поисковой строки
Универсальная строка поиска с иконкой и очисткой
"""

import customtkinter as ctk
from typing import Optional, Callable
import sys
import os

# Добавляем путь к корневой папке
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from themes.dark_theme import DarkTheme


class SearchBar(ctk.CTkFrame):
    """Поисковая строка с расширенным функционалом"""
    
    def __init__(self, parent,
                 placeholder: str = "Поиск...",
                 width: int = 300,
                 height: int = 32,
                 on_search: Optional[Callable] = None,
                 on_clear: Optional[Callable] = None,
                 search_delay: int = 300):
        """
        Инициализация поисковой строки
        
        Args:
            parent: Родительский виджет
            placeholder: Текст-подсказка
            width: Ширина виджета
            height: Высота виджета
            on_search: Callback при поиске (text: str)
            on_clear: Callback при очистке
            search_delay: Задержка перед поиском (мс)
        """
        super().__init__(parent, 
                        fg_color='transparent',
                        width=width,
                        height=height)
        
        # Callbacks
        self.on_search = on_search
        self.on_clear = on_clear
        
        # Параметры
        self.search_delay = search_delay
        self.search_timer = None
        
        # Создаём элементы
        self._create_widgets(placeholder, width, height)
    
    def _create_widgets(self, placeholder: str, width: int, height: int):
        """Создание виджетов"""
        # Контейнер
        container = ctk.CTkFrame(self, 
                                fg_color=DarkTheme.BG_INPUT,
                                corner_radius=6,
                                height=height)
        container.pack(fill='x', expand=True)
        container.pack_propagate(False)
        
        # Иконка поиска
        self.search_icon = ctk.CTkLabel(
            container,
            text="🔍",
            font=("Arial", 14),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        self.search_icon.pack(side='left', padx=(8, 4))
        
        # Поле ввода
        self.entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder,
            border_width=0,
            fg_color='transparent',
            text_color=DarkTheme.TEXT_PRIMARY,
            placeholder_text_color=DarkTheme.TEXT_DISABLED,
            font=("Arial", 12)
        )
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 4))
        
        # Кнопка очистки (изначально скрыта)
        self.clear_btn = ctk.CTkButton(
            container,
            text="✕",
            width=20,
            height=20,
            fg_color='transparent',
            text_color=DarkTheme.TEXT_SECONDARY,
            hover_color=DarkTheme.BG_HOVER,
            font=("Arial", 12),
            command=self.clear
        )
        
        # Привязываем события
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<Return>', self._on_enter)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Стиль контейнера
        self.container = container
    
    def _on_key_release(self, event):
        """Обработчик ввода текста"""
        text = self.entry.get()
        
        # Показываем/скрываем кнопку очистки
        if text:
            if not self.clear_btn.winfo_ismapped():
                self.clear_btn.pack(side='right', padx=(0, 8))
        else:
            if self.clear_btn.winfo_ismapped():
                self.clear_btn.pack_forget()
        
        # Отменяем предыдущий таймер
        if self.search_timer:
            self.after_cancel(self.search_timer)
        
        # Запускаем новый таймер
        if self.on_search:
            self.search_timer = self.after(
                self.search_delay,
                lambda: self._perform_search(text)
            )
    
    def _on_enter(self, event):
        """Обработчик нажатия Enter"""
        text = self.entry.get()
        
        # Отменяем таймер
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None
        
        # Выполняем поиск сразу
        if self.on_search:
            self._perform_search(text)
    
    def _on_focus_in(self, event):
        """Обработчик получения фокуса"""
        self.container.configure(border_width=1, 
                                border_color=DarkTheme.BORDER_FOCUS)
        self.search_icon.configure(text_color=DarkTheme.ACCENT_GREEN)
    
    def _on_focus_out(self, event):
        """Обработчик потери фокуса"""
        self.container.configure(border_width=0)
        self.search_icon.configure(text_color=DarkTheme.TEXT_SECONDARY)
    
    def _perform_search(self, text: str):
        """Выполнить поиск"""
        if self.on_search:
            self.on_search(text)
    
    def clear(self):
        """Очистить поле поиска"""
        self.entry.delete(0, 'end')
        
        # Скрываем кнопку очистки
        if self.clear_btn.winfo_ismapped():
            self.clear_btn.pack_forget()
        
        # Вызываем callback
        if self.on_clear:
            self.on_clear()
        
        # Вызываем поиск с пустой строкой
        if self.on_search:
            self.on_search("")
    
    def set_text(self, text: str):
        """
        Установить текст
        
        Args:
            text: Текст для установки
        """
        self.entry.delete(0, 'end')
        self.entry.insert(0, text)
        
        # Обновляем кнопку очистки
        if text and not self.clear_btn.winfo_ismapped():
            self.clear_btn.pack(side='right', padx=(0, 8))
        elif not text and self.clear_btn.winfo_ismapped():
            self.clear_btn.pack_forget()
    
    def get_text(self) -> str:
        """
        Получить текст
        
        Returns:
            str: Текущий текст
        """
        return self.entry.get()
    
    def focus(self):
        """Установить фокус на поле ввода"""
        self.entry.focus_set()
    
    def set_placeholder(self, placeholder: str):
        """
        Изменить текст-подсказку
        
        Args:
            placeholder: Новый текст-подсказка
        """
        self.entry.configure(placeholder_text=placeholder)
    
    def enable(self):
        """Включить поиск"""
        self.entry.configure(state='normal')
        self.search_icon.configure(text_color=DarkTheme.TEXT_SECONDARY)
    
    def disable(self):
        """Отключить поиск"""
        self.entry.configure(state='disabled')
        self.search_icon.configure(text_color=DarkTheme.TEXT_DISABLED)