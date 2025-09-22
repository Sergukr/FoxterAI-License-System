"""
FoxterAI License Manager v2.2
Точка входа в приложение
"""

import sys
import os
import traceback

# Исправляем кодировку для Windows
if sys.platform == 'win32':
    import locale
    if locale.getpreferredencoding().upper() != 'UTF-8':
        os.environ['PYTHONIOENCODING'] = 'utf-8'

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Проверка зависимостей
def check_requirements():
    """Проверка установленных зависимостей"""
    required_modules = {
        'customtkinter': 'customtkinter',
        'requests': 'requests',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'PIL': 'pillow'
    }
    
    missing_modules = []
    
    for module_name, pip_name in required_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(pip_name)
    
    if missing_modules:
        print("\n" + "="*50)
        print("❌ Отсутствуют необходимые модули:")
        print("="*50)
        for module in missing_modules:
            print(f"  • {module}")
        
        print("\n📦 Установите их командой:")
        print(f"  pip install {' '.join(missing_modules)}")
        print("="*50)
        return False
    
    return True

def main():
    """Главная функция запуска приложения"""
    try:
        # Проверяем зависимости
        if not check_requirements():
            input("\nНажмите Enter для выхода...")
            sys.exit(1)
        
        # Импортируем приложение
        from app.application import Application
        
        print("\n" + "="*50)
        print("🦊 FoxterAI License Manager v2.2")
        print("="*50)
        print("✓ Запуск приложения...")
        print("="*50 + "\n")
        
        # Создаем и запускаем приложение
        app = Application()
        
        # ИСПРАВЛЕНО: используем mainloop() вместо run()
        app.mainloop()
        
    except ImportError as e:
        print("\n" + "="*50)
        print(f"❌ Ошибка импорта: {e}")
        print("="*50)
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
        
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ Критическая ошибка: {e}")
        print("="*50)
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()