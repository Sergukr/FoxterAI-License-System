// =====================
// FoxterAI_Server/routes/licenses.js
// API маршруты для работы с лицензиями
// ИСПРАВЛЕНО: Правильный формат ответа для десктоп приложения
// =====================

const express = require('express');
const router = express.Router();
const licenseService = require('../services/licenseService');
const authMiddleware = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

// Все маршруты требуют авторизации
router.use(authMiddleware);

// GET /api/licenses - получить все лицензии
router.get('/', asyncHandler(async (req, res) => {
    const filters = {
        status: req.query.status,
        robot_name: req.query.robot_name
    };
    
    try {
        const licenses = await licenseService.getAll(filters);
        
        // ИСПРАВЛЕНО: Всегда возвращаем в правильном формате
        res.json({
            success: true,
            licenses: licenses || [],
            count: licenses ? licenses.length : 0
        });
    } catch (error) {
        logger.error('Ошибка получения лицензий:', error);
        res.status(500).json({
            success: false,
            error: 'INTERNAL_ERROR',
            message: 'Не удалось получить лицензии'
        });
    }
}));

// GET /api/licenses/:key - получить одну лицензию
router.get('/:key', asyncHandler(async (req, res) => {
    const license = await licenseService.getByKey(req.params.key);
    
    if (!license) {
        return res.status(404).json({
            success: false,
            error: 'LICENSE_NOT_FOUND'
        });
    }
    
    // ИСПРАВЛЕНО: Единообразный формат ответа
    res.json({
        success: true,
        license: license
    });
}));

// POST /api/licenses - создать лицензию
router.post('/', asyncHandler(async (req, res) => {
    logger.info('Создание лицензии:', {
        client: req.body.client_name,
        months: req.body.months,
        universal: req.body.universal
    });
    
    // Добавляем флаг universal если не указан
    if (req.body.universal === undefined) {
        req.body.universal = true; // По умолчанию создаем универсальные
    }
    
    const result = await licenseService.create(req.body);
    
    if (result.success) {
        logger.info(`✅ Лицензия создана: ${result.license_key}`);
        res.status(201).json(result);
    } else {
        logger.error(`❌ Ошибка создания лицензии: ${result.error}`);
        res.status(400).json(result);
    }
}));

// PUT /api/licenses/:key - обновить лицензию
router.put('/:key', asyncHandler(async (req, res) => {
    const result = await licenseService.update(req.params.key, req.body);
    
    res.json({
        success: true,
        ...result
    });
}));

// POST /api/licenses/:key/block - заблокировать/разблокировать
router.post('/:key/block', asyncHandler(async (req, res) => {
    const { blocked } = req.body;
    const result = await licenseService.setBlockStatus(req.params.key, blocked);
    
    logger.info(`Лицензия ${req.params.key} ${blocked ? 'заблокирована' : 'разблокирована'}`);
    
    res.json({
        success: true,
        blocked: blocked,
        ...result
    });
}));

// POST /api/licenses/:key/extend - продлить лицензию
router.post('/:key/extend', asyncHandler(async (req, res) => {
    const { months } = req.body;
    
    if (!months || months < 1) {
        return res.status(400).json({
            success: false,
            error: 'INVALID_MONTHS'
        });
    }
    
    const result = await licenseService.extend(req.params.key, months);
    
    logger.info(`Лицензия ${req.params.key} продлена на ${months} мес.`);
    
    res.json({
        success: true,
        months_added: months,
        ...result
    });
}));

// DELETE /api/licenses/:key - удалить лицензию
router.delete('/:key', asyncHandler(async (req, res) => {
    const result = await licenseService.delete(req.params.key);
    
    logger.info(`Лицензия ${req.params.key} удалена`);
    
    res.json({
        success: true,
        deleted: true,
        ...result
    });
}));

// GET /api/licenses/stats - статистика лицензий
router.get('/stats', asyncHandler(async (req, res) => {
    const stats = await licenseService.getStatistics();
    
    res.json({
        success: true,
        statistics: stats
    });
}));

module.exports = router;