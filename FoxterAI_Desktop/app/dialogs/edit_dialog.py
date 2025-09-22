"""
Диалог редактирования лицензии с премиум дизайном
"""

import customtkinter as ctk
from app.dialogs.base_dialog import CustomDialog
from themes.dark_theme import DarkTheme


class EditLicenseDialog(CustomDialog):
    """Диалог редактирования существующей лицензии"""
    
    def __init__(self, parent, license):
        """
        Инициализация диалога редактирования
        
        Args:
            parent: Родительское окно
            license: Данные лицензии для редактирования
        """
        # Сохраняем данные лицензии
        self.license = license
        
        # Извлекаем данные
        if hasattr(license, '__dict__'):
            self.license_data = license.__dict__
        else:
            self.license_data = license
        
        # Получаем ключ лицензии для заголовка
        key = self.license_data.get('license_key', 'Unknown')
        short_key = f"{key[:20]}..." if len(key) > 20 else key
        
        super().__init__(parent, f"✏️ Редактирование: {short_key}", 500, 550)
        
        # Результат диалога
        self.result = None
        
        # Создаем форму
        self._create_form()
    
    def _create_form(self):
        """Создание формы редактирования"""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self, fg_color=DarkTheme.BG_SECONDARY, corner_radius=10)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Скроллируемый контент
        content = ctk.CTkScrollableFrame(
            main_frame,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.BORDER_PRIMARY,
            scrollbar_button_hover_color=DarkTheme.NEON_BLUE_DIM
        )
        content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Поля формы
        self.fields = {}
        
        # Информация о лицензии (не редактируемая)
        self._create_info_section(content)
        
        # Редактируемые поля
        self._create_editable_section(content)
        
        # Заметки
        self._create_notes_section(content)
        
        # Кнопки
        self._create_buttons()
    
    def _create_info_section(self, parent):
        """Создать секцию с информацией о лицензии"""
        # Заголовок секции
        info_frame = ctk.CTkFrame(parent, fg_color=DarkTheme.BG_TERTIARY, corner_radius=8)
        info_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="🔐 Информация о лицензии",
            text_color=DarkTheme.NEON_BLUE,
            font=(DarkTheme.FONT_FAMILY, 13, "bold")
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        # Ключ лицензии
        key_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
        key_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(
            key_frame,
            text="Ключ:",
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11),
            width=100,
            anchor='w'
        ).pack(side='left')
        
        ctk.CTkLabel(
            key_frame,
            text=self.license_data.get('license_key', 'N/A'),
            text_color=DarkTheme.TEXT_PRIMARY,
            font=(DarkTheme.FONT_FAMILY, 11, "bold")
        ).pack(side='left')
        
        # Статус
        status_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
        status_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(
            status_frame,
            text="Статус:",
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11),
            width=100,
            anchor='w'
        ).pack(side='left')
        
        status = self.license_data.get('status', 'unknown')
        status_colors = {
            'active': DarkTheme.STATUS_ACTIVE,
            'expired': DarkTheme.STATUS_WARNING,
            'blocked': DarkTheme.STATUS_EXPIRED,
            'created': DarkTheme.TEXT_SECONDARY
        }
        
        ctk.CTkLabel(
            status_frame,
            text=status.upper(),
            text_color=status_colors.get(status, DarkTheme.TEXT_PRIMARY),
            font=(DarkTheme.FONT_FAMILY, 11, "bold")
        ).pack(side='left')
        
        # Даты
        dates_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
        dates_frame.pack(fill='x', padx=15, pady=(5, 10))
        
        ctk.CTkLabel(
            dates_frame,
            text="Создана:",
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11),
            width=100,
            anchor='w'
        ).pack(side='left')
        
        ctk.CTkLabel(
            dates_frame,
            text=self.license_data.get('created_date', 'N/A')[:10],
            text_color=DarkTheme.TEXT_PRIMARY,
            font=(DarkTheme.FONT_FAMILY, 11)
        ).pack(side='left')
    
    def _create_editable_section(self, parent):
        """Создать секцию с редактируемыми полями"""
        ctk.CTkLabel(
            parent,
            text="👤 Данные клиента",
            text_color=DarkTheme.NEON_GREEN,
            font=(DarkTheme.FONT_FAMILY, 13, "bold")
        ).pack(anchor='w', pady=(10, 10))
        
        # Имя клиента
        self._create_field(parent, "Имя клиента:", "client_name",
                          self.license_data.get('client_name', ''))
        
        # Телефон
        self._create_field(parent, "Телефон:", "client_contact",
                          self.license_data.get('client_contact', ''))
        
        # Telegram
        self._create_field(parent, "Telegram:", "client_telegram",
                          self.license_data.get('client_telegram', ''))
        
        # Владелец счета
        self._create_field(parent, "Владелец счета:", "account_owner",
                          self.license_data.get('account_owner', ''))
    
    def _create_field(self, parent, label: str, key: str, value: str):
        """Создать поле ввода"""
        ctk.CTkLabel(
            parent,
            text=label,
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11)
        ).pack(anchor='w', pady=(8, 3))
        
        entry = ctk.CTkEntry(
            parent,
            fg_color=DarkTheme.BG_TERTIARY,
            border_color=DarkTheme.BORDER_PRIMARY,
            text_color=DarkTheme.TEXT_PRIMARY,
            height=32
        )
        entry.pack(fill='x', pady=(0, 5))
        entry.insert(0, value or '')
        
        self.fields[key] = entry
    
    def _create_notes_section(self, parent):
        """Создать секцию заметок"""
        ctk.CTkLabel(
            parent,
            text="📝 Заметки",
            text_color=DarkTheme.NEON_YELLOW,
            font=(DarkTheme.FONT_FAMILY, 13, "bold")
        ).pack(anchor='w', pady=(15, 8))
        
        self.notes_text = ctk.CTkTextbox(
            parent,
            fg_color=DarkTheme.BG_TERTIARY,
            height=80,
            border_width=1,
            border_color=DarkTheme.BORDER_PRIMARY,
            text_color=DarkTheme.TEXT_PRIMARY
        )
        self.notes_text.pack(fill='x', pady=(0, 10))
        
        # Вставляем текущие заметки
        current_notes = self.license_data.get('notes', '')
        if current_notes:
            self.notes_text.insert('1.0', current_notes)
    
    def _create_buttons(self):
        """Создать кнопки действий"""
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(side='bottom', pady=15)
        
        # Кнопка сохранения с эффектом свечения
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            command=self._on_save,
            fg_color=DarkTheme.NEON_GREEN,
            hover_color=DarkTheme.NEON_GREEN_DIM,
            width=120,
            height=35,
            corner_radius=8
        )
        save_btn.pack(side='left', padx=5)
        
        # Кнопка отмены
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Отмена",
            command=self._on_cancel,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            width=120,
            height=35,
            corner_radius=8
        )
        cancel_btn.pack(side='left', padx=5)
    
    def _validate_form(self) -> bool:
        """Валидация формы"""
        # Проверяем телефон если изменен
        phone = self.fields['client_contact'].get().strip()
        if phone and not self._validate_phone(phone):
            self._show_error("Неверный формат телефона!")
            return False
        
        # Проверяем Telegram если изменен
        telegram = self.fields['client_telegram'].get().strip()
        if telegram and not self._validate_telegram(telegram):
            self._show_error("Неверный формат Telegram!")
            return False
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Валидация телефона"""
        clean = ''.join(c for c in phone if c.isdigit())
        return len(clean) >= 10 or len(clean) == 0
    
    def _validate_telegram(self, telegram: str) -> bool:
        """Валидация Telegram username"""
        if not telegram:
            return True
        if telegram.startswith('@'):
            telegram = telegram[1:]
        return len(telegram) >= 3 and telegram.replace('_', '').isalnum()
    
    def _show_error(self, message: str):
        """Показать ошибку с анимацией"""
        error_label = ctk.CTkLabel(
            self,
            text=f"⚠️ {message}",
            text_color=DarkTheme.STATUS_EXPIRED,
            font=(DarkTheme.FONT_FAMILY, 12, "bold"),
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=6
        )
        error_label.place(relx=0.5, rely=0.92, anchor='center')
        
        # Анимация исчезновения
        self.after(3000, error_label.destroy)
    
    def _on_save(self):
        """Обработка сохранения изменений"""
        if not self._validate_form():
            return
        
        # Собираем только измененные данные
        self.result = {}
        
        for key, entry in self.fields.items():
            new_value = entry.get().strip()
            old_value = self.license_data.get(key, '')
            
            if new_value != old_value:
                self.result[key] = new_value
        
        # Проверяем заметки
        new_notes = self.notes_text.get('1.0', 'end-1c').strip()
        old_notes = self.license_data.get('notes', '').strip()
        
        if new_notes != old_notes:
            self.result['notes'] = new_notes
        
        # Если ничего не изменено
        if not self.result:
            self.result = None
        
        self.destroy()
    
    def _on_cancel(self):
        """Обработка отмены"""
        self.result = None
        self.destroy()