/**
 * FoxterAI_Server/routes/activation.js
 * Маршруты для активации и проверки лицензий (для роботов MT4)
 */

const express = require('express');
const router = express.Router();
const activationService = require('../services/activationService');
const { asyncHandler } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

/**
 * POST /activate
 * Универсальная активация лицензии
 */
router.post('/activate', asyncHandler(async (req, res) => {
    const ip = req.ip || req.connection.remoteAddress;
    
    logger.info('Activation request received', {
        ip,
        account: req.body.account?.substring(0, 3) + '***',
        robot: req.body.robot_name
    });
    
    const result = await activationService.activate({
        ...req.body,
        ip
    });
    
    res.json(result);
}));

/**
 * POST /api/universal-activate
 * Альтернативный эндпоинт для универсальной активации
 */
router.post('/api/universal-activate', asyncHandler(async (req, res) => {
    const ip = req.ip || req.connection.remoteAddress;
    
    const result = await activationService.activate({
        ...req.body,
        ip
    });
    
    res.json(result);
}));

/**
 * POST /check
 * Проверка статуса лицензии
 */
router.post('/check', asyncHandler(async (req, res) => {
    const ip = req.ip || req.connection.remoteAddress;
    
    logger.debug('Check request received', {
        ip,
        key: req.body.key?.substring(0, 8) + '***'
    });
    
    const result = await activationService.check({
        ...req.body,
        ip
    });
    
    res.json(result);
}));

/**
 * POST /heartbeat
 * Heartbeat для поддержания активности
 */
router.post('/heartbeat', asyncHandler(async (req, res) => {
    const ip = req.ip || req.connection.remoteAddress;
    
    const result = await activationService.heartbeat({
        ...req.body,
        ip
    });
    
    res.json(result);
}));

/**
 * GET /verify/:key
 * Простая проверка существования лицензии
 */
router.get('/verify/:key', asyncHandler(async (req, res) => {
    const exists = await activationService.verifyKey(req.params.key);
    
    res.json({
        success: exists,
        valid: exists
    });
}));

module.exports = router;