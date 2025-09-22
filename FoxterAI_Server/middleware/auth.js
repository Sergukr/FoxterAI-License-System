/**
 * FoxterAI_Server/middleware/auth.js
 * Middleware для проверки API ключа
 */

const config = require('../config/config');
const logger = require('../utils/logger');

/**
 * Проверка API ключа для административных запросов
 */
function checkAdminAuth(req, res, next) {
    // Получаем API ключ из заголовков
    const apiKey = req.headers['x-api-key'] || 
                   req.headers['authorization']?.replace('Bearer ', '') ||
                   req.query.api_key;
    
    // Маскируем ключ для логов
    const maskedKey = apiKey ? apiKey.substring(0, 10) + '...' : 'отсутствует';
    
    // Проверка наличия ключа
    if (!apiKey) {
        logger.warn(`Отклонен запрос без API ключа с IP ${req.ip}`);
        return res.status(401).json({ 
            success: false, 
            error: 'API_KEY_REQUIRED',
            message: 'API key is required for this endpoint'
        });
    }
    
    // Проверка правильности ключа
    if (apiKey !== config.API_KEY) {
        logger.warn(`Неверный API ключ: ${maskedKey} с IP ${req.ip}`);
        return res.status(401).json({ 
            success: false, 
            error: 'INVALID_API_KEY',
            message: 'Invalid API key'
        });
    }
    
    // Ключ правильный, продолжаем
    logger.debug(`Авторизован запрос с ключом ${maskedKey} от IP ${req.ip}`);
    next();
}

/**
 * Опциональная проверка API ключа
 * Не блокирует запрос, но устанавливает req.isAuthenticated
 */
function optionalAuth(req, res, next) {
    const apiKey = req.headers['x-api-key'] || 
                   req.headers['authorization']?.replace('Bearer ', '') ||
                   req.query.api_key;
    
    req.isAuthenticated = apiKey === config.API_KEY;
    next();
}

module.exports = checkAdminAuth;
module.exports.optional = optionalAuth;