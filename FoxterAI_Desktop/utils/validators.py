"""
Функции валидации данных
"""

import re
from typing import Tuple, Optional


def validate_license_key(key: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать лицензионный ключ
    
    Args:
        key: Ключ лицензии
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not key:
        return False, "Ключ не может быть пустым"
    
    # Убираем пробелы
    key = key.strip().upper()
    
    # Проверяем формат FXAI-YYYY-XXXX-XXXX
    pattern = r'^FXAI-\d{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    
    if not re.match(pattern, key):
        return False, "Неверный формат ключа. Ожидается: FXAI-2024-XXXX-XXXX"
    
    # Проверяем год
    year_part = key.split('-')[1]
    try:
        year = int(year_part)
        if year < 2024 or year > 2030:
            return False, f"Неверный год в ключе: {year}"
    except ValueError:
        return False, "Год должен быть числом"
    
    return True, None


def validate_phone(phone: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Валидировать номер телефона
    
    Args:
        phone: Номер телефона
        required: Обязательное поле
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not phone:
        if required:
            return False, "Номер телефона обязателен"
        return True, None  # Пустой допустим если не обязательный
    
    # Оставляем только цифры и +
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Проверяем длину (минимум 10 цифр)
    digits = ''.join(c for c in clean if c.isdigit())
    
    if len(digits) < 10:
        return False, "Номер должен содержать минимум 10 цифр"
    
    if len(digits) > 15:
        return False, "Слишком длинный номер телефона"
    
    # Проверяем формат
    if clean.startswith('+'):
        if len(digits) < 11:
            return False, "Международный номер должен содержать код страны"
    
    return True, None


def validate_telegram(telegram: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Валидировать Telegram username
    
    Args:
        telegram: Username в Telegram
        required: Обязательное поле
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not telegram:
        if required:
            return False, "Telegram username обязателен"
        return True, None
    
    # Убираем @ если есть
    if telegram.startswith('@'):
        telegram = telegram[1:]
    
    # Проверяем длину
    if len(telegram) < 3:
        return False, "Username слишком короткий (минимум 3 символа)"
    
    if len(telegram) > 32:
        return False, "Username слишком длинный (максимум 32 символа)"
    
    # Проверяем символы (только латиница, цифры и подчеркивание)
    if not re.match(r'^[a-zA-Z0-9_]+$', telegram):
        return False, "Username может содержать только латиницу, цифры и _"
    
    # Не может начинаться с цифры
    if telegram[0].isdigit():
        return False, "Username не может начинаться с цифры"
    
    return True, None


def validate_email(email: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Валидировать email адрес
    
    Args:
        email: Email адрес
        required: Обязательное поле
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not email:
        if required:
            return False, "Email обязателен"
        return True, None
    
    # Простая проверка формата
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Неверный формат email"
    
    # Проверяем длину
    if len(email) > 254:
        return False, "Email слишком длинный"
    
    # Проверяем части
    local, domain = email.rsplit('@', 1)
    
    if len(local) > 64:
        return False, "Локальная часть email слишком длинная"
    
    if '..' in email:
        return False, "Email не может содержать две точки подряд"
    
    return True, None


def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать API ключ
    
    Args:
        api_key: API ключ
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not api_key:
        return False, "API ключ не может быть пустым"
    
    # Убираем пробелы
    api_key = api_key.strip()
    
    # Проверяем длину
    if len(api_key) < 20:
        return False, "API ключ слишком короткий"
    
    if len(api_key) > 100:
        return False, "API ключ слишком длинный"
    
    # Проверяем символы (буквы, цифры и спец.символы)
    if not re.match(r'^[a-zA-Z0-9\-_@#$%&*!]+$', api_key):
        return False, "API ключ содержит недопустимые символы"
    
    return True, None


def validate_months(months: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать количество месяцев
    
    Args:
        months: Количество месяцев (строка)
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not months:
        return False, "Количество месяцев обязательно"
    
    try:
        months_int = int(months)
        
        if months_int < 1:
            return False, "Минимальный срок - 1 месяц"
        
        if months_int > 999:
            return False, "Максимальный срок - 999 месяцев"
        
        return True, None
        
    except ValueError:
        return False, "Количество месяцев должно быть числом"


def validate_account_number(account: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Валидировать номер торгового счёта
    
    Args:
        account: Номер счёта
        required: Обязательное поле
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not account:
        if required:
            return False, "Номер счёта обязателен"
        return True, None
    
    # Проверяем что это число
    try:
        account_int = int(account)
        
        if account_int < 1:
            return False, "Номер счёта должен быть положительным"
        
        if account_int > 999999999:
            return False, "Слишком большой номер счёта"
        
        return True, None
        
    except ValueError:
        return False, "Номер счёта должен быть числом"


def validate_balance(balance: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать баланс
    
    Args:
        balance: Баланс (строка)
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not balance:
        return True, None  # Пустой баланс допустим (0)
    
    try:
        balance_float = float(balance)
        
        if balance_float < 0:
            return False, "Баланс не может быть отрицательным"
        
        if balance_float > 999999999:
            return False, "Слишком большой баланс"
        
        return True, None
        
    except ValueError:
        return False, "Баланс должен быть числом"


def validate_client_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать имя клиента
    
    Args:
        name: Имя клиента
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not name:
        return False, "Имя клиента обязательно"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Имя слишком короткое (минимум 2 символа)"
    
    if len(name) > 100:
        return False, "Имя слишком длинное (максимум 100 символов)"
    
    # Проверяем на недопустимые символы
    if re.search(r'[<>\"\'%;()&+]', name):
        return False, "Имя содержит недопустимые символы"
    
    return True, None


def validate_notes(notes: str) -> Tuple[bool, Optional[str]]:
    """
    Валидировать заметки
    
    Args:
        notes: Текст заметок
        
    Returns:
        Tuple[bool, str]: (валидный, сообщение об ошибке)
    """
    if not notes:
        return True, None  # Пустые заметки допустимы
    
    if len(notes) > 500:
        return False, "Заметки слишком длинные (максимум 500 символов)"
    
    # Проверяем на опасные символы
    if re.search(r'[<>\"\'%]', notes):
        return False, "Заметки содержат недопустимые символы"
    
    return True, None