"""
Миксин для управления подключением к серверу
ПОЛНЫЙ ФАЙЛ: FoxterAI_Desktop/app/mixins/connection_mixin.py
ИСПРАВЛЕНО: update_licenses заменен на load_licenses
"""

import threading
from typing import List, Dict


class ConnectionMixin:
    """Методы для управления подключением к серверу лицензий"""
    
    def connect_to_server(self):
        """Подключение к серверу лицензий"""
        print("🔄 Попытка подключения к серверу...")
        
        # Проверяем наличие сервиса
        if not hasattr(self, 'license_service'):
            print("❌ Сервис лицензий не инициализирован!")
            self.set_status("❌ Ошибка: сервис не готов", "error")
            return
        
        # Устанавливаем статус
        self.set_status("⏳ Подключение к серверу...", "loading")
        
        # Отключаем кнопки на время подключения
        if hasattr(self, '_enable_controls'):
            self._enable_controls(False)
        
        # Запускаем подключение в отдельном потоке
        thread = threading.Thread(target=self._connect_thread)
        thread.daemon = True
        thread.start()
    
    def _connect_thread(self):
        """Поток подключения к серверу"""
        try:
            # Пытаемся подключиться
            result = self.license_service.connect()
            
            # Передаем результат в главный поток
            self.after(0, self._handle_connection_result, result)
            
        except Exception as e:
            print(f"❌ Ошибка при подключении: {e}")
            self.after(0, self._handle_connection_error, str(e))
    
    def _handle_connection_result(self, success: bool):
        """Обработка результата подключения"""
        if success:
            print("✅ Подключение успешно!")
            self.set_status("✅ Подключен к серверу", "success")
            
            # Включаем элементы управления
            if hasattr(self, '_enable_controls'):
                self._enable_controls(True)
            
            # Обновляем индикатор в заголовке
            if hasattr(self, 'header') and self.header:
                self.header.set_connection_status(True)
            
            # Автоматически загружаем лицензии после подключения
            if hasattr(self, 'load_licenses'):
                self.load_licenses()
        else:
            self._handle_connection_error("Не удалось подключиться к серверу")
    
    def _handle_connection_error(self, error: str):
        """Обработка ошибки подключения"""
        print(f"❌ Ошибка подключения: {error}")
        self.set_status(f"❌ Ошибка: {error}", "error")
        
        # Оставляем кнопки отключенными
        if hasattr(self, '_enable_controls'):
            self._enable_controls(False)
        
        # Обновляем индикатор
        if hasattr(self, 'header') and self.header:
            self.header.set_connection_status(False)
        
        # Показываем уведомление
        self.show_notification(
            "Ошибка подключения",
            "Не удалось подключиться к серверу лицензий.\nПроверьте настройки в config.ini",
            "error"
        )
    
    def _on_service_connected(self):
        """Callback при успешном подключении сервиса"""
        print("✅ Сервис подключен!")
        self.after(0, lambda: self._handle_connection_result(True))
    
    def _on_service_disconnected(self):
        """Callback при отключении сервиса"""
        print("⚠️ Сервис отключен")
        self.after(0, lambda: self.set_status("⚠️ Отключен от сервера", "warning"))
        
        # Обновляем индикатор
        if hasattr(self, 'header') and self.header:
            self.header.set_connection_status(False)
    
    def _on_licenses_loaded(self, licenses: List[Dict]):
        """Callback при загрузке лицензий от сервиса"""
        print(f"📦 Получено лицензий от сервиса: {len(licenses) if licenses else 0}")
        
        # Сохраняем лицензии
        self.licenses = licenses if licenses else []
        self.filtered_licenses = self.licenses.copy()
        
        # Обновляем таблицу - ИСПРАВЛЕНО: используем load_licenses вместо update_licenses
        if hasattr(self, 'license_table') and self.license_table:
            self.license_table.load_licenses(self.filtered_licenses)
        
        # Обновляем статистику
        if hasattr(self, 'update_statistics'):
            self.update_statistics()
        
        # Обновляем счетчик в UI
        if hasattr(self, '_update_license_count'):
            self._update_license_count()
        
        # Статус
        count = len(self.licenses)
        if count > 0:
            self.set_status(f"✅ Загружено {count} лицензий", "success")
        else:
            self.set_status("ℹ️ Нет лицензий", "info")
    
    def _on_service_error(self, error: str):
        """Callback при ошибке в сервисе"""
        print(f"❌ Ошибка сервиса: {error}")
        self.after(0, lambda: self.set_status(f"❌ Ошибка: {error}", "error"))
    
    def _setup_service_callbacks(self):
        """Настройка callback функций для сервиса"""
        if hasattr(self.license_service, 'set_callbacks'):
            self.license_service.set_callbacks(
                on_connected=self._on_service_connected,
                on_disconnected=self._on_service_disconnected,
                on_licenses_loaded=self._on_licenses_loaded,
                on_error=self._on_service_error
            )
        
        # Альтернативный способ установки callbacks
        self.license_service.on_connected = self._on_service_connected
        self.license_service.on_disconnected = self._on_service_disconnected
        self.license_service.on_licenses_loaded = self._on_licenses_loaded
        self.license_service.on_error = self._on_service_error
    
    def _enable_controls(self, enabled: bool):
        """Включить/выключить элементы управления"""
        state = 'normal' if enabled else 'disabled'
        
        controls = ['refresh_btn', 'create_btn', 'export_btn']
        for control_name in controls:
            if hasattr(self, control_name):
                control = getattr(self, control_name)
                if hasattr(control, 'configure'):
                    try:
                        control.configure(state=state)
                    except:
                        pass
    
    def reconnect(self):
        """Переподключиться к серверу"""
        print("🔄 Переподключение к серверу...")
        self.connect_to_server()
    
    def disconnect(self):
        """Отключиться от сервера"""
        if hasattr(self, 'license_service'):
            self.license_service.disconnect()
            
        # Обновляем UI
        if hasattr(self, 'header') and self.header:
            self.header.set_connection_status(False)
        
        self.set_status("⚠️ Отключен от сервера", "warning")
        
        # Отключаем элементы управления
        if hasattr(self, '_enable_controls'):
            self._enable_controls(False)