/**
 * FoxterAI_Server/services/eventLogger.js
 * Сервис логирования событий в БД - РУССКАЯ ВЕРСИЯ
 */

const db = require('../database/connection');
const logger = require('../utils/logger');

class EventLogger {
    
    /**
     * Запись события в БД
     */
    async log(eventType, licenseKey, robotName, clientName, description, priority = 'обычный', details = {}) {
        try {
            const detailsJson = JSON.stringify(details);
            const ipAddress = details.ip || null;
            
            await db.run(`
                INSERT INTO events (
                    event_type, 
                    license_key, 
                    robot_name, 
                    client_name, 
                    description, 
                    priority, 
                    details, 
                    ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            `, [
                eventType || 'НЕИЗВЕСТНО',
                licenseKey || null,
                robotName || null,
                clientName || null,
                description || '',
                priority || 'обычный',
                detailsJson || '{}',
                ipAddress || null
            ]);
            
            logger.debug(`Событие записано: ${eventType}`, { licenseKey, robotName });
            
        } catch (error) {
            // Не даем ошибке логирования сломать основную логику
            logger.error('Не удалось записать событие:', {
                error: error.message,
                eventType,
                licenseKey
            });
            
            // Пытаемся записать упрощенную версию
            try {
                await db.run(
                    `INSERT INTO events (event_type, description) VALUES (?, ?)`,
                    [eventType || 'ОШИБКА', description || 'Ошибка записи события']
                );
            } catch (secondError) {
                logger.error('Критическая ошибка: Невозможно записать в таблицу событий', secondError);
            }
        }
    }
    
    /**
     * Получение событий за период
     */
    async getEvents(filters = {}) {
        const { days = 7, eventType, priority, licenseKey } = filters;
        
        let query = `
            SELECT * FROM events 
            WHERE event_date >= datetime('now', '-${days} days')
        `;
        const params = [];
        
        if (eventType) {
            query += ' AND event_type = ?';
            params.push(eventType);
        }
        
        if (priority) {
            query += ' AND priority = ?';
            params.push(priority);
        }
        
        if (licenseKey) {
            query += ' AND license_key = ?';
            params.push(licenseKey);
        }
        
        query += ' ORDER BY event_date DESC';
        
        try {
            return await db.all(query, params);
        } catch (error) {
            logger.error('Не удалось получить события:', error);
            return [];
        }
    }
    
    /**
     * Получение нарушений
     */
    async getViolations(days = 7) {
        const violationTypes = [
            'БЛОКИРОВКА_АКТИВАЦИИ',
            'ПОПЫТКА_КРАЖИ_ЛИЦЕНЗИИ',
            'НЕСООТВЕТСТВИЕ_РОБОТА',
            'ИЗМЕНЕНИЕ_ОКРУЖЕНИЯ',
            'МНОЖЕСТВЕННАЯ_ПОПЫТКА_АКТИВАЦИИ'
        ];
        
        const query = `
            SELECT * FROM events 
            WHERE event_type IN (${violationTypes.map(() => '?').join(',')})
            AND event_date >= datetime('now', '-${days} days')
            ORDER BY event_date DESC
        `;
        
        try {
            return await db.all(query, violationTypes);
        } catch (error) {
            logger.error('Не удалось получить нарушения:', error);
            return [];
        }
    }
    
    /**
     * Очистка старых событий
     */
    async cleanup(daysToKeep = 30) {
        try {
            const result = await db.run(
                `DELETE FROM events WHERE event_date < datetime('now', '-${daysToKeep} days')`
            );
            
            logger.info(`Очищено ${result.changes} старых событий`);
            return result.changes;
        } catch (error) {
            logger.error('Не удалось очистить события:', error);
            return 0;
        }
    }
}

module.exports = new EventLogger();