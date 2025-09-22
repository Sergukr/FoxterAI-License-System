"""
FoxterAI License Manager - Главный класс приложения
Версия 2.2 - Модульная архитектура с премиум дизайном
"""

import customtkinter as ctk
from typing import List, Dict
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорт конфигурации и сервисов
from app.config import ConfigManager
from core.services.license_service import LicenseService
from core.models.license import License
from core.models.stats import Statistics

# Импорт миксинов
from app.mixins.connection_mixin import ConnectionMixin
from app.mixins.license_mixin import LicenseMixin
from app.mixins.ui_mixin import UIMixin

# Импорт диалогов
from app.dialogs.create_dialog import CreateLicenseDialog
from app.dialogs.edit_dialog import EditLicenseDialog
from app.dialogs.extend_dialog import ExtendLicenseDialog
from app.dialogs.details_dialog import LicenseDetailsDialog


def get_config():
    """Получить конфигурацию приложения"""
    return ConfigManager()


class Application(ctk.CTk, ConnectionMixin, LicenseMixin, UIMixin):
    """
    Главный класс приложения с премиум дизайном
    Использует миксины для разделения логики
    """
    
    def __init__(self):
        """Инициализация приложения"""
        super().__init__()
        
        # Конфигурация
        self.config = get_config()
        
        # Сервисный слой
        self.license_service = LicenseService()
        self._setup_service_callbacks()
        
        # Данные
        self.licenses: List[License] = []
        self.filtered_licenses: List[License] = []
        self.statistics = Statistics()
        
        # Компоненты UI (будут созданы в _build_ui)
        self.header = None
        self.stats_panel = None
        self.control_panel = None
        self.license_table = None
        self.status_bar = None
        
        # Состояние
        self.is_loading = False
        
        # Настройка окна
        self._setup_window()
        
        # Создание интерфейса
        self._build_ui()
        
        # Автоподключение при запуске
        self.after(500, self.connect_to_server)
    
    # ==================== МЕТОДЫ ДИАЛОГОВ ====================
    
    def create_license_dialog(self):
        """Открыть диалог создания лицензии"""
        dialog = CreateLicenseDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            self.create_license(dialog.result)
    
    def edit_license_dialog(self, license):
        """Открыть диалог редактирования лицензии"""
        dialog = EditLicenseDialog(self, license)
        self.wait_window(dialog)
        
        if dialog.result:
            key = license.get('license_key') if isinstance(license, dict) else license.license_key
            self.edit_license(key, dialog.result)
    
    def extend_license_dialog(self, license):
        """Открыть диалог продления лицензии"""
        dialog = ExtendLicenseDialog(self, license)
        self.wait_window(dialog)
        
        if dialog.result:
            self.extend_license(license, dialog.result)
    
    def show_license_details(self, license):
        """Показать детали лицензии"""
        dialog = LicenseDetailsDialog(self, license)
        self.wait_window(dialog)


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    app = Application()
    app.mainloop()