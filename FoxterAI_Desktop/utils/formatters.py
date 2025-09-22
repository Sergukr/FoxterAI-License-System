"""
Функции форматирования данных
"""

from datetime import datetime
from typing import Optional, Union


def format_money(amount: Union[int, float], currency: str = '$', 
                decimals: int = 0) -> str:
    """
    Форматировать денежную сумму
    
    Args:
        amount: Сумма
        currency: Символ валюты
        decimals: Количество знаков после запятой
        
    Returns:
        str: Форматированная сумма
    """
    try:
        if decimals > 0:
            return f"{currency}{amount:,.{decimals}f}"
        else:
            return f"{currency}{amount:,.0f}"
    except:
        return f"{currency}0"


def format_date(date: Union[str, datetime, None], 
               format_str: str = '%d.%m.%Y') -> str:
    """
    Форматировать дату
    
    Args:
        date: Дата (строка ISO, datetime или None)
        format_str: Формат вывода
        
    Returns:
        str: Форматированная дата или 'Н/Д'
    """
    if not date:
        return 'Н/Д'
    
    try:
        if isinstance(date, str):
            # Парсим ISO формат
            if 'T' in date:
                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date, '%Y-%m-%d')
        elif isinstance(date, datetime):
            dt = date
        else:
            return 'Н/Д'
        
        return dt.strftime(format_str)
    except:
        if isinstance(date, str) and len(date) >= 10:
            return date[:10]
        return str(date) if date else 'Н/Д'


def format_datetime(date: Union[str, datetime, None],
                   format_str: str = '%d.%m.%Y %H:%M') -> str:
    """
    Форматировать дату и время
    
    Args:
        date: Дата и время
        format_str: Формат вывода
        
    Returns:
        str: Форматированные дата и время
    """
    return format_date(date, format_str)


def format_phone(phone: str) -> str:
    """
    Форматировать номер телефона
    
    Args:
        phone: Номер телефона
        
    Returns:
        str: Форматированный номер
    """
    if not phone:
        return ''
    
    # Оставляем только цифры
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Форматируем в зависимости от длины
    if len(digits) == 11 and digits.startswith('7'):
        # Российский формат
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    elif len(digits) == 10:
        # Без кода страны
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    elif len(digits) == 12 and digits.startswith('380'):
        # Украинский формат
        return f"+380 ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}"
    else:
        # Возвращаем как есть
        return phone


def format_bytes(bytes_count: int) -> str:
    """
    Форматировать размер в байтах
    
    Args:
        bytes_count: Количество байт
        
    Returns:
        str: Форматированный размер
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_percent(value: float, decimals: int = 1) -> str:
    """
    Форматировать процент
    
    Args:
        value: Значение (0-100)
        decimals: Знаков после запятой
        
    Returns:
        str: Форматированный процент
    """
    try:
        if decimals > 0:
            return f"{value:.{decimals}f}%"
        else:
            return f"{value:.0f}%"
    except:
        return "0%"


def format_days(days: int) -> str:
    """
    Форматировать количество дней
    
    Args:
        days: Количество дней
        
    Returns:
        str: Форматированная строка
    """
    if days < 0:
        return 'Н/Д'
    elif days == 0:
        return 'Сегодня'
    elif days == 1:
        return '1 день'
    elif days < 5:
        return f'{days} дня'
    else:
        return f'{days} дней'


def format_license_key(key: str) -> str:
    """
    Форматировать лицензионный ключ
    
    Args:
        key: Ключ лицензии
        
    Returns:
        str: Форматированный ключ
    """
    if not key or len(key) < 19:
        return key
    
    # FXAI-2024-XXXX-XXXX
    parts = key.split('-')
    if len(parts) == 4:
        return '-'.join(parts).upper()
    
    return key.upper()


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Обрезать текст до максимальной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
        
    Returns:
        str: Обрезанный текст
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix