"""
Диалог деталей лицензии с премиум дизайном
ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Desktop/app/dialogs/details_dialog.py
ИСПРАВЛЕНО: Убрана кнопка печати, исправлено отображение владельца счета и дней
"""

import customtkinter as ctk
from datetime import datetime
import json
from tkinter import filedialog
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.dialogs.base_dialog import CustomDialog
from themes.dark_theme import DarkTheme


class LicenseDetailsDialog(CustomDialog):
    """Диалог с детальной информацией о лицензии"""
    
    def __init__(self, parent, license):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            license: Данные лицензии для отображения
        """
        # Извлекаем данные из объекта или словаря
        if hasattr(license, '__dict__'):
            self.license_data = license.__dict__
        else:
            self.license_data = license
        
        # Получаем ключ для заголовка
        key = self.license_data.get('license_key', 'Unknown')
        short_key = f"{key[:20]}..." if len(key) > 20 else key
        
        super().__init__(parent, f"📋 Детали лицензии: {short_key}", 700, 600)
        
        self._create_ui()
    
    def _create_ui(self):
        """Создание интерфейса с табами"""
        # Главный контейнер
        main_frame = ctk.CTkFrame(self, fg_color=DarkTheme.BG_SECONDARY)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок с ключом
        self._create_header(main_frame)
        
        # Табы с информацией
        self._create_tabs(main_frame)
        
        # Кнопки действий
        self._create_action_buttons(main_frame)
    
    def _create_header(self, parent):
        """Создание заголовка с ключом лицензии"""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=10
        )
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        # Контейнер для ключа
        key_container = ctk.CTkFrame(header_frame, fg_color='transparent')
        key_container.pack(fill='x', padx=15, pady=15)
        
        # Ключ лицензии
        key_label = ctk.CTkLabel(
            key_container,
            text="🔑 Ключ лицензии:",
            font=(DarkTheme.FONT_FAMILY, 12),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        key_label.pack(side='left', padx=(0, 10))
        
        key_value = ctk.CTkLabel(
            key_container,
            text=self.license_data.get('license_key', 'N/A'),
            font=(DarkTheme.FONT_FAMILY_MONO, 14, 'bold'),
            text_color=DarkTheme.CHAMPAGNE_GOLD
        )
        key_value.pack(side='left')
        
        # Кнопка копирования
        copy_btn = ctk.CTkButton(
            key_container,
            text="📋 Копировать",
            width=100,
            height=28,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            command=lambda: self._copy_to_clipboard(self.license_data.get('license_key'))
        )
        copy_btn.pack(side='right', padx=(10, 0))
        
        # Статус
        status = self.license_data.get('status', 'unknown')
        status_colors = {
            'active': DarkTheme.STATUS_ACTIVE,
            'expired': DarkTheme.STATUS_EXPIRED,
            'blocked': DarkTheme.STATUS_BLOCKED,
            'created': DarkTheme.STATUS_PENDING
        }
        
        status_display = self._get_status_display(status)
        status_label = ctk.CTkLabel(
            key_container,
            text=status_display,
            font=(DarkTheme.FONT_FAMILY, 12, 'bold'),
            text_color=status_colors.get(status, DarkTheme.TEXT_SECONDARY)
        )
        status_label.pack(side='right', padx=(10, 10))
    
    def _create_tabs(self, parent):
        """Создание табов с информацией"""
        # Контейнер для табов
        tab_view = ctk.CTkTabview(
            parent,
            fg_color=DarkTheme.BG_SECONDARY,
            segmented_button_fg_color=DarkTheme.BG_TERTIARY,
            segmented_button_selected_color=DarkTheme.JADE_GREEN,
            segmented_button_unselected_color=DarkTheme.BG_TERTIARY,
            segmented_button_selected_hover_color=DarkTheme.SOFT_MINT,
            segmented_button_unselected_hover_color=DarkTheme.BG_HOVER,
            text_color=DarkTheme.TEXT_SECONDARY,
            text_color_disabled=DarkTheme.TEXT_DISABLED
        )
        tab_view.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Создаем табы
        tab_general = tab_view.add("📊 Основное")
        tab_client = tab_view.add("👤 Клиент")
        tab_technical = tab_view.add("⚙️ Технические")
        tab_history = tab_view.add("📝 История")
        
        # Заполняем табы
        self._fill_general_tab(tab_general)
        self._fill_client_tab(tab_client)
        self._fill_technical_tab(tab_technical)
        self._fill_history_tab(tab_history)
    
    def _fill_general_tab(self, parent):
        """Заполнение таба с основной информацией"""
        # Скроллируемый фрейм
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=DarkTheme.SCROLLBAR_THUMB_HOVER
        )
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # ИСПРАВЛЕНО: Правильное отображение оставшихся дней
        days_left_display = self._get_proper_days_left_display()
        
        # Информация
        info_items = [
            ("📅 Дата создания", self._format_date(self.license_data.get('created_date'))),
            ("⏰ Срок действия", f"{self.license_data.get('months', 1)} мес."),
            ("📆 Дата активации", self._format_date(self.license_data.get('activation_date', '-'))),
            ("📆 Дата истечения", self._format_date(self.license_data.get('expiry_date', '-'))),
            ("⏳ Осталось дней", days_left_display),  # ИСПРАВЛЕНО
            ("🤖 Робот", self.license_data.get('robot_name') or 'Не привязан'),
            ("📈 Версия робота", self.license_data.get('robot_version') or '-'),
            ("💼 Тип счета", self.license_data.get('account_type', 'Real')),
            ("💰 Последний баланс", self._format_balance(self.license_data.get('last_balance', 0))),
            ("🔢 Макс. счетов", str(self.license_data.get('max_accounts', 1)))
        ]
        
        for label, value in info_items:
            self._add_info_row(scroll_frame, label, value)
    
    def _fill_client_tab(self, parent):
        """Заполнение таба с информацией о клиенте"""
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=DarkTheme.SCROLLBAR_THUMB_HOVER
        )
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # ИСПРАВЛЕНО: Правильное отображение владельца счета
        account_owner = self._get_proper_account_owner()
        
        client_items = [
            ("👤 Имя клиента", self.license_data.get('client_name') or '-'),
            ("📞 Телефон", self.license_data.get('client_contact') or '-'),
            ("💬 Telegram", self.license_data.get('client_telegram') or '-'),
            ("🏦 Владелец счета", account_owner),  # ИСПРАВЛЕНО
            ("🔢 Номер счета", str(self.license_data.get('account_number')) if self.license_data.get('account_number') else '-'),
            ("🏢 Брокер", self.license_data.get('broker_name') or '-')
        ]
        
        for label, value in client_items:
            self._add_info_row(scroll_frame, label, value)
        
        # Заметки
        notes = self.license_data.get('notes')
        if notes and notes != 'None':
            notes_label = ctk.CTkLabel(
                scroll_frame,
                text="📝 Заметки:",
                font=(DarkTheme.FONT_FAMILY, 12, 'bold'),
                text_color=DarkTheme.TEXT_SECONDARY
            )
            notes_label.pack(anchor='w', pady=(15, 5), padx=10)
            
            notes_text = ctk.CTkTextbox(
                scroll_frame,
                height=100,
                fg_color=DarkTheme.BG_TERTIARY,
                text_color=DarkTheme.TEXT_PRIMARY,
                font=(DarkTheme.FONT_FAMILY, 11),
                corner_radius=8
            )
            notes_text.pack(fill='x', pady=(0, 10), padx=10)
            notes_text.insert('1.0', notes)
            notes_text.configure(state='disabled')
    
    def _fill_technical_tab(self, parent):
        """Заполнение таба с технической информацией"""
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=DarkTheme.SCROLLBAR_THUMB_HOVER
        )
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Отпечаток
        fingerprint = self.license_data.get('fingerprint')
        if fingerprint and fingerprint != 'None':
            fp_label = ctk.CTkLabel(
                scroll_frame,
                text="🔐 Отпечаток системы:",
                font=(DarkTheme.FONT_FAMILY, 12, 'bold'),
                text_color=DarkTheme.TEXT_SECONDARY
            )
            fp_label.pack(anchor='w', pady=(10, 5), padx=10)
            
            fp_text = ctk.CTkTextbox(
                scroll_frame,
                height=60,
                fg_color=DarkTheme.BG_TERTIARY,
                text_color=DarkTheme.TEXT_PRIMARY,
                font=(DarkTheme.FONT_FAMILY_MONO, 10),
                corner_radius=8
            )
            fp_text.pack(fill='x', pady=(0, 15), padx=10)
            fp_text.insert('1.0', self._format_fingerprint(fingerprint))
            fp_text.configure(state='disabled')
        
        tech_items = [
            ("🔏 Хеш отпечатка", self.license_data.get('fingerprint_hash') or '-'),
            ("💻 Версия терминала", self.license_data.get('terminal_version') or '-'),
            ("🖥️ Операционная система", self.license_data.get('os_info') or '-'),
            ("🌐 Последний IP адрес", self.license_data.get('last_ip') or '-'),
            ("📊 Количество проверок", str(self.license_data.get('check_count', 0))),
            ("🕒 Последняя проверка", self._format_date(self.license_data.get('last_check'))),
            ("📡 Последнее обновление", self._format_date(self.license_data.get('last_update'))),
            ("⚡ Счетчик heartbeat", str(self.license_data.get('heartbeat_count', 0))),
            ("❌ Неудачных проверок", str(self.license_data.get('failed_checks', 0)))
        ]
        
        for label, value in tech_items:
            self._add_info_row(scroll_frame, label, value)
    
    def _fill_history_tab(self, parent):
        """Заполнение таба с историей"""
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color='transparent',
            scrollbar_button_color=DarkTheme.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=DarkTheme.SCROLLBAR_THUMB_HOVER
        )
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Основные даты
        history_items = [
            ("🆕 Создана", self._format_date(self.license_data.get('created_date'))),
            ("✅ Активирована", self._format_date(self.license_data.get('activation_date', '-'))),
            ("🕒 Последняя проверка", self._format_date(self.license_data.get('last_check', '-'))),
            ("📍 Последний IP", self.license_data.get('last_ip') or '-'),
            ("💰 Последний баланс", self._format_balance(self.license_data.get('last_balance', 0)))
        ]
        
        for label, value in history_items:
            self._add_info_row(scroll_frame, label, value)
        
        # Статистика активности
        stats_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=DarkTheme.BG_TERTIARY,
            corner_radius=8
        )
        stats_frame.pack(fill='x', pady=20, padx=10)
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Статистика использования",
            font=(DarkTheme.FONT_FAMILY, 12, 'bold'),
            text_color=DarkTheme.CHAMPAGNE_GOLD
        )
        stats_label.pack(pady=(10, 10))
        
        # Статистика
        check_count = self.license_data.get('check_count', 0)
        heartbeat_count = self.license_data.get('heartbeat_count', 0)
        failed_checks = self.license_data.get('failed_checks', 0)
        
        stats_text = f"Проверок: {check_count} | Heartbeat: {heartbeat_count} | Ошибок: {failed_checks}"
        
        stats_info = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=(DarkTheme.FONT_FAMILY, 11),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        stats_info.pack(pady=(0, 10))
        
        # Информационное сообщение
        info_label = ctk.CTkLabel(
            scroll_frame,
            text="ℹ️ Полная история событий доступна в логах сервера",
            font=(DarkTheme.FONT_FAMILY, 10),
            text_color=DarkTheme.TEXT_SECONDARY
        )
        info_label.pack(pady=10)
    
    def _add_info_row(self, parent, label, value):
        """Добавление строки информации"""
        row_frame = ctk.CTkFrame(parent, fg_color='transparent', height=30)
        row_frame.pack(fill='x', pady=3, padx=10)
        row_frame.pack_propagate(False)
        
        # Метка
        label_widget = ctk.CTkLabel(
            row_frame,
            text=label,
            font=(DarkTheme.FONT_FAMILY, 11),
            text_color=DarkTheme.TEXT_SECONDARY,
            width=200,
            anchor='w'
        )
        label_widget.pack(side='left')
        
        # Определяем цвет значения
        value_color = DarkTheme.TEXT_PRIMARY
        
        # Проверка на пустые значения
        if value in ['-', 'N/A', 'Не активирован', 'Не привязан', None, 'None', '']:
            value_color = DarkTheme.TEXT_SECONDARY
            if value in [None, 'None', '']:
                value = '-'
        # Проверка на истечение
        elif isinstance(value, str) and 'Истек' in value:
            value_color = DarkTheme.STATUS_EXPIRED
        # Проверка на бесконечность
        elif '∞' in str(value):
            value_color = DarkTheme.STATUS_SUCCESS
        # Проверка на предупреждение
        elif '⚠️' in str(value):
            value_color = DarkTheme.STATUS_WARNING
        
        # Значение
        value_widget = ctk.CTkLabel(
            row_frame,
            text=str(value),
            font=(DarkTheme.FONT_FAMILY, 11, 'bold'),
            text_color=value_color,
            anchor='w'
        )
        value_widget.pack(side='left', expand=True, fill='x')
    
    def _create_action_buttons(self, parent):
        """Создание кнопок действий"""
        button_frame = ctk.CTkFrame(parent, fg_color='transparent')
        button_frame.pack(fill='x', padx=15, pady=(10, 15))
        
        # Кнопка закрыть
        close_btn = ctk.CTkButton(
            button_frame,
            text="Закрыть",
            width=120,
            height=35,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            font=(DarkTheme.FONT_FAMILY, 12),
            command=self.destroy
        )
        close_btn.pack(side='right')
        
        # Кнопка экспорта
        export_btn = ctk.CTkButton(
            button_frame,
            text="📤 Экспорт",
            width=120,
            height=35,
            fg_color=DarkTheme.BUTTON_SECONDARY,
            hover_color=DarkTheme.BUTTON_SECONDARY_HOVER,
            font=(DarkTheme.FONT_FAMILY, 12),
            command=self._export_license
        )
        export_btn.pack(side='right', padx=(0, 10))
        
        # ИСПРАВЛЕНО: Убрана кнопка печати
        
        # Левая сторона - кнопки действий в зависимости от статуса
        status = self.license_data.get('status', 'unknown')
        
        if status == 'created':
            # Для неактивированных лицензий - можно редактировать
            edit_btn = ctk.CTkButton(
                button_frame,
                text="✏️ Редактировать",
                width=140,
                height=35,
                fg_color=DarkTheme.BUTTON_PRIMARY,
                hover_color=DarkTheme.BUTTON_PRIMARY_HOVER,
                font=(DarkTheme.FONT_FAMILY, 12),
                command=self._open_edit_dialog
            )
            edit_btn.pack(side='left')
        
        elif status == 'active':
            # Для активных лицензий - можно продлить
            extend_btn = ctk.CTkButton(
                button_frame,
                text="⏰ Продлить",
                width=140,
                height=35,
                fg_color=DarkTheme.JADE_GREEN,
                hover_color=DarkTheme.SOFT_MINT,
                text_color=DarkTheme.CHARCOAL_BLACK,
                font=(DarkTheme.FONT_FAMILY, 12),
                command=self._open_extend_dialog
            )
            extend_btn.pack(side='left')
            
            # Кнопка блокировки
            block_btn = ctk.CTkButton(
                button_frame,
                text="🔒 Заблокировать",
                width=140,
                height=35,
                fg_color=DarkTheme.BUTTON_DANGER,
                hover_color=DarkTheme.BUTTON_DANGER_HOVER,
                font=(DarkTheme.FONT_FAMILY, 12),
                command=self._block_license
            )
            block_btn.pack(side='left', padx=(10, 0))
        
        elif status == 'blocked':
            # Для заблокированных - можно разблокировать
            unblock_btn = ctk.CTkButton(
                button_frame,
                text="🔓 Разблокировать",
                width=140,
                height=35,
                fg_color=DarkTheme.BUTTON_SUCCESS,
                hover_color=DarkTheme.BUTTON_SUCCESS_HOVER,
                font=(DarkTheme.FONT_FAMILY, 12),
                command=self._unblock_license
            )
            unblock_btn.pack(side='left')
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def _get_proper_days_left_display(self):
        """ИСПРАВЛЕНО: Правильное отображение оставшихся дней"""
        status = self.license_data.get('status', 'unknown')
        
        # Если лицензия не активирована
        if status == 'created':
            return '∞ (не активирована)'
        
        # Если лицензия заблокирована
        if status == 'blocked':
            return 'Заблокирована'
        
        # Используем days_left_text если есть
        if 'days_left_text' in self.license_data:
            return self.license_data['days_left_text']
        
        # Иначе используем days_left
        days_left = self.license_data.get('days_left')
        if days_left is not None:
            if days_left == 999 or days_left == -1:
                return '∞ (не активирована)'
            elif days_left < 0:
                return f'Истекла {abs(days_left)} дн. назад'
            elif days_left == 0:
                return '⚠️ Истекает сегодня!'
            elif days_left <= 7:
                return f'⚠️ {days_left} дн.'
            else:
                return f'{days_left} дн.'
        
        # По умолчанию
        return '-'
    
    def _get_proper_account_owner(self):
        """ИСПРАВЛЕНО: Правильное отображение владельца счета"""
        # Используем account_owner из модели License
        account_owner = self.license_data.get('account_owner')
        
        if account_owner and account_owner not in ['None', 'null', '', None]:
            return account_owner
        
        # Если счет есть но владелец не передан
        account_number = self.license_data.get('account_number')
        if account_number and account_number not in ['None', '', None]:
            return f"Счет {account_number}"
        
        # Если лицензия не активирована
        status = self.license_data.get('status', 'unknown')
        if status == 'created':
            return 'Не активирована'
        
        return '-'
    
    def _format_date(self, date_str):
        """Форматирование даты"""
        if not date_str or date_str in ['-', 'None', None, '']:
            return '-'
        
        try:
            # Пробуем разные форматы
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%d.%m.%Y %H:%M',
                '%d.%m.%Y'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    return dt.strftime('%d.%m.%Y %H:%M')
                except:
                    continue
            
            # Если не удалось распарсить, возвращаем как есть
            return str(date_str)
        except:
            return str(date_str)
    
    def _format_balance(self, balance):
        """Форматирование баланса"""
        try:
            if balance is None or balance == 'None':
                return '$0.00'
            return f'${float(balance):.2f}'
        except:
            return '$0.00'
    
    def _format_fingerprint(self, fingerprint):
        """Форматирование отпечатка"""
        if not fingerprint or fingerprint in ['-', 'None', None]:
            return '-'
        
        # Разбиваем длинный отпечаток на строки
        fp_str = str(fingerprint)
        if len(fp_str) > 80:
            # Разбиваем по 80 символов
            lines = []
            for i in range(0, len(fp_str), 80):
                lines.append(fp_str[i:i+80])
            return '\n'.join(lines)
        
        return fp_str
    
    def _get_status_display(self, status):
        """Получить отображаемый статус"""
        status_map = {
            'active': '✅ Активна',
            'expired': '⏰ Истекла',
            'blocked': '🔒 Заблокирована',
            'created': '⏳ Не активирована'
        }
        return status_map.get(status, f'❓ {status}')
    
    def _copy_to_clipboard(self, text):
        """Копирование в буфер обмена"""
        if text:
            try:
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update()
                
                # Показываем временное уведомление (можно заменить на всплывающее)
                print(f"📋 Скопировано в буфер: {text}")
                
                # Можно добавить визуальную индикацию
                if hasattr(self.master, 'set_status'):
                    self.master.set_status("📋 Ключ скопирован в буфер обмена", "success")
                    
            except Exception as e:
                print(f"❌ Ошибка копирования: {e}")
    
    def _export_license(self):
        """Экспорт данных лицензии"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON файл", "*.json"),
                    ("Текстовый файл", "*.txt"),
                    ("Все файлы", "*.*")
                ],
                initialfile=f"license_{self.license_data.get('license_key', 'unknown')}.json"
            )
            
            if filename:
                # Подготавливаем данные для экспорта
                export_data = self.license_data.copy()
                
                # Конвертируем datetime объекты в строки
                for key, value in export_data.items():
                    if isinstance(value, datetime):
                        export_data[key] = value.isoformat()
                
                # Сохраняем в файл
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"✅ Лицензия экспортирована: {filename}")
                
                if hasattr(self.master, 'set_status'):
                    self.master.set_status(f"✅ Экспортировано в {filename}", "success")
                    
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            
            if hasattr(self.master, 'show_notification'):
                self.master.show_notification(
                    "Ошибка экспорта",
                    f"Не удалось экспортировать лицензию:\n{str(e)}",
                    "error"
                )
    
    def _open_edit_dialog(self):
        """Открыть диалог редактирования"""
        # Закрываем текущий диалог
        self.destroy()
        
        # Вызываем метод родителя для открытия диалога редактирования
        if hasattr(self.master, 'edit_license_dialog'):
            self.master.edit_license_dialog(self.license_data)
    
    def _open_extend_dialog(self):
        """Открыть диалог продления"""
        # Закрываем текущий диалог
        self.destroy()
        
        # Вызываем метод родителя для открытия диалога продления
        if hasattr(self.master, 'extend_license_dialog'):
            self.master.extend_license_dialog(self.license_data)
    
    def _block_license(self):
        """Заблокировать лицензию"""
        # Закрываем текущий диалог
        self.destroy()
        
        # Вызываем метод родителя для блокировки
        if hasattr(self.master, 'block_license'):
            self.master.block_license(self.license_data)
    
    def _unblock_license(self):
        """Разблокировать лицензию"""
        # Закрываем текущий диалог
        self.destroy()
        
        # Создаем копию данных с измененным статусом для разблокировки
        license_copy = self.license_data.copy()
        license_copy['is_blocked'] = True  # Флаг что лицензия заблокирована
        
        # Вызываем метод родителя для разблокировки
        if hasattr(self.master, 'block_license'):
            self.master.block_license(license_copy)