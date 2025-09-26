//+------------------------------------------------------------------+
//|                                          15_storage_manager.mqh  |
//|                   Модуль локального хранения FoxterAI v2.0      |
//|                         БЕЗ GlobalVariables и FILE_COMMON       |
//+------------------------------------------------------------------+

//--- Константы для путей
#define STORAGE_ROOT_DIR     "FoxterAI"
#define SETTINGS_FILE        "settings.dat"
#define STATE_FILE          "state.dat"
#define LICENSE_FILE        "license.key"

//--- Флаги состояния
bool g_IsCleanShutdown = false;        // Флаг чистого закрытия
datetime g_LastStateSave = 0;          // Время последнего сохранения состояния
bool g_WasCrashRecovery = false;       // Флаг восстановления после сбоя
string g_StorageAccountDir = "";       // Путь к папке аккаунта
string g_StorageSymbolDir = "";        // Путь к папке символа

//+------------------------------------------------------------------+
//| ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ХРАНЕНИЯ                                  |
//+------------------------------------------------------------------+
void InitializeStorage() {
    // В тестере используем упрощенную систему
    if(IsTesting() || IsOptimization()) {
        Print("📁 Система хранения v2.0: режим тестера");
        return;
    }
    
    Print("========================================");
    Print("📁 ИНИЦИАЛИЗАЦИЯ ЛОКАЛЬНОГО ХРАНЕНИЯ v2.0");
    Print("========================================");
    
    // Создаем структуру папок: FoxterAI/[AccountNumber]/[Symbol]/
    g_StorageAccountDir = STORAGE_ROOT_DIR + "/" + IntegerToString(AccountNumber());
    g_StorageSymbolDir = g_StorageAccountDir + "/" + Symbol();
    
    // Проверяем и создаем папки если нужно
    CreateDirectoryStructure();
    
    Print("📂 Папка аккаунта: ", g_StorageAccountDir);
    Print("📂 Папка символа: ", g_StorageSymbolDir);
    
    // Проверяем наличие файла состояния для определения сбоя
    CheckCrashRecovery();
    
    Print("========================================");
}

//+------------------------------------------------------------------+
//| СОЗДАНИЕ СТРУКТУРЫ ДИРЕКТОРИЙ                                   |
//+------------------------------------------------------------------+
void CreateDirectoryStructure() {
    // Проверяем и создаем корневую папку
    if(!FolderCreate(STORAGE_ROOT_DIR)) {
        // Папка уже существует или ошибка создания
        if(!FileIsExist(STORAGE_ROOT_DIR)) {
            Print("⚠️ Не удалось создать папку: ", STORAGE_ROOT_DIR);
        }
    }
    
    // Проверяем и создаем папку аккаунта
    if(!FolderCreate(g_StorageAccountDir)) {
        if(!FileIsExist(g_StorageAccountDir)) {
            Print("⚠️ Не удалось создать папку аккаунта: ", g_StorageAccountDir);
        }
    }
    
    // Проверяем и создаем папку символа
    if(!FolderCreate(g_StorageSymbolDir)) {
        if(!FileIsExist(g_StorageSymbolDir)) {
            Print("⚠️ Не удалось создать папку символа: ", g_StorageSymbolDir);
        }
    }
}

//+------------------------------------------------------------------+
//| ПРОВЕРКА НА АВАРИЙНОЕ ЗАВЕРШЕНИЕ                               |
//+------------------------------------------------------------------+
void CheckCrashRecovery() {
    string stateFile = g_StorageSymbolDir + "/" + STATE_FILE;
    
    if(FileIsExist(stateFile)) {
        // Читаем файл состояния
        int handle = FileOpen(stateFile, FILE_READ | FILE_TXT);
        if(handle != INVALID_HANDLE) {
            string lastState = FileReadString(handle);
            FileClose(handle);
            
            // Если файл существует и не содержит флаг чистого закрытия
            if(StringFind(lastState, "CLEAN_SHUTDOWN") < 0) {
                g_WasCrashRecovery = true;
                Print("⚠️ ОБНАРУЖЕНО АВАРИЙНОЕ ЗАВЕРШЕНИЕ!");
                Print("📁 Восстановление настроек после сбоя...");
                
                // Показываем уведомление пользователю
                Alert("FoxterAI v2.0\n\nОбнаружено аварийное завершение!\nНастройки восстановлены из локального хранилища.");
            }
        }
    }
    
    // Создаем новый файл состояния
    SaveRobotState();
}

//+------------------------------------------------------------------+
//| СОХРАНИТЬ ЛИЦЕНЗИОННЫЙ КЛЮЧ ЛОКАЛЬНО                           |
//+------------------------------------------------------------------+
void SaveLicenseKeyLocal(string key) {
    if(IsTesting() || IsOptimization()) return;
    
    string licenseFile = g_StorageAccountDir + "/" + LICENSE_FILE;
    
    int handle = FileOpen(licenseFile, FILE_WRITE | FILE_TXT);
    if(handle != INVALID_HANDLE) {
        FileWriteString(handle, key);
        FileClose(handle);
        Print("✅ Лицензия сохранена локально: ", licenseFile);
    } else {
        Print("❌ Ошибка сохранения лицензии!");
    }
}

//+------------------------------------------------------------------+
//| ПОЛУЧИТЬ ЛИЦЕНЗИОННЫЙ КЛЮЧ ИЗ ЛОКАЛЬНОГО ХРАНИЛИЩА            |
//+------------------------------------------------------------------+
string GetLicenseKeyLocal() {
    if(IsTesting() || IsOptimization()) {
        return "UNIV-TEST-MODE-KEY";
    }
    
    string licenseFile = g_StorageAccountDir + "/" + LICENSE_FILE;
    
    // Проверяем существование файла
    if(!FileIsExist(licenseFile)) {
        Print("❌ Локальный файл лицензии не найден");
        return "";
    }
    
    // Читаем ключ
    int handle = FileOpen(licenseFile, FILE_READ | FILE_TXT);
    if(handle != INVALID_HANDLE) {
        string key = FileReadString(handle);
        FileClose(handle);
        
        // Очищаем ключ от лишних символов
        string cleanKey = "";
        for(int i = 0; i < StringLen(key); i++) {
            ushort charCode = StringGetCharacter(key, i);
            if(charCode > 32 && charCode < 127) {
                cleanKey = cleanKey + CharToString((uchar)charCode);
            }
        }
        
        if(StringLen(cleanKey) >= 10 && StringSubstr(cleanKey, 0, 5) == "UNIV-") {
            Print("✅ Лицензия загружена из локального хранилища");
            return cleanKey;
        }
    }
    
    return "";
}

//+------------------------------------------------------------------+
//| СОХРАНИТЬ НАСТРОЙКИ ПАНЕЛИ                                     |
//+------------------------------------------------------------------+
void SavePanelSettings() {
    // В тестере используем память
    if(IsTesting() || IsOptimization()) {
        return;
    }
    
    string settingsFile = g_StorageSymbolDir + "/" + SETTINGS_FILE;
    
    int handle = FileOpen(settingsFile, FILE_WRITE | FILE_BIN);
    if(handle != INVALID_HANDLE) {
        // Сохраняем версию формата
        FileWriteInteger(handle, 200); // версия 2.0.0
        
        // Сохраняем настройки
        FileWriteInteger(handle, g_BotEnabled ? 1 : 0);
        FileWriteInteger(handle, g_TradeDirection);
        FileWriteInteger(handle, g_MaxOrdersBuy);
        FileWriteInteger(handle, g_MaxOrdersSell);
        FileWriteDouble(handle, g_BasketProfitPercent);
        FileWriteInteger(handle, g_BasketType);
        FileWriteInteger(handle, g_BasketAfterN);
        
        // Сохраняем позицию панели
        FileWriteInteger(handle, g_PanelPosX);
        FileWriteInteger(handle, g_PanelPosY);
        
        // Временная метка
        FileWriteLong(handle, TimeCurrent());
        
        FileClose(handle);
        Print("💾 Настройки сохранены локально для ", Symbol());
    }
}

//+------------------------------------------------------------------+
//| ЗАГРУЗИТЬ НАСТРОЙКИ ПАНЕЛИ                                     |
//+------------------------------------------------------------------+
bool LoadPanelSettings() {
    // В тестере используем входные параметры
    if(IsTesting() || IsOptimization()) {
        Print("📁 Тестер: используются входные параметры");
        return false;
    }
    
    string settingsFile = g_StorageSymbolDir + "/" + SETTINGS_FILE;
    
    // Проверяем существование файла
    if(!FileIsExist(settingsFile)) {
        Print("📁 Файл настроек не найден, используются параметры по умолчанию");
        return false;
    }
    
    int handle = FileOpen(settingsFile, FILE_READ | FILE_BIN);
    if(handle != INVALID_HANDLE) {
        // Проверяем версию
        int version = FileReadInteger(handle);
        if(version != 200) {
            FileClose(handle);
            Print("⚠️ Неподдерживаемая версия настроек: ", version);
            return false;
        }
        
        // Загружаем настройки
        g_BotEnabled = FileReadInteger(handle) > 0;
        g_TradeDirection = (ENUM_TRADE_DIRECTION)FileReadInteger(handle);
        g_MaxOrdersBuy = FileReadInteger(handle);
        g_MaxOrdersSell = FileReadInteger(handle);
        g_BasketProfitPercent = FileReadDouble(handle);
        g_BasketType = (ENUM_BASKET_TYPE)FileReadInteger(handle);
        g_BasketAfterN = FileReadInteger(handle);
        
        // Загружаем позицию панели
        g_PanelPosX = FileReadInteger(handle);
        g_PanelPosY = FileReadInteger(handle);
        
        // Читаем временную метку
        datetime savedTime = (datetime)FileReadLong(handle);
        
        FileClose(handle);
        
        Print("✅ Настройки загружены для ", Symbol());
        Print("   Сохранены: ", TimeToString(savedTime));
        Print("   Робот: ", g_BotEnabled ? "ВКЛЮЧЕН" : "ВЫКЛЮЧЕН");
        Print("   Направление: ", g_TradeDirection);
        Print("   Позиция панели: X=", g_PanelPosX, " Y=", g_PanelPosY);
        
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| СОХРАНИТЬ СОСТОЯНИЕ РОБОТА                                     |
//+------------------------------------------------------------------+
void SaveRobotState() {
    if(IsTesting() || IsOptimization()) return;
    
    string stateFile = g_StorageSymbolDir + "/" + STATE_FILE;
    
    int handle = FileOpen(stateFile, FILE_WRITE | FILE_TXT);
    if(handle != INVALID_HANDLE) {
        // Сохраняем состояние
        string state = "";
        state = state + "VERSION=2.0.0\n";
        state = state + "TIME=" + TimeToString(TimeCurrent()) + "\n";
        state = state + "ACCOUNT=" + IntegerToString(AccountNumber()) + "\n";
        state = state + "SYMBOL=" + Symbol() + "\n";
        state = state + "MAGIC=" + IntegerToString(MagicNumber) + "\n";
        state = state + "BOT_ENABLED=" + (g_BotEnabled ? "YES" : "NO") + "\n";
        state = state + "CLEAN_SHUTDOWN=" + (g_IsCleanShutdown ? "YES" : "NO") + "\n";
        
        // Информация о сериях
        state = state + "BUY_SERIES_ACTIVE=" + (g_BuySeries.active ? "YES" : "NO") + "\n";
        state = state + "BUY_SERIES_COUNT=" + IntegerToString(g_BuySeries.count) + "\n";
        state = state + "SELL_SERIES_ACTIVE=" + (g_SellSeries.active ? "YES" : "NO") + "\n";
        state = state + "SELL_SERIES_COUNT=" + IntegerToString(g_SellSeries.count) + "\n";
        
        FileWriteString(handle, state);
        FileClose(handle);
        
        g_LastStateSave = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| ЗАГРУЗИТЬ СОСТОЯНИЕ РОБОТА                                     |
//+------------------------------------------------------------------+
bool LoadRobotState() {
    if(IsTesting() || IsOptimization()) return false;
    
    string stateFile = g_StorageSymbolDir + "/" + STATE_FILE;
    
    if(!FileIsExist(stateFile)) {
        return false;
    }
    
    int handle = FileOpen(stateFile, FILE_READ | FILE_TXT);
    if(handle != INVALID_HANDLE) {
        string content = "";
        while(!FileIsEnding(handle)) {
            content = content + FileReadString(handle) + "\n";
        }
        FileClose(handle);
        
        // Парсим состояние
        if(StringFind(content, "VERSION=2.0") >= 0) {
            Print("📁 Состояние робота загружено");
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| ЧИСТОЕ ЗАКРЫТИЕ РОБОТА                                         |
//+------------------------------------------------------------------+
void CleanShutdownRobot() {
    Print("========================================");
    Print("🔴 ЧИСТОЕ ЗАКРЫТИЕ РОБОТА");
    Print("========================================");
    
    // Устанавливаем флаг чистого закрытия
    g_IsCleanShutdown = true;
    
    // Сохраняем финальное состояние
    SaveRobotState();
    
    // Удаляем настройки для текущей пары
    string settingsFile = g_StorageSymbolDir + "/" + SETTINGS_FILE;
    if(FileIsExist(settingsFile)) {
        FileDelete(settingsFile);
        Print("🗑️ Настройки для ", Symbol(), " удалены");
    }
    
    // Удаляем файл состояния
    string stateFile = g_StorageSymbolDir + "/" + STATE_FILE;
    if(FileIsExist(stateFile)) {
        FileDelete(stateFile);
        Print("🗑️ Файл состояния удален");
    }
    
    Print("✅ Следующий запуск будет с настройками по умолчанию");
    Print("========================================");
    
    // Закрываем все ордера если есть
    if(g_BuySeries.active || g_SellSeries.active) {
        Print("⚠️ Закрываем все открытые позиции...");
        CloseAllOrders();
    }
    
    // Удаляем панель
    DeletePanel();
    
    // Завершаем работу эксперта
    ExpertRemove();
}

//+------------------------------------------------------------------+
//| ПРОВЕРКА СУЩЕСТВОВАНИЯ ФАЙЛА В ЛОКАЛЬНОЙ ПАПКЕ                 |
//+------------------------------------------------------------------+
bool FileIsExistLocal(string filepath) {
    // Пытаемся открыть файл для чтения
    int handle = FileOpen(filepath, FILE_READ);
    if(handle != INVALID_HANDLE) {
        FileClose(handle);
        return true;
    }
    return false;
}

//+------------------------------------------------------------------+
//| ПЕРИОДИЧЕСКОЕ СОХРАНЕНИЕ СОСТОЯНИЯ                             |
//+------------------------------------------------------------------+
void PeriodicStateSave() {
    if(IsTesting() || IsOptimization()) return;
    
    // Сохраняем каждые 5 минут
    if(TimeCurrent() - g_LastStateSave > 300) {
        SaveRobotState();
        SavePanelSettings();
    }
}

//+------------------------------------------------------------------+
//| МИГРАЦИЯ СТАРЫХ ДАННЫХ - НЕ ИСПОЛЬЗУЕТСЯ!                      |
//+------------------------------------------------------------------+
// НЕ делаем миграцию согласно ТЗ - начинаем с чистого листа!