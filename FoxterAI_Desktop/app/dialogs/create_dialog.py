"""
Диалог создания лицензии с премиум дизайном
Поддержка универсальных лицензий без привязки к роботу
ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Desktop/app/dialogs/create_dialog.py
ИСПРАВЛЕНО: Правильная высота окна, украинский номер, видимость кнопок
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from themes.dark_theme import DarkTheme


class CreateLicenseDialog(ctk.CTkToplevel):
    """Универсальный диалог создания лицензии с премиум дизайном"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.result = None
        
        # Настройка окна - УВЕЛИЧЕНА ВЫСОТА
        self.title("🔑 Создание универсальной лицензии")
        self.geometry("600x720")
        self.configure(fg_color=DarkTheme.CHARCOAL_BLACK)
        
        # Центрирование окна
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 360
        self.geometry(f"600x720+{x}+{y}")
        
        # Модальное окно
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        # Создаем элементы
        self._create_widgets()
        
        # Фокус на первое поле
        self.name_entry.focus_set()
    
    def _create_widgets(self):
        """Создание виджетов с премиум дизайном"""
        
        # Основной скроллируемый контейнер
        main_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color=DarkTheme.CHARCOAL_BLACK,
            scrollbar_button_color=DarkTheme.JADE_GREEN,
            scrollbar_button_hover_color=DarkTheme.SOFT_MINT
        )
        main_scroll.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ===== ЗАГОЛОВОК =====
        header_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=DarkTheme.DEEP_EMERALD,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            height=60
        )
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_container = ctk.CTkFrame(header_frame, fg_color='transparent')
        title_container.pack(expand=True)
        
        ctk.CTkLabel(
            title_container,
            text="🔑",
            font=("Segoe UI Emoji", 24)
        ).pack()
        
        ctk.CTkLabel(
            title_container,
            text="Универсальная лицензия",
            font=("Montserrat", 18, "bold"),
            text_color=DarkTheme.PURE_WHITE
        ).pack()
        
        # ===== ИНФОРМАЦИОННЫЙ БЛОК =====
        info_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            border_width=1,
            border_color=DarkTheme.JADE_GREEN
        )
        info_frame.pack(fill='x', pady=(0, 15))
        
        info_text = """💡 Универсальная система активации:
• Создается ключ без привязки к конкретному роботу
• При первой активации робот автоматически фиксирует ключ
• Один ключ = один робот + один счет
• Защита от использования на других счетах"""
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Inter", 11),
            text_color=DarkTheme.SOFT_MINT,
            justify='left'
        ).pack(padx=15, pady=10)
        
        # ===== ФОРМА =====
        form_frame = ctk.CTkFrame(main_scroll, fg_color='transparent')
        form_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Имя клиента
        self._create_input_field(form_frame, "👤 Имя клиента *", 
                                 "name_entry", "Введите полное имя")
        
        # Телефон - УКРАИНСКИЙ ФОРМАТ
        self._create_input_field(form_frame, "📱 Телефон", 
                                 "phone_entry", "+380 (XX) XXX-XX-XX")
        
        # Telegram
        self._create_input_field(form_frame, "💬 Telegram", 
                                 "telegram_entry", "@username")
        
        # Срок действия
        duration_frame = ctk.CTkFrame(form_frame, fg_color='transparent')
        duration_frame.pack(fill='x', pady=(15, 10))
        
        ctk.CTkLabel(
            duration_frame,
            text="⏱️ Срок действия",
            font=("Inter", 14),
            text_color=DarkTheme.PURE_WHITE
        ).pack(anchor='w', pady=(0, 5))
        
        self.duration_var = ctk.StringVar(value="1")
        
        duration_options = ctk.CTkFrame(
            duration_frame,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            corner_radius=DarkTheme.RADIUS_NORMAL,
            height=50
        )
        duration_options.pack(fill='x')
        duration_options.pack_propagate(False)
        
        # Контейнер для радио-кнопок
        radio_container = ctk.CTkFrame(duration_options, fg_color='transparent')
        radio_container.pack(expand=True)
        
        durations = [
            ("1 месяц", "1"),
            ("3 месяца", "3"),
            ("6 месяцев", "6"),
            ("12 месяцев", "12")
        ]
        
        for text, value in durations:
            radio = ctk.CTkRadioButton(
                radio_container,
                text=text,
                variable=self.duration_var,
                value=value,
                fg_color=DarkTheme.JADE_GREEN,
                hover_color=DarkTheme.SOFT_MINT,
                text_color=DarkTheme.WARM_GRAY,
                font=("Inter", 12),
                radiobutton_width=18,
                radiobutton_height=18
            )
            radio.pack(side='left', padx=12)
        
        # Заметки
        notes_label = ctk.CTkLabel(
            form_frame,
            text="📝 Заметки",
            font=("Inter", 14),
            text_color=DarkTheme.PURE_WHITE
        )
        notes_label.pack(anchor='w', pady=(15, 5))
        
        self.notes_entry = ctk.CTkTextbox(
            form_frame,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            border_color=DarkTheme.JADE_GREEN,
            border_width=1,
            text_color=DarkTheme.PURE_WHITE,
            font=("Inter", 12),
            height=80,
            width=540
        )
        self.notes_entry.pack(fill='x')
        
        # ===== КНОПКИ (ФИКСИРОВАННОЕ ПОЛОЖЕНИЕ) =====
        # Создаем контейнер для кнопок внизу окна
        button_container = ctk.CTkFrame(self, fg_color=DarkTheme.CHARCOAL_BLACK)
        button_container.pack(side='bottom', fill='x', padx=20, pady=(10, 20))
        
        button_frame = ctk.CTkFrame(button_container, fg_color='transparent')
        button_frame.pack()
        
        # Кнопка создать
        create_btn = ctk.CTkButton(
            button_frame,
            text="✨ Создать ключ",
            command=self._on_create,
            fg_color=DarkTheme.JADE_GREEN,
            hover_color=DarkTheme.SOFT_MINT,
            text_color=DarkTheme.CHARCOAL_BLACK,
            font=("Inter", 14, "bold"),
            width=240,
            height=45,
            corner_radius=DarkTheme.RADIUS_NORMAL
        )
        create_btn.pack(side='left', padx=5)
        
        # Кнопка отмена
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Отмена",
            command=self.destroy,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            hover_color=DarkTheme.BG_HOVER,
            text_color=DarkTheme.PURE_WHITE,
            font=("Inter", 14, "bold"),
            width=240,
            height=45,
            corner_radius=DarkTheme.RADIUS_NORMAL
        )
        cancel_btn.pack(side='left', padx=5)
    
    def _create_input_field(self, parent, label_text, attr_name, placeholder):
        """Создание поля ввода с меткой"""
        
        # Метка
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Inter", 14),
            text_color=DarkTheme.PURE_WHITE
        )
        label.pack(anchor='w', pady=(10, 5))
        
        # Поле ввода
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color=DarkTheme.GRAPHITE_GRAY,
            border_color=DarkTheme.JADE_GREEN,
            border_width=1,
            text_color=DarkTheme.PURE_WHITE,
            placeholder_text_color=DarkTheme.WARM_GRAY,
            font=("Inter", 13),
            height=40,
            width=540
        )
        entry.pack(fill='x', pady=(0, 10))
        
        # Сохраняем ссылку на поле
        setattr(self, attr_name, entry)
    
    def _on_create(self):
        """Обработка создания универсальной лицензии"""
        
        # Получаем данные
        client_name = self.name_entry.get().strip()
        
        # Проверка обязательного поля
        if not client_name:
            messagebox.showerror(
                "Ошибка",
                "Введите имя клиента!",
                parent=self
            )
            self.name_entry.focus_set()
            return
        
        # Получаем телефон
        client_contact = self.phone_entry.get().strip()
        
        # Получаем Telegram
        client_telegram = self.telegram_entry.get().strip()
        
        # Собираем данные для универсальной лицензии
        # robot_name НЕ указывается - он зафиксируется при активации
        self.result = {
            'client_name': client_name,
            'client_contact': client_contact,
            'client_telegram': client_telegram,
            'months': int(self.duration_var.get()),
            'notes': self.notes_entry.get('1.0', 'end-1c').strip(),
            'universal': True  # Флаг универсальной лицензии
        }
        
        # Показываем информационное окно об успехе
        self._show_success_dialog()
    
    def _show_success_dialog(self):
        """Показать диалог успешного создания"""
        info_dialog = ctk.CTkToplevel(self)
        info_dialog.title("✅ Лицензия создана")
        info_dialog.geometry("500x320")
        info_dialog.configure(fg_color=DarkTheme.CHARCOAL_BLACK)
        
        # Центрирование
        info_dialog.update_idletasks()
        x = (info_dialog.winfo_screenwidth() // 2) - 250
        y = (info_dialog.winfo_screenheight() // 2) - 160
        info_dialog.geometry(f"500x320+{x}+{y}")
        
        info_dialog.transient(self)
        info_dialog.grab_set()
        info_dialog.resizable(False, False)
        
        # Содержимое
        content = ctk.CTkFrame(info_dialog, fg_color=DarkTheme.CHARCOAL_BLACK)
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Иконка успеха
        success_frame = ctk.CTkFrame(
            content,
            fg_color=DarkTheme.JADE_GREEN,
            corner_radius=50,
            width=80,
            height=80
        )
        success_frame.pack(pady=20)
        success_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            success_frame,
            text="✅",
            font=("Segoe UI Emoji", 36),
            text_color=DarkTheme.CHARCOAL_BLACK
        ).place(relx=0.5, rely=0.5, anchor='center')
        
        # Заголовок
        ctk.CTkLabel(
            content,
            text="Универсальная лицензия создана!",
            font=("Montserrat", 18, "bold"),
            text_color=DarkTheme.PURE_WHITE
        ).pack(pady=(10, 15))
        
        # Информационный текст
        info_text = """Ключ готов к использованию любым роботом.
При первой активации робот автоматически
зафиксирует лицензию за собой и счетом.

После фиксации ключ будет работать только
с этим роботом и счетом."""
        
        ctk.CTkLabel(
            content,
            text=info_text,
            font=("Inter", 12),
            text_color=DarkTheme.WARM_GRAY,
            justify='center'
        ).pack()
        
        # Кнопка закрыть
        ctk.CTkButton(
            content,
            text="Понятно",
            command=lambda: [info_dialog.destroy(), self.destroy()],
            fg_color=DarkTheme.JADE_GREEN,
            hover_color=DarkTheme.SOFT_MINT,
            text_color=DarkTheme.CHARCOAL_BLACK,
            font=("Inter", 14, "bold"),
            width=150,
            height=40
        ).pack(pady=(25, 0))


# Алиас для обратной совместимости
UniversalCreateDialog = CreateLicenseDialog