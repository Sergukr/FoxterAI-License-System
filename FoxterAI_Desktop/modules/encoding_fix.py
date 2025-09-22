"""
Модуль для исправления проблем с кодировкой
Особенно важно для кириллицы из MT4
"""

import chardet


class EncodingFixer:
    """Класс для исправления проблем с кодировкой текста"""
    
    # Список возможных кодировок для проверки
    ENCODINGS = [
        'utf-8',
        'cp1251',      # Windows кириллица
        'cp1252',      # Windows латиница
        'iso-8859-1',  # Latin-1
        'utf-16',
        'utf-32'
    ]
    
    @staticmethod
    def fix_text(text):
        """
        Исправить кодировку текста
        
        Args:
            text: Текст с возможными проблемами кодировки
            
        Returns:
            str: Исправленный текст
        """
        if not text:
            return ""
        
        # Если текст уже нормальный UTF-8
        if isinstance(text, str):
            try:
                text.encode('utf-8').decode('utf-8')
                # Проверяем на мусорные символы
                if not any(c in text for c in ['�', 'Ð', 'Ã']):
                    return text
            except:
                pass
        
        # Пробуем автоопределение кодировки
        if isinstance(text, bytes):
            detected = chardet.detect(text)
            if detected['encoding']:
                try:
                    return text.decode(detected['encoding'])
                except:
                    pass
        
        # Пробуем разные комбинации декодирования
        original = text
        
        # Если это строка с мусорными символами
        if isinstance(text, str):
            # Частые случаи двойного кодирования
            try:
                # UTF-8 -> Latin-1 -> UTF-8 (частая ошибка)
                fixed = text.encode('latin-1').decode('utf-8')
                if '�' not in fixed:
                    return fixed
            except:
                pass
            
            try:
                # CP1251 -> Latin-1 -> UTF-8
                fixed = text.encode('latin-1').decode('cp1251')
                if '�' not in fixed:
                    return fixed
            except:
                pass
            
            try:
                # Обратное преобразование
                fixed = text.encode('utf-8').decode('cp1251')
                if '�' not in fixed:
                    return fixed
            except:
                pass
        
        # Если это байты, пробуем все кодировки
        if isinstance(text, bytes):
            for encoding in EncodingFixer.ENCODINGS:
                try:
                    decoded = text.decode(encoding)
                    if '�' not in decoded:
                        return decoded
                except:
                    continue
        
        # Если ничего не помогло, возвращаем как есть
        # но заменяем мусорные символы
        if isinstance(text, str):
            return EncodingFixer.clean_garbage(text)
        
        return str(original)
    
    @staticmethod
    def clean_garbage(text):
        """
        Очистить текст от мусорных символов
        
        Args:
            text: Текст с мусорными символами
            
        Returns:
            str: Очищенный текст
        """
        if not text:
            return ""
        
        # Простая очистка - убираем непечатные символы
        cleaned = ''.join(char for char in text 
                         if char.isprintable() or char.isspace())
        
        # Если получилось полностью пустое, возвращаем хотя бы что-то
        if not cleaned.strip() and text:
            # Возвращаем только ASCII символы
            return ''.join(char for char in text if ord(char) < 128)
        
        return cleaned.strip()
    
    @staticmethod
    def fix_dict(data_dict):
        """
        Исправить кодировку во всех строковых значениях словаря
        
        Args:
            data_dict: Словарь с данными
            
        Returns:
            dict: Словарь с исправленной кодировкой
        """
        if not isinstance(data_dict, dict):
            return data_dict
        
        fixed = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                fixed[key] = EncodingFixer.fix_text(value)
            elif isinstance(value, bytes):
                fixed[key] = EncodingFixer.fix_text(value)
            elif isinstance(value, dict):
                fixed[key] = EncodingFixer.fix_dict(value)
            elif isinstance(value, list):
                fixed[key] = [EncodingFixer.fix_text(item) if isinstance(item, (str, bytes)) else item 
                             for item in value]
            else:
                fixed[key] = value
        
        return fixed
    
    @staticmethod
    def fix_dict_encoding(data_dict):
        """
        Исправить кодировку во всех строковых значениях словаря
        (Алиас для метода fix_dict для обратной совместимости)
        
        Args:
            data_dict: Словарь с данными
            
        Returns:
            dict: Словарь с исправленной кодировкой
        """
        return EncodingFixer.fix_dict(data_dict)
    
    @staticmethod
    def detect_encoding(text):
        """
        Определить кодировку текста
        
        Args:
            text: Текст или байты
            
        Returns:
            str: Название кодировки или None
        """
        if isinstance(text, str):
            text = text.encode()
        
        if isinstance(text, bytes):
            result = chardet.detect(text)
            return result.get('encoding', None)
        
        return None