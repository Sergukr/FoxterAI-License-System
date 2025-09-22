// =====================
// FoxterAI_Server/middleware/errorHandler.js
// Глобальный обработчик ошибок
// =====================

const logger = require('../utils/logger');

// Обертка для асинхронных маршрутов
function asyncHandler(fn) {
    return function(req, res, next) {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
}

// Главный обработчик ошибок
function errorHandler(err, req, res, next) {
    // Логируем ошибку
    logger.error('Request error:', {
        error: err.message,
        stack: err.stack,
        url: req.url,
        method: req.method,
        ip: req.ip,
        body: req.body
    });
    
    // Определяем статус
    const status = err.status || err.statusCode || 500;
    
    // Формируем ответ
    const response = {
        success: false,
        error: err.code || 'INTERNAL_ERROR',
        message: err.message || 'Internal server error'
    };
    
    // В режиме разработки добавляем стек
    if (process.env.NODE_ENV === 'development') {
        response.stack = err.stack;
    }
    
    // Отправляем ответ
    res.status(status).json(response);
}

// Обработчик для несуществующих маршрутов
function notFound(req, res, next) {
    const error = new Error(`Not Found - ${req.originalUrl}`);
    error.status = 404;
    error.code = 'NOT_FOUND';
    next(error);
}

module.exports = errorHandler;
module.exports.asyncHandler = asyncHandler;
module.exports.notFound = notFound;