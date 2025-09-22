/**
 * FoxterAI_Server/routes/api.js
 * ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ
 * Дополнительные API маршруты
 */

const express = require('express');
const router = express.Router();
const db = require('../database/connection');
const authMiddleware = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');
const eventLogger = require('../services/eventLogger');
const logger = require('../utils/logger');
const config = require('../config/config');

/**
 * GET /api/violations
 * Получить нарушения (публичный маршрут для совместимости)
 */
router.get('/violations', authMiddleware, asyncHandler(async (req, res) => {
    const { days = 7 } = req.query;
    const violations = await eventLogger.getViolations(days);
    
    res.json({
        success: true,
        violations,
        count: violations.length,
        period_days: days
    });
}));

/**
 * GET /api/info
 * Общая информация о сервере
 */
router.get('/info', asyncHandler(async (req, res) => {
    const stats = await db.get(`
        SELECT 
            COUNT(*) as total_licenses,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_licenses
        FROM licenses
    `);
    
    res.json({
        server: 'FoxterAI License Server',
        version: '4.0.0',
        features: {
            universal_licenses: true,
            fingerprinting: true,
            autonomy_mode: true,
            check_interval: config.CHECK_INTERVAL_HOURS,
            autonomy_hours: config.AUTONOMY_HOURS
        },
        statistics: {
            total_licenses: stats.total_licenses || 0,
            active_licenses: stats.active_licenses || 0
        }
    });
}));

/**
 * POST /api/verify-license
 * Проверка валидности лицензии (упрощенная версия для клиентов)
 */
router.post('/verify-license', asyncHandler(async (req, res) => {
    const { key } = req.body;
    
    if (!key) {
        return res.status(400).json({
            success: false,
            error: 'KEY_REQUIRED'
        });
    }
    
    const license = await db.get(
        'SELECT status, expiry_date FROM licenses WHERE license_key = ?',
        [key]
    );
    
    if (!license) {
        return res.json({
            success: false,
            valid: false,
            error: 'LICENSE_NOT_FOUND'
        });
    }
    
    const isValid = license.status === 'active' && 
                   (!license.expiry_date || new Date(license.expiry_date) > new Date());
    
    res.json({
        success: true,
        valid: isValid,
        status: license.status
    });
}));

/**
 * GET /api/robots
 * Список поддерживаемых роботов
 */
router.get('/robots', authMiddleware, asyncHandler(async (req, res) => {
    const robots = await db.all(`
        SELECT DISTINCT 
            robot_name,
            COUNT(*) as license_count,
            MAX(robot_version) as latest_version
        FROM licenses
        WHERE robot_name IS NOT NULL
        GROUP BY robot_name
        ORDER BY license_count DESC
    `);
    
    res.json({
        success: true,
        robots,
        count: robots.length
    });
}));

/**
 * GET /api/brokers
 * Список брокеров
 */
router.get('/brokers', authMiddleware, asyncHandler(async (req, res) => {
    const brokers = await db.all(`
        SELECT DISTINCT 
            broker_name,
            COUNT(*) as license_count,
            SUM(CASE WHEN account_type = 'Real' THEN 1 ELSE 0 END) as real_accounts,
            SUM(CASE WHEN account_type = 'Demo' THEN 1 ELSE 0 END) as demo_accounts
        FROM licenses
        WHERE broker_name IS NOT NULL
        GROUP BY broker_name
        ORDER BY license_count DESC
    `);
    
    res.json({
        success: true,
        brokers,
        count: brokers.length
    });
}));

/**
 * GET /api/activity
 * Активность за последние 24 часа
 */
router.get('/activity', authMiddleware, asyncHandler(async (req, res) => {
    const activity = await db.all(`
        SELECT 
            strftime('%H:00', check_date) as hour,
            COUNT(*) as checks
        FROM checks
        WHERE check_date >= datetime('now', '-24 hours')
        GROUP BY strftime('%H', check_date)
        ORDER BY hour
    `);
    
    const events = await db.all(`
        SELECT 
            strftime('%H:00', event_date) as hour,
            COUNT(*) as events
        FROM events
        WHERE event_date >= datetime('now', '-24 hours')
        GROUP BY strftime('%H', event_date)
        ORDER BY hour
    `);
    
    res.json({
        success: true,
        activity: {
            checks: activity,
            events: events
        }
    });
}));

/**
 * GET /api/top-clients
 * Топ клиентов по количеству лицензий
 */
router.get('/top-clients', authMiddleware, asyncHandler(async (req, res) => {
    const { limit = 10 } = req.query;
    
    const clients = await db.all(`
        SELECT 
            client_name,
            COUNT(*) as license_count,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
            MAX(created_date) as last_license_date
        FROM licenses
        WHERE client_name IS NOT NULL
        GROUP BY client_name
        ORDER BY license_count DESC
        LIMIT ?
    `, [limit]);
    
    res.json({
        success: true,
        clients,
        count: clients.length
    });
}));

/**
 * POST /api/search
 * Поиск по лицензиям
 */
router.post('/search', authMiddleware, asyncHandler(async (req, res) => {
    const { query, field = 'all' } = req.body;
    
    if (!query) {
        return res.status(400).json({
            success: false,
            error: 'QUERY_REQUIRED'
        });
    }
    
    let sql = 'SELECT * FROM licenses WHERE ';
    const searchParam = `%${query}%`;
    
    switch (field) {
        case 'key':
            sql += 'license_key LIKE ?';
            break;
        case 'client':
            sql += 'client_name LIKE ?';
            break;
        case 'account':
            sql += 'account_number LIKE ?';
            break;
        case 'robot':
            sql += 'robot_name LIKE ?';
            break;
        default: // all
            sql += `(
                license_key LIKE ? OR 
                client_name LIKE ? OR 
                account_number LIKE ? OR 
                robot_name LIKE ? OR
                client_contact LIKE ? OR
                client_telegram LIKE ?
            )`;
    }
    
    sql += ' ORDER BY created_date DESC LIMIT 100';
    
    const params = field === 'all' 
        ? [searchParam, searchParam, searchParam, searchParam, searchParam, searchParam]
        : [searchParam];
    
    const results = await db.all(sql, params);
    
    res.json({
        success: true,
        results,
        count: results.length
    });
}));

/**
 * GET /api/export
 * Экспорт данных в JSON
 */
router.get('/export', authMiddleware, asyncHandler(async (req, res) => {
    const { table = 'licenses' } = req.query;
    
    // Проверяем допустимые таблицы
    const allowedTables = ['licenses', 'events', 'checks'];
    if (!allowedTables.includes(table)) {
        return res.status(400).json({
            success: false,
            error: 'INVALID_TABLE'
        });
    }
    
    const data = await db.all(`SELECT * FROM ${table}`);
    
    res.json({
        success: true,
        table,
        count: data.length,
        data
    });
}));

/**
 * POST /api/batch-update
 * Массовое обновление статусов
 */
router.post('/batch-update', authMiddleware, asyncHandler(async (req, res) => {
    const { license_keys, status } = req.body;
    
    if (!Array.isArray(license_keys) || !status) {
        return res.status(400).json({
            success: false,
            error: 'INVALID_PARAMETERS'
        });
    }
    
    // Допустимые статусы
    const allowedStatuses = ['active', 'blocked', 'expired'];
    if (!allowedStatuses.includes(status)) {
        return res.status(400).json({
            success: false,
            error: 'INVALID_STATUS'
        });
    }
    
    // Обновляем каждую лицензию
    let updated = 0;
    for (const key of license_keys) {
        const result = await db.run(
            'UPDATE licenses SET status = ? WHERE license_key = ?',
            [status, key]
        );
        if (result.changes > 0) {
            updated++;
        }
    }
    
    logger.info(`Batch update: ${updated} licenses set to ${status}`);
    
    res.json({
        success: true,
        requested: license_keys.length,
        updated
    });
}));

/**
 * GET /api/config
 * Получение конфигурации (для админки)
 */
router.get('/config', authMiddleware, (req, res) => {
    res.json({
        success: true,
        config: {
            check_interval_hours: config.CHECK_INTERVAL_HOURS,
            autonomy_hours: config.AUTONOMY_HOURS,
            rate_limit: config.RATE_LIMIT,
            environment: config.NODE_ENV
        }
    });
});

module.exports = router;