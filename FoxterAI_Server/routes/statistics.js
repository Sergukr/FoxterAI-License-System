/**
 * FoxterAI_Server/routes/statistics.js
 * API маршруты для статистики
 */

const express = require('express');
const router = express.Router();
const db = require('../database/connection');
const authMiddleware = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');
const eventLogger = require('../services/eventLogger');

// Все маршруты требуют авторизации
router.use(authMiddleware);

/**
 * GET /api/statistics
 * Общая статистика
 */
router.get('/', asyncHandler(async (req, res) => {
    const stats = await db.get(`
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired,
            SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) as blocked,
            SUM(CASE WHEN status = 'created' THEN 1 ELSE 0 END) as inactive,
            SUM(CASE WHEN robot_name IS NULL AND status = 'created' THEN 1 ELSE 0 END) as universal_unused,
            SUM(CASE WHEN account_type = 'Real' THEN last_balance ELSE 0 END) as total_balance,
            COUNT(DISTINCT robot_name) as unique_robots,
            COUNT(DISTINCT account_number) as unique_accounts
        FROM licenses
    `);
    
    res.json({
        success: true,
        statistics: {
            licenses: {
                total: stats.total || 0,
                active: stats.active || 0,
                expired: stats.expired || 0,
                blocked: stats.blocked || 0,
                inactive: stats.inactive || 0,
                universal_unused: stats.universal_unused || 0
            },
            metrics: {
                total_balance: stats.total_balance || 0,
                unique_robots: stats.unique_robots || 0,
                unique_accounts: stats.unique_accounts || 0
            }
        }
    });
}));

/**
 * GET /api/statistics/violations
 * Статистика нарушений
 */
router.get('/violations', asyncHandler(async (req, res) => {
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
 * GET /api/statistics/events
 * События системы
 */
router.get('/events', asyncHandler(async (req, res) => {
    const events = await eventLogger.getEvents(req.query);
    
    res.json({
        success: true,
        events,
        count: events.length
    });
}));

/**
 * GET /api/statistics/revenue
 * Статистика доходов
 */
router.get('/revenue', asyncHandler(async (req, res) => {
    const { period = 'month' } = req.query;
    
    let dateFilter = "datetime('now', '-1 month')";
    if (period === 'week') {
        dateFilter = "datetime('now', '-7 days')";
    } else if (period === 'year') {
        dateFilter = "datetime('now', '-1 year')";
    }
    
    const revenue = await db.all(`
        SELECT 
            DATE(created_date) as date,
            COUNT(*) as licenses_created,
            SUM(months) as total_months
        FROM licenses
        WHERE created_date >= ${dateFilter}
        GROUP BY DATE(created_date)
        ORDER BY date DESC
    `);
    
    res.json({
        success: true,
        revenue,
        period
    });
}));

/**
 * GET /api/statistics/robots
 * Статистика по роботам
 */
router.get('/robots', asyncHandler(async (req, res) => {
    const robots = await db.all(`
        SELECT 
            robot_name,
            COUNT(*) as license_count,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
            AVG(last_balance) as avg_balance
        FROM licenses
        WHERE robot_name IS NOT NULL
        GROUP BY robot_name
        ORDER BY license_count DESC
    `);
    
    res.json({
        success: true,
        robots
    });
}));

module.exports = router;