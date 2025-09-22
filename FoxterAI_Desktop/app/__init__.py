"""
FoxterAI License Manager Application Package
Версия 2.2 - Модульная архитектура
"""

__version__ = "2.2.0"
__author__ = "FoxterX"
__description__ = "Система управления лицензиями FoxterAI"

# Экспортируем основные классы
from .application import Application
from .config import ConfigManager

__all__ = [
    'Application',
    'ConfigManager',
    '__version__',
    '__author__',
    '__description__'
]