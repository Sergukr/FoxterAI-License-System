"""
API модули для FoxterAI License Manager
Разделение API на логические части
"""

from .base_client import BaseAPIClient
from .licenses_api import LicensesAPI
from .auth_api import AuthAPI

__all__ = [
    'BaseAPIClient',
    'LicensesAPI', 
    'AuthAPI'
]