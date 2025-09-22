"""
Пакет миксинов для разделения логики приложения
"""

from .connection_mixin import ConnectionMixin
from .license_mixin import LicenseMixin
from .ui_mixin import UIMixin

__all__ = [
    'ConnectionMixin',
    'LicenseMixin',
    'UIMixin'
]