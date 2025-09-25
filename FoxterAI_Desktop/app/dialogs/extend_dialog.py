"""
Диалог продления лицензии с премиум дизайном и анимациями
ИСПРАВЛЕНО: Добавлен скролл для корректного отображения всех элементов
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
from app.dialogs.base_dialog import CustomDialog
from themes.dark_theme import DarkTheme


class ExtendLicenseDialog(CustomDialog):
    """Диалог продления лицензии с визуальными эффектами"""
    
    def __init__(self, parent, license):
        """
        Инициализация диалога продления
        
        Args:
            parent: Родительское окно
            license: Данные лицензии для продления
        """
        self.license = license
        
        # Извлекаем данные
        if hasattr(license, '__dict__'):
            self.license_data = license.__dict__
        else:
            self.license_data = license
        
        # Получаем ключ для заголовка
        key = self.license_data.get('license_key', 'Unknown')
        short_key = f"{key[:20]}..." if len(key) > 20 else key
        
        # Увеличена высота для комфортного отображения
        super().__init__(parent, f"⏰ Продление: {short_key}", 450, 550)
        
        # Результат (количество месяцев)
        self.result = None
        
        # Создаем интерфейс
        self._create_ui()
    
    def _create_ui(self):
        """Создание интерфейса диалога"""
        # Главный контейнер с градиентом
        main_frame = ctk.CTkFrame(
            self,
            fg_color=DarkTheme.BG_SECONDARY,
            corner_radius=12
        )
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ИСПРАВЛЕНО: Добавлен скроллируемый фрейм
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=DarkTheme.SCROLLBAR_THUMB_HOVER
        )
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Информация о лицензии
        self._create_license_info(scroll_frame)
        
        # Выбор срока продления
        self._create_extension_options(scroll_frame)
        
        # Предпросмотр новой даты
        self._create_preview_section(scroll_frame)
        
        # Кнопки внизу (не в скролле)
        self._create_buttons(main_frame)
    
    def _create_license_info(self, parent):
        """Создать блок с информацией о лицензии"""
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=10
        )
        info_frame.pack(fill='x', padx=10, pady=(10, 10))
        
        # Заголовок блока
        header = ctk.CTkFrame(info_frame, fg_color='transparent')
        header.pack(fill='x', padx=15, pady=(12, 8))
        
        ctk.CTkLabel(
            header,
            text="📋",
            font=(DarkTheme.FONT_FAMILY, 20)
        ).pack(side='left', padx=(0, 8))
        
        ctk.CTkLabel(
            header,
            text="Информация о лицензии",
            text_color=DarkTheme.NEON_BLUE,
            font=(DarkTheme.FONT_FAMILY, 13, "bold")
        ).pack(side='left')
        
        # Детали лицензии
        details_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
        details_frame.pack(fill='x', padx=15, pady=(0, 12))
        
        # Клиент
        self._create_info_row(details_frame, "Клиент:",
                             self.license_data.get('client_name', 'Не указан'))
        
        # Текущий статус
        status = self.license_data.get('status', 'unknown')
        status_text = {
            'active': 'Активна',
            'expired': 'Истекла',
            'blocked': 'Заблокирована',
            'created': 'Не активирована'
        }.get(status, status.upper())
        
        status_color = {
            'active': DarkTheme.STATUS_ACTIVE,
            'expired': DarkTheme.STATUS_WARNING,
            'blocked': DarkTheme.STATUS_EXPIRED,
            'created': DarkTheme.TEXT_SECONDARY
        }.get(status, DarkTheme.TEXT_PRIMARY)
        
        self._create_info_row(details_frame, "Статус:", status_text, status_color)
        
        # Дата истечения
        expiry_date = self.license_data.get('expiry_date', 'Не установлена')
        if expiry_date and expiry_date != 'Не установлена':
            try:
                exp_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                days_left = (exp_dt - datetime.now()).days
                
                if days_left > 0:
                    expiry_text = f"{expiry_date[:10]} (осталось {days_left} дн.)"
                    color = DarkTheme.STATUS_ACTIVE if days_left > 30 else DarkTheme.STATUS_WARNING
                else:
                    expiry_text = f"{expiry_date[:10]} (истекла {abs(days_left)} дн. назад)"
                    color = DarkTheme.STATUS_EXPIRED
            except:
                expiry_text = expiry_date[:10] if len(expiry_date) > 10 else expiry_date
                color = DarkTheme.TEXT_PRIMARY
        else:
            expiry_text = "Не установлена"
            color = DarkTheme.TEXT_SECONDARY
        
        self._create_info_row(details_frame, "Истекает:", expiry_text, color)
    
    def _create_info_row(self, parent, label: str, value: str, value_color=None):
        """Создать строку информации"""
        row = ctk.CTkFrame(parent, fg_color='transparent')
        row.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            row,
            text=label,
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11),
            width=80,
            anchor='w'
        ).pack(side='left')
        
        ctk.CTkLabel(
            row,
            text=value,
            text_color=value_color or DarkTheme.TEXT_PRIMARY,
            font=(DarkTheme.FONT_FAMILY, 11, "bold")
        ).pack(side='left')
    
    def _create_extension_options(self, parent):
        """Создать опции продления"""
        # Заголовок секции
        ctk.CTkLabel(
            parent,
            text="⏱️ Выберите срок продления",
            text_color=DarkTheme.NEON_GREEN,
            font=(DarkTheme.FONT_FAMILY, 13, "bold")
        ).pack(pady=(15, 10))
        
        # Опции продления
        options_frame = ctk.CTkFrame(parent, fg_color='transparent')
        options_frame.pack(fill='x', padx=10)
        
        self.months_var = tk.IntVar(value=1)
        
        # Создаем кнопки-опции с анимацией
        options = [
            (1, "1 месяц", DarkTheme.NEON_BLUE),
            (3, "3 месяца", DarkTheme.NEON_GREEN),
            (6, "6 месяцев", DarkTheme.NEON_YELLOW),
            (12, "12 месяцев", DarkTheme.NEON_PURPLE)
        ]
        
        for months, text, color in options:
            btn_frame = ctk.CTkFrame(options_frame, fg_color='transparent')
            btn_frame.pack(fill='x', pady=4)
            
            radio = ctk.CTkRadioButton(
                btn_frame,
                text="",
                variable=self.months_var,
                value=months,
                fg_color=color,
                hover_color=color,
                command=self._update_preview,
                width=20
            )
            radio.pack(side='left', padx=(0, 10))
            
            label = ctk.CTkButton(
                btn_frame,
                text=text,
                fg_color=DarkTheme.BG_TERTIARY,
                hover_color=DarkTheme.BG_PRIMARY,
                text_color=DarkTheme.TEXT_PRIMARY,
                anchor='w',
                corner_radius=6,
                command=lambda m=months: self._select_months(m)
            )
            label.pack(side='left', fill='x', expand=True)
    
    def _select_months(self, months: int):
        """Выбрать количество месяцев"""
        self.months_var.set(months)
        self._update_preview()
    
    def _create_preview_section(self, parent):
        """Создать секцию предпросмотра"""
        preview_frame = ctk.CTkFrame(
            parent,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=10,
            border_width=2,
            border_color=DarkTheme.NEON_GREEN_DIM
        )
        preview_frame.pack(fill='x', padx=10, pady=(15, 10))
        
        ctk.CTkLabel(
            preview_frame,
            text="📅 Новая дата истечения:",
            text_color=DarkTheme.TEXT_SECONDARY,
            font=(DarkTheme.FONT_FAMILY, 11)
        ).pack(pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="",
            text_color=DarkTheme.NEON_GREEN,
            font=(DarkTheme.FONT_FAMILY, 16, "bold")
        )
        self.preview_label.pack(pady=(0, 10))
        
        # Обновляем предпросмотр
        self._update_preview()
    
    def _update_preview(self):
        """Обновить предпросмотр новой даты"""
        months = self.months_var.get()
        
        # Определяем базовую дату
        current_expiry = self.license_data.get('expiry_date')
        if current_expiry:
            try:
                base_date = datetime.fromisoformat(current_expiry.replace('Z', '+00:00'))
                # Если лицензия истекла, продлеваем от сегодня
                if base_date < datetime.now():
                    base_date = datetime.now()
            except:
                base_date = datetime.now()
        else:
            base_date = datetime.now()
        
        # Вычисляем новую дату
        new_date = base_date + timedelta(days=months * 30)
        
        # Форматируем для отображения
        formatted_date = new_date.strftime("%d.%m.%Y")
        days_total = months * 30
        
        self.preview_label.configure(
            text=f"{formatted_date}\n(+{days_total} дней)"
        )
        
        # Анимация пульсации при изменении
        self._pulse_widget(self.preview_label)
    
    def _pulse_widget(self, widget):
        """Анимация пульсации виджета"""
        original_color = widget.cget('text_color')
        
        def pulse(step=0):
            if step < 3:
                if step % 2 == 0:
                    widget.configure(text_color=DarkTheme.NEON_GREEN)
                else:
                    widget.configure(text_color=DarkTheme.NEON_GREEN_DIM)
                self.after(150, lambda: pulse(step + 1))
            else:
                widget.configure(text_color=original_color)
        
        pulse()
    
    def _create_buttons(self, parent):
        """Создать кнопки действий"""
        # ИСПРАВЛЕНО: кнопки теперь в основном фрейме, а не в скролле
        btn_frame = ctk.CTkFrame(parent, fg_color='transparent')
        btn_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        # Центрируем кнопки
        button_container = ctk.CTkFrame(btn_frame, fg_color='transparent')
        button_container.pack()
        
        # Кнопка продления
        extend_btn = ctk.CTkButton(
            button_container,
            text="✅ Продлить",
            command=self._on_extend,
            fg_color=DarkTheme.NEON_GREEN,
            hover_color=DarkTheme.NEON_GREEN_DIM,
            text_color=DarkTheme.CHARCOAL_BLACK,
            width=120,
            height=35,
            corner_radius=8,
            font=(DarkTheme.FONT_FAMILY, 12, "bold")
        )
        extend_btn.grid(row=0, column=0, padx=5)
        
        # Эффект свечения для кнопки
        self._add_glow_effect(extend_btn)
        
        # Кнопка отмены
        cancel_btn = ctk.CTkButton(
            button_container,
            text="❌ Отмена",
            command=self._on_cancel,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            text_color=DarkTheme.TEXT_PRIMARY,
            width=120,
            height=35,
            corner_radius=8,
            font=(DarkTheme.FONT_FAMILY, 12)
        )
        cancel_btn.grid(row=0, column=1, padx=5)
    
    def _add_glow_effect(self, button):
        """Добавить эффект свечения кнопке"""
        def on_enter(e):
            button.configure(border_width=2, border_color=DarkTheme.NEON_GREEN)
        
        def on_leave(e):
            button.configure(border_width=0)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _on_extend(self):
        """Обработка продления"""
        self.result = self.months_var.get()
        
        # Анимация закрытия
        self._animate_out()
    
    def _on_cancel(self):
        """Обработка отмены"""
        self.result = None
        self._animate_out()