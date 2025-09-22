"""
Пакет диалоговых окон FoxterAI License Manager
"""

from .base_dialog import CustomDialog, ConfirmDialog, InputDialog
from .create_dialog import CreateLicenseDialog
from .edit_dialog import EditLicenseDialog
from .extend_dialog import ExtendLicenseDialog
from .details_dialog import LicenseDetailsDialog

__all__ = [
    'CustomDialog',
    'ConfirmDialog', 
    'InputDialog',
    'CreateLicenseDialog',
    'EditLicenseDialog',
    'ExtendLicenseDialog',
    'LicenseDetailsDialog'
]