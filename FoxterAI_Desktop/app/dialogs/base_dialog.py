"""
Базовые классы диалоговых окон с премиум дизайном
"""

import customtkinter as ctk
from typing import Optional, Tuple
import sys
import os

# Добавляем путь к корню проекта для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from themes.dark_theme import DarkTheme


class CustomDialog(ctk.CTkToplevel):
    """Премиум диалоговое окно с анимациями и темной темой"""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            title: Заголовок диалога
            width: Ширина окна
            height: Высота окна
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=DarkTheme.BG_PRIMARY)
        
        # Центрирование окна
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Настройки окна
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()
        
        # Эффект появления (анимация)
        self.attributes('-alpha', 0.0)
        self._animate_in()
        
        # Обработка закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Результат диалога
        self.result = None
    
    def _animate_in(self):
        """Анимация появления окна"""
        alpha = float(self.attributes('-alpha'))
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(10, self._animate_in)
    
    def _animate_out(self, callback=None):
        """Анимация исчезновения окна"""
        alpha = float(self.attributes('-alpha'))
        if alpha > 0:
            self.attributes('-alpha', alpha - 0.1)
            self.after(10, lambda: self._animate_out(callback))
        else:
            if callback:
                callback()
            self.destroy()
    
    def on_closing(self):
        """Обработка закрытия окна"""
        self._animate_out()


class ConfirmDialog(CustomDialog):
    """Диалог подтверждения с премиум дизайном"""
    
    def __init__(self, parent, title: str, message: str, 
                 dialog_type: str = "info", width: int = 400, height: int = 200):
        """
        Создать диалог подтверждения
        
        Args:
            parent: Родительское окно
            title: Заголовок
            message: Сообщение
            dialog_type: Тип диалога (info, warning, error, success)
            width: Ширина
            height: Высота
        """
        super().__init__(parent, title, width, height)
        
        # Иконки и цвета для типов
        self.icons = {
            'info': ('ℹ️', DarkTheme.NEON_BLUE),
            'warning': ('⚠️', DarkTheme.NEON_YELLOW),
            'error': ('❌', DarkTheme.STATUS_EXPIRED),
            'success': ('✅', DarkTheme.NEON_GREEN)
        }
        
        icon, color = self.icons.get(dialog_type, self.icons['info'])
        
        # Контент
        content = ctk.CTkFrame(self, fg_color=DarkTheme.BG_SECONDARY, corner_radius=10)
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Иконка и заголовок
        header = ctk.CTkFrame(content, fg_color='transparent')
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=(DarkTheme.FONT_FAMILY, 24),
            text_color=color
        ).pack(side='left', padx=(0, 10))
        
        ctk.CTkLabel(
            header,
            text=title,
            font=(DarkTheme.FONT_FAMILY, 14, "bold"),
            text_color=DarkTheme.TEXT_PRIMARY
        ).pack(side='left')
        
        # Сообщение
        ctk.CTkLabel(
            content,
            text=message,
            font=(DarkTheme.FONT_FAMILY, 12),
            text_color=DarkTheme.TEXT_SECONDARY,
            justify='left',
            wraplength=width-80
        ).pack(padx=20, pady=(10, 20))
        
        # Кнопки
        btn_frame = ctk.CTkFrame(content, fg_color='transparent')
        btn_frame.pack(side='bottom', pady=(20, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Да",
            command=self._on_yes,
            fg_color=DarkTheme.BUTTON_PRIMARY,
            hover_color=DarkTheme.BUTTON_PRIMARY_HOVER,
            width=100
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Нет",
            command=self._on_no,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            width=100
        ).pack(side='left', padx=5)
    
    def _on_yes(self):
        self.result = True
        self.destroy()
    
    def _on_no(self):
        self.result = False
        self.destroy()


class InputDialog(CustomDialog):
    """Диалог ввода значения с премиум дизайном"""
    
    def __init__(self, parent, title: str, prompt: str, 
                 initial_value: str = "", width: int = 400, height: int = 200):
        """
        Создать диалог ввода
        
        Args:
            parent: Родительское окно
            title: Заголовок
            prompt: Подсказка
            initial_value: Начальное значение
            width: Ширина
            height: Высота
        """
        super().__init__(parent, title, width, height)
        
        # Контент
        content = ctk.CTkFrame(self, fg_color=DarkTheme.BG_SECONDARY, corner_radius=10)
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Подсказка
        ctk.CTkLabel(
            content,
            text=prompt,
            font=(DarkTheme.FONT_FAMILY, 12),
            text_color=DarkTheme.TEXT_PRIMARY
        ).pack(padx=20, pady=(20, 10))
        
        # Поле ввода
        self.entry = ctk.CTkEntry(
            content,
            fg_color=DarkTheme.BG_TERTIARY,
            border_color=DarkTheme.BORDER_PRIMARY,
            text_color=DarkTheme.TEXT_PRIMARY
        )
        self.entry.pack(fill='x', padx=20, pady=(0, 20))
        self.entry.insert(0, initial_value)
        self.entry.focus_set()
        
        # Кнопки
        btn_frame = ctk.CTkFrame(content, fg_color='transparent')
        btn_frame.pack(side='bottom', pady=(20, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="OK",
            command=self._on_ok,
            fg_color=DarkTheme.BUTTON_PRIMARY,
            hover_color=DarkTheme.BUTTON_PRIMARY_HOVER,
            width=100
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self._on_cancel,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            width=100
        ).pack(side='left', padx=5)
        
        # Enter для подтверждения
        self.entry.bind('<Return>', lambda e: self._on_ok())
    
    def _on_ok(self):
        self.result = self.entry.get()
        self.destroy()
    
    def _on_cancel(self):
        self.result = None
        self.destroy()