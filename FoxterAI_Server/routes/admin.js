/**
 * FoxterAI_Server/routes/admin.js
 * ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ
 * Административные маршруты
 */

const express = require('express');
const router = express.Router();
const db = require('../database/connection');
const authMiddleware = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');
const eventLogger = require('../services/eventLogger');
const logger = require('../utils/logger');

// Все маршруты требуют авторизации
router.use(authMiddleware);

/**
 * POST /api/admin/cleanup
 * Очистка старых данных
 */
router.post('/cleanup', asyncHandler(async (req, res) => {
    const { days = 30 } = req.body;
    
    logger.info(`Cleanup requested for data older than ${days} days`);
    
    // Очистка событий
    const deletedEvents = await eventLogger.cleanup(days);
    
    // Очистка старых проверок
    const checksResult = await db.run(
        `DELETE FROM checks WHERE check_date < datetime('now', '-${days} days')`
    );
    
    logger.info(`Cleanup completed: ${deletedEvents} events, ${checksResult.changes} checks`);
    
    res.json({
        success: true,
        message: `Cleaned data older than ${days} days`,
        cleaned: {
            events: deletedEvents,
            checks: checksResult.changes
        }
    });
}));

/**
 * GET /api/admin/backup
 * Информация о базе данных для бэкапа
 */
router.get('/backup', asyncHandler(async (req, res) => {
    const stats = await db.get(`
        SELECT 
            COUNT(*) as total_licenses,
            (SELECT COUNT(*) FROM events) as total_events,
            (SELECT COUNT(*) FROM checks) as total_checks
        FROM licenses
    `);
    
    // Размер базы данных
    const fs = require('fs');
    const path = require('path');
    const dbPath = path.resolve('./licenses.db');
    let dbSize = 0;
    
    try {
        const dbStats = fs.statSync(dbPath);
        dbSize = dbStats.size;
    } catch (error) {
        logger.error('Failed to get database size:', error);
    }
    
    res.json({
        success: true,
        database: {
            file: 'licenses.db',
            path: dbPath,
            size: dbSize,
            size_mb: (dbSize / (1024 * 1024)).toFixed(2),
            records: {
                licenses: stats.total_licenses || 0,
                events: stats.total_events || 0,
                checks: stats.total_checks || 0,
                total: (stats.total_licenses || 0) + (stats.total_events || 0) + (stats.total_checks || 0)
            }
        }
    });
}));

/**
 * POST /api/admin/reset-failed
 * Сброс счетчика неудачных проверок
 */
router.post('/reset-failed', asyncHandler(async (req, res) => {
    const { license_key } = req.body;
    
    if (license_key) {
        await db.run(
            'UPDATE licenses SET failed_checks = 0 WHERE license_key = ?',
            [license_key]
        );
        
        logger.info(`Reset failed checks for license ${license_key.substring(0, 8)}...`);
        
        res.json({ 
            success: true,
            message: `Failed checks reset for license ${license_key.substring(0, 8)}...`
        });
    } else {
        const result = await db.run('UPDATE licenses SET failed_checks = 0');
        
        logger.info(`Reset all failed checks (${result.changes} licenses)`);
        
        res.json({ 
            success: true,
            message: `Failed checks reset for all licenses`,
            affected: result.changes
        });
    }
}));

/**
 * GET /api/admin/system-info
 * Информация о системе
 */
router.get('/system-info', asyncHandler(async (req, res) => {
    const os = require('os');
    
    res.json({
        success: true,
        system: {
            platform: os.platform(),
            arch: os.arch(),
            hostname: os.hostname(),
            uptime: os.uptime(),
            memory: {
                total: os.totalmem(),
                free: os.freemem(),
                used: os.totalmem() - os.freemem(),
                usage_percent: ((os.totalmem() - os.freemem()) / os.totalmem() * 100).toFixed(2)
            },
            cpu: os.cpus()[0].model,
            cores: os.cpus().length,
            node_version: process.version
        },
        process: {
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            pid: process.pid
        }
    });
}));

/**
 * POST /api/admin/maintenance
 * Режим обслуживания
 */
router.post('/maintenance', asyncHandler(async (req, res) => {
    const { enabled, message } = req.body;
    
    // Здесь можно реализовать логику режима обслуживания
    // Например, сохранить состояние в БД или в памяти
    
    logger.info(`Maintenance mode ${enabled ? 'enabled' : 'disabled'}`);
    
    res.json({
        success: true,
        maintenance: {
            enabled: enabled || false,
            message: message || 'System is under maintenance'
        }
    });
}));

/**
 * GET /api/admin/logs
 * Получение последних логов
 */
router.get('/logs', asyncHandler(async (req, res) => {
    const { lines = 100 } = req.query;
    const fs = require('fs');
    const path = require('path');
    
    // Находим текущий файл логов
    const date = new Date().toISOString().split('T')[0];
    const logFile = path.join('./logs', `server-${date}.log`);
    
    let logs = [];
    
    try {
        if (fs.existsSync(logFile)) {
            const content = fs.readFileSync(logFile, 'utf8');
            const allLines = content.split('\n').filter(line => line.trim());
            logs = allLines.slice(-lines); // Берем последние N строк
        }
    } catch (error) {
        logger.error('Failed to read logs:', error);
    }
    
    res.json({
        success: true,
        file: logFile,
        lines: logs.length,
        logs: logs
    });
}));

/**
 * POST /api/admin/test-email
 * Тест отправки email (если настроен)
 */
router.post('/test-email', asyncHandler(async (req, res) => {
    const { email } = req.body;
    
    if (!email) {
        return res.status(400).json({
            success: false,
            error: 'EMAIL_REQUIRED'
        });
    }
    
    // Здесь можно реализовать отправку тестового письма
    logger.info(`Test email requested for ${email}`);
    
    res.json({
        success: true,
        message: `Test email would be sent to ${email} (email service not configured)`
    });
}));

/**
 * DELETE /api/admin/events
 * Очистка всех событий
 */
router.delete('/events', asyncHandler(async (req, res) => {
    const result = await db.run('DELETE FROM events');
    
    logger.warn(`All events deleted (${result.changes} records)`);
    
    res.json({
        success: true,
        deleted: result.changes
    });
}));

/**
 * POST /api/admin/vacuum
 * Оптимизация базы данных
 */
router.post('/vacuum', asyncHandler(async (req, res) => {
    await db.run('VACUUM');
    
    logger.info('Database vacuum completed');
    
    res.json({
        success: true,
        message: 'Database optimized successfully'
    });
}));

module.exports = router;