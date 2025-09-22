// =====================
// FoxterAI_Server/config/config.js
// Централизованная конфигурация
// ИСПРАВЛЕНО: Убрана проверка переменных окружения для API_KEY
// =====================

module.exports = {
    // Сервер
    PORT: process.env.PORT || 3000,
    NODE_ENV: process.env.NODE_ENV || 'production',
    
    // API - ФИКСИРОВАННЫЙ КЛЮЧ БЕЗ ПРОВЕРКИ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
    API_KEY: 'FXA-Kj8$mN2@pQ9#vX5!wY3&zL7*',
    
    // База данных
    DATABASE: {
        filename: process.env.DB_PATH || './licenses.db',
        mode: process.env.DB_MODE || 'OPEN_READWRITE | OPEN_CREATE'
    },
    
    // Интервалы
    CHECK_INTERVAL_HOURS: parseInt(process.env.CHECK_INTERVAL_HOURS) || 12,
    AUTONOMY_HOURS: parseInt(process.env.AUTONOMY_HOURS) || 48,
    
    // Логирование
    LOG_LEVEL: process.env.LOG_LEVEL || 'info',
    LOG_DIR: process.env.LOG_DIR || './logs',
    
    // Безопасность
    RATE_LIMIT: {
        windowMs: 15 * 60 * 1000, // 15 минут
        max: 100 // максимум запросов
    }
};