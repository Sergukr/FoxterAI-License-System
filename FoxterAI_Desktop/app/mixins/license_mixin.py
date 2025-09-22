"""
Миксин для работы с лицензиями
ПОЛНЫЙ ФАЙЛ: FoxterAI_Desktop/app/mixins/license_mixin.py
ИСПРАВЛЕНО: update_licenses заменен на load_licenses
"""

import threading
from tkinter import filedialog, messagebox
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import customtkinter as ctk


class LicenseMixin:
    """Методы для работы с лицензиями"""
    
    def load_licenses(self):
        """Загрузка лицензий с сервера"""
        print("🔄 Начинаем загрузку лицензий...")
        
        # Проверяем подключение
        if not hasattr(self, 'license_service'):
            print("❌ Сервис лицензий не инициализирован!")
            self.set_status("❌ Ошибка: сервис не готов", "error")
            return
        
        # Проверяем состояние подключения
        if not self.license_service.is_connected:
            print("⚠️ Нет подключения к серверу, пытаемся подключиться...")
            self.connect_to_server()
            # После подключения load_licenses будет вызван автоматически
            return
        
        self.set_status("⏳ Загрузка лицензий...", "loading")
        self.show_loading(True)
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._load_licenses_thread)
        thread.daemon = True
        thread.start()
    
    def _load_licenses_thread(self):
        """Поток загрузки лицензий"""
        try:
            print("📡 Запрос лицензий с сервера...")
            
            # Получаем лицензии через сервис
            licenses = self.license_service.get_licenses()
            
            print(f"✅ Получено лицензий: {len(licenses) if licenses else 0}")
            
            # Передаем результат в главный поток
            self.after(0, self._handle_licenses_loaded, licenses)
            
        except Exception as e:
            print(f"❌ Ошибка загрузки лицензий: {e}")
            self.after(0, self._handle_licenses_error, str(e))
    
    def _handle_licenses_loaded(self, licenses: List[Dict]):
        """Обработка загруженных лицензий"""
        print(f"🔄 Обработка {len(licenses) if licenses else 0} лицензий...")
        
        self.show_loading(False)
        
        # Сохраняем лицензии
        if licenses is None:
            licenses = []
        
        self.licenses = licenses
        self.filtered_licenses = licenses.copy()
        
        # ИСПРАВЛЕНО: используем load_licenses вместо update_licenses
        if hasattr(self, 'license_table') and self.license_table:
            print("📊 Обновляем таблицу лицензий...")
            self.license_table.load_licenses(self.licenses)
        
        # Вычисляем и обновляем статистику
        self._update_statistics_from_licenses()
        
        # Обновляем счетчик
        if hasattr(self, '_update_license_count'):
            self._update_license_count()
        
        # Статус
        count = len(self.licenses)
        if count > 0:
            self.set_status(f"✅ Загружено {count} лицензий", "success")
        else:
            self.set_status("ℹ️ Нет лицензий", "info")
    
    def _handle_licenses_error(self, error: str):
        """Обработка ошибки загрузки"""
        self.show_loading(False)
        self.set_status(f"❌ Ошибка загрузки: {error}", "error")
        
        self.show_notification(
            "Ошибка загрузки",
            f"Не удалось загрузить лицензии:\n{error}",
            "error"
        )
    
    def _update_statistics_from_licenses(self):
        """Обновить статистику на основе загруженных лицензий"""
        if not self.licenses:
            stats = {'total': 0, 'active': 0, 'expired': 0, 'blocked': 0, 'inactive': 0, 'balance': 0}
        else:
            stats = {
                'total': len(self.licenses),
                'active': len([l for l in self.licenses if self._get_field(l, 'status') == 'active']),
                'expired': len([l for l in self.licenses if self._get_field(l, 'status') == 'expired']),
                'blocked': len([l for l in self.licenses if self._get_field(l, 'status') == 'blocked']),
                'inactive': len([l for l in self.licenses if self._get_field(l, 'status') == 'created']),
                'balance': sum([float(self._get_field(l, 'last_balance', 0)) for l in self.licenses 
                               if self._get_field(l, 'account_type') == 'Real'])
            }
        
        print(f"📊 Статистика: Всего={stats['total']}, Активных={stats['active']}, "
              f"Истекших={stats['expired']}, Заблокированных={stats['blocked']}, "
              f"Неактивных={stats['inactive']}, Баланс REAL=${stats['balance']:.2f}")
        
        # Обновляем UI
        if hasattr(self, 'update_statistics'):
            self.update_statistics(stats)
    
    def _get_field(self, obj, field_name, default=None):
        """Универсальное получение поля из объекта или словаря"""
        if hasattr(obj, field_name):
            return getattr(obj, field_name, default)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__.get(field_name, default)
        elif isinstance(obj, dict):
            return obj.get(field_name, default)
        return default
    
    def create_license(self, license_data: Dict):
        """Создание новой лицензии"""
        self.set_status("⏳ Создание лицензии...", "loading")
        
        def create_thread():
            try:
                # Добавляем флаг universal если его нет
                if 'universal' not in license_data:
                    license_data['universal'] = True
                    
                result = self.license_service.create_license(license_data)
                self.after(0, self._handle_create_result, result, license_data)
            except Exception as e:
                self.after(0, self._handle_create_error, str(e))
        
        thread = threading.Thread(target=create_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_create_result(self, result: Dict, license_data: Dict):
        """Обработка результата создания лицензии"""
        if result and result.get('success'):
            key = result.get('license_key', license_data.get('license_key', 'Unknown'))
            self.set_status(f"✅ Лицензия создана: {key}", "success")
            
            # Перезагружаем список
            self.load_licenses()
            
            # Уведомление
            self.show_notification(
                "Лицензия создана",
                f"Ключ: {key}\nКлиент: {license_data.get('client_name', '')}",
                "success"
            )
        else:
            error = result.get('error', 'Неизвестная ошибка') if result else 'Нет ответа от сервера'
            self._handle_create_error(error)
    
    def _handle_create_error(self, error: str):
        """Обработка ошибки создания"""
        self.set_status(f"❌ Ошибка создания: {error}", "error")
        self.show_notification(
            "Ошибка создания",
            f"Не удалось создать лицензию:\n{error}",
            "error"
        )
    
    def edit_license(self, license_key: str, updates: Dict):
        """Редактирование лицензии"""
        self.set_status(f"⏳ Обновление лицензии...", "loading")
        
        def edit_thread():
            try:
                success = self.license_service.update_license(license_key, updates)
                self.after(0, self._handle_edit_result, success, license_key)
            except Exception as e:
                self.after(0, self._handle_edit_error, license_key, str(e))
        
        thread = threading.Thread(target=edit_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_edit_result(self, success: bool, license_key: str):
        """Обработка результата редактирования"""
        if success:
            self.set_status(f"✅ Лицензия обновлена", "success")
            self.load_licenses()
            
            self.show_notification(
                "Лицензия обновлена",
                f"Ключ: {license_key[:12]}...",
                "success"
            )
        else:
            self._handle_edit_error(license_key, "Не удалось обновить")
    
    def _handle_edit_error(self, license_key: str, error: str):
        """Обработка ошибки редактирования"""
        self.set_status(f"❌ Ошибка обновления: {error}", "error")
        self.show_notification(
            "Ошибка обновления",
            f"Не удалось обновить лицензию {license_key[:12]}...:\n{error}",
            "error"
        )
    
    def delete_license(self, license):
        """Удаление лицензии"""
        # Получаем ключ
        key = self._get_field(license, 'license_key', 'Unknown')
        
        # Подтверждение
        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить лицензию?\n\nКлюч: {key[:12]}...\n\nЭто действие необратимо!"
        )
        
        if not result:
            return
        
        self.set_status("⏳ Удаление лицензии...", "loading")
        
        def delete_thread():
            try:
                success = self.license_service.delete_license(key)
                self.after(0, self._handle_delete_result, success, key)
            except Exception as e:
                self.after(0, self._handle_delete_error, key, str(e))
        
        thread = threading.Thread(target=delete_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_delete_result(self, success: bool, key: str):
        """Обработка результата удаления"""
        if success:
            self.set_status(f"✅ Лицензия удалена", "success")
            self.load_licenses()
            
            self.show_notification(
                "Лицензия удалена",
                f"Ключ: {key[:12]}...",
                "success"
            )
        else:
            self._handle_delete_error(key, "Не удалось удалить")
    
    def _handle_delete_error(self, key: str, error: str):
        """Обработка ошибки удаления"""
        self.set_status(f"❌ Ошибка удаления: {error}", "error")
        self.show_notification(
            "Ошибка удаления",
            f"Не удалось удалить лицензию {key[:12]}...:\n{error}",
            "error"
        )
    
    def extend_license(self, license, months: int):
        """Продление лицензии"""
        key = self._get_field(license, 'license_key', 'Unknown')
        self.set_status(f"⏳ Продление лицензии...", "loading")
        
        def extend_thread():
            try:
                success = self.license_service.extend_license(key, months)
                self.after(0, self._handle_extend_result, success, key, months)
            except Exception as e:
                self.after(0, self._handle_extend_error, key, str(e))
        
        thread = threading.Thread(target=extend_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_extend_result(self, success: bool, key: str, months: int):
        """Обработка результата продления"""
        if success:
            self.set_status(f"✅ Лицензия продлена", "success")
            self.load_licenses()
            
            self.show_notification(
                "Лицензия продлена",
                f"Ключ: {key[:12]}...\nПродлена на: {months} месяцев",
                "success"
            )
        else:
            self._handle_extend_error(key, "Не удалось продлить")
    
    def _handle_extend_error(self, key: str, error: str):
        """Обработка ошибки продления"""
        self.set_status(f"❌ Ошибка продления: {error}", "error")
        self.show_notification(
            "Ошибка продления",
            f"Не удалось продлить лицензию {key[:12]}...:\n{error}",
            "error"
        )
    
    def block_license(self, license):
        """Блокировка/разблокировка лицензии"""
        # Получаем данные
        key = self._get_field(license, 'license_key', 'Unknown')
        current_status = self._get_field(license, 'status', 'unknown')
        
        # Определяем действие
        is_blocked = current_status == 'blocked'
        action = 'разблокировать' if is_blocked else 'заблокировать'
        new_status = 'active' if is_blocked else 'blocked'
        
        # Подтверждение
        result = messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите {action} лицензию?\n\nКлюч: {key[:12]}...\n\n"
            f"{'Клиент сможет использовать робота' if is_blocked else 'Клиент НЕ сможет использовать робота'}!"
        )
        
        if not result:
            return
        
        self.set_status(f"⏳ Изменение статуса...", "loading")
        
        def block_thread():
            try:
                success = self.license_service.block_license(key, not is_blocked)
                self.after(0, self._handle_block_result, success, key, action)
            except Exception as e:
                self.after(0, self._handle_block_error, key, str(e))
        
        thread = threading.Thread(target=block_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_block_result(self, success: bool, key: str, action: str):
        """Обработка результата блокировки"""
        if success:
            self.set_status(f"✅ Лицензия {action}на", "success")
            self.load_licenses()
            
            self.show_notification(
                f"Лицензия {action}на",
                f"Ключ: {key[:12]}...",
                "success"
            )
        else:
            self._handle_block_error(key, f"Не удалось {action}")
    
    def _handle_block_error(self, key: str, error: str):
        """Обработка ошибки блокировки"""
        self.set_status(f"❌ Ошибка: {error}", "error")
        self.show_notification(
            "Ошибка изменения статуса",
            f"Не удалось изменить статус лицензии {key[:12]}...:\n{error}",
            "error"
        )
    
    def export_licenses(self):
        """Экспорт лицензий в файл"""
        if not self.licenses:
            messagebox.showwarning("Предупреждение", "Нет лицензий для экспорта")
            return
        
        # Выбор файла для сохранения
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel файлы", "*.xlsx"),
                ("CSV файлы", "*.csv"),
                ("Все файлы", "*.*")
            ],
            initialfile=f"licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not filename:
            return
        
        try:
            # Подготавливаем данные
            data = []
            for lic in self.licenses:
                data.append({
                    'Ключ лицензии': self._get_field(lic, 'license_key', ''),
                    'Клиент': self._get_field(lic, 'client_name', ''),
                    'Телефон': self._get_field(lic, 'client_contact', ''),
                    'Telegram': self._get_field(lic, 'client_telegram', ''),
                    'Владелец счета': self._get_field(lic, 'account_owner', ''),
                    'Номер счета': self._get_field(lic, 'account_number', ''),
                    'Брокер': self._get_field(lic, 'broker_name', ''),
                    'Робот': self._get_field(lic, 'robot_name', ''),
                    'Версия': self._get_field(lic, 'robot_version', ''),
                    'Баланс': self._get_field(lic, 'last_balance', 0),
                    'Тип счета': self._get_field(lic, 'account_type', ''),
                    'Статус': self._get_field(lic, 'status', ''),
                    'Создана': self._get_field(lic, 'created_date', ''),
                    'Активирована': self._get_field(lic, 'activation_date', ''),
                    'Истекает': self._get_field(lic, 'expiry_date', ''),
                    'Дней осталось': self._get_field(lic, 'days_left', ''),
                    'Заметки': self._get_field(lic, 'notes', '')
                })
            
            # Создаем DataFrame
            df = pd.DataFrame(data)
            
            # Сохраняем файл
            if filename.endswith('.csv'):
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            else:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Лицензии')
            
            self.set_status(f"✅ Экспортировано в {filename.split('/')[-1]}", "success")
            
            # Уведомление
            self.show_notification(
                "Экспорт завершен",
                f"Экспортировано {len(self.licenses)} лицензий",
                "success"
            )
            
        except Exception as e:
            self.set_status(f"❌ Ошибка экспорта: {str(e)}", "error")
            messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{str(e)}")