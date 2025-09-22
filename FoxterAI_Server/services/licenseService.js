/**
 * FoxterAI_Server/services/licenseService.js
 * Бизнес-логика работы с лицензиями - РУССКАЯ ВЕРСИЯ
 */

const crypto = require('crypto');
const db = require('../database/connection');
const logger = require('../utils/logger');
const eventLogger = require('./eventLogger');

class LicenseService {
    
    // Генерация уникального ключа лицензии
    generateKey(prefix = 'FXAI') {
        const timestamp = Date.now().toString(36).toUpperCase();
        const random = crypto.randomBytes(4).toString('hex').toUpperCase();
        const hash = crypto.randomBytes(8).toString('hex').toUpperCase();
        return `${prefix}-${timestamp.substring(0, 2)}-${random}-${hash}`;
    }
    
    // Создание новой лицензии
    async create(data) {
        const {
            client_name,
            client_contact,
            client_telegram,
            robot_name,
            months = 1,
            notes,
            universal = false
        } = data;
        
        // Генерируем ключ
        const prefix = universal ? 'UNIV' : (robot_name ? robot_name.substring(0, 4).toUpperCase() : 'FXAI');
        const license_key = this.generateKey(prefix);
        
        // Сохраняем в БД
        const robotToSave = universal ? null : robot_name;
        
        try {
            const result = await db.run(
                `INSERT INTO licenses (license_key, client_name, client_contact, client_telegram, robot_name, months, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?)`,
                [license_key, client_name, client_contact, client_telegram, robotToSave, months, notes]
            );
            
            // Логируем событие
            const licenseType = universal ? 'универсальная' : `для робота ${robot_name}`;
            logger.info(`Создана ${licenseType} лицензия ${license_key.substring(0, 12)}... для клиента ${client_name}`);
            
            await eventLogger.log('СОЗДАНИЕ_ЛИЦЕНЗИИ', license_key, robotToSave, client_name,
                `Создана ${licenseType} лицензия`, 'обычный');
            
            return {
                success: true,
                license_key,
                license: {
                    id: result.id,
                    license_key,
                    client_name,
                    client_contact,
                    client_telegram,
                    robot_name: robotToSave,
                    status: 'created',
                    universal,
                    months,
                    notes
                }
            };
        } catch (error) {
            logger.error('Не удалось создать лицензию:', error);
            throw error;
        }
    }
    
    // Получение всех лицензий
    async getAll(filters = {}) {
        let query = 'SELECT * FROM licenses WHERE 1=1';
        const params = [];
        
        // Фильтры
        if (filters.status) {
            query += ' AND status = ?';
            params.push(filters.status);
        }
        
        if (filters.robot_name) {
            query += ' AND robot_name = ?';
            params.push(filters.robot_name);
        }
        
        query += ' ORDER BY created_date DESC';
        
        try {
            const licenses = await db.all(query, params);
            
            // Добавляем вычисляемые поля
            return licenses.map(license => {
                const now = new Date();
                const expiryDate = license.expiry_date ? new Date(license.expiry_date) : null;
                const daysLeft = expiryDate ? Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24)) : null;
                
                return {
                    ...license,
                    days_left: daysLeft,
                    is_expired: daysLeft !== null && daysLeft < 0,
                    is_expiring: daysLeft !== null && daysLeft <= 7 && daysLeft > 0
                };
            });
        } catch (error) {
            logger.error('Не удалось получить лицензии:', error);
            throw error;
        }
    }
    
    // Получение одной лицензии
    async getByKey(licenseKey) {
        try {
            return await db.get('SELECT * FROM licenses WHERE license_key = ?', [licenseKey]);
        } catch (error) {
            logger.error('Не удалось получить лицензию:', error);
            throw error;
        }
    }
    
    // Обновление лицензии
    async update(licenseKey, updates) {
        const allowedFields = ['client_name', 'client_contact', 'client_telegram', 'notes'];
        const updatePairs = [];
        const values = [];
        
        for (const field of allowedFields) {
            if (updates[field] !== undefined) {
                updatePairs.push(`${field} = ?`);
                values.push(updates[field]);
            }
        }
        
        if (updatePairs.length === 0) {
            throw new Error('Нет полей для обновления');
        }
        
        values.push(licenseKey);
        const query = `UPDATE licenses SET ${updatePairs.join(', ')} WHERE license_key = ?`;
        
        try {
            await db.run(query, values);
            logger.info(`Обновлена лицензия ${licenseKey.substring(0, 12)}...`);
            return { success: true };
        } catch (error) {
            logger.error('Не удалось обновить лицензию:', error);
            throw error;
        }
    }
    
    // Блокировка/разблокировка
    async setBlockStatus(licenseKey, blocked) {
        const newStatus = blocked ? 'blocked' : 'active';
        
        try {
            await db.run(
                'UPDATE licenses SET status = ? WHERE license_key = ?',
                [newStatus, licenseKey]
            );
            
            logger.info(`Лицензия ${licenseKey.substring(0, 12)}... ${blocked ? 'заблокирована' : 'разблокирована'}`);
            return { success: true };
        } catch (error) {
            logger.error('Не удалось изменить статус блокировки:', error);
            throw error;
        }
    }
    
    // Удаление лицензии
    async delete(licenseKey) {
        try {
            await db.run('DELETE FROM licenses WHERE license_key = ?', [licenseKey]);
            logger.info(`Удалена лицензия ${licenseKey.substring(0, 12)}...`);
            return { success: true };
        } catch (error) {
            logger.error('Не удалось удалить лицензию:', error);
            throw error;
        }
    }
    
    // Продление лицензии
    async extend(licenseKey, months) {
        try {
            const license = await this.getByKey(licenseKey);
            if (!license) {
                throw new Error('Лицензия не найдена');
            }
            
            // Вычисляем новую дату
            let baseDate = license.expiry_date ? new Date(license.expiry_date) : new Date();
            if (baseDate < new Date()) {
                baseDate = new Date(); // Если истекла, продлеваем от сегодня
            }
            
            const newExpiry = new Date(baseDate);
            newExpiry.setMonth(newExpiry.getMonth() + months);
            
            await db.run(
                'UPDATE licenses SET expiry_date = ? WHERE license_key = ?',
                [newExpiry.toISOString(), licenseKey]
            );
            
            logger.info(`Продлена лицензия ${licenseKey.substring(0, 12)}... на ${months} месяцев`);
            return { success: true, new_expiry: newExpiry };
        } catch (error) {
            logger.error('Не удалось продлить лицензию:', error);
            throw error;
        }
    }
}

module.exports = new LicenseService();