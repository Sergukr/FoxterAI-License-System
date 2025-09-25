/**
 * FoxterAI_Server/services/activationService.js
 * Бизнес-логика активации и проверки лицензий
 * ИСПРАВЛЕНО: Добавлено сохранение equity и profit в heartbeat
 */

const crypto = require('crypto');
const db = require('../database/connection');
const logger = require('../utils/logger');
const eventLogger = require('./eventLogger');
const config = require('../config/config');

class ActivationService {
    
    /**
     * Создание отпечатка для привязки и аналитики
     */
    createFingerprint(data) {
        const {
            account,
            broker,
            account_owner,
            account_type,
            robot_name,
            robot_version
        } = data;
        
        // Полный отпечаток для аналитики (сохраняем ВСЕ данные)
        const fullFingerprint = `${account || ''}_${broker || ''}_${account_type || 'Real'}_${robot_name || 'FoxterAI'}_${robot_version || '1.6'}_${account_owner || ''}`;
        
        // Хэш только от ключевых параметров привязки (account + robot_name)
        const bindingString = `${account || ''}_${robot_name || 'FoxterAI'}`;
        const hash = crypto.createHash('md5').update(bindingString).digest('hex').substring(0, 8);
        
        return {
            full: fullFingerprint,  // Полные данные для аналитики
            hash: hash,             // Хэш только от account + robot_name
            components: {
                account,
                broker,
                account_owner,
                account_type: account_type || 'Real',
                robot_name: robot_name || 'FoxterAI',
                robot_version: robot_version || '1.6'
            }
        };
    }
    
    /**
     * Универсальная активация лицензии
     */
    async activate(data) {
        // Извлекаем параметры с учетом различных вариантов имен от MT4
        const key = data.key || data.license_key || data.Key;
        const account = data.account || data.AccountNumber || data.Account;
        const broker = data.broker || data.broker_server || data.BrokerServer || data.Broker;
        const account_owner = data.account_owner || data.owner_name || data.AccountOwner || data.OwnerName || '';
        
        // Дополнительные параметры с дефолтными значениями
        const robot_name = data.robot_name || data.RobotName || 'FoxterAI';
        const robot_version = data.robot_version || data.RobotVersion || data.Version || '1.6';
        const balance = data.balance || data.Balance || data.initial_balance || 0;
        const terminal_version = data.terminal_version || data.TerminalVersion || '';
        const os_info = data.os_info || data.OSInfo || '';
        const account_type = data.account_type || data.AccountType || 'Real';
        const ip = data.ip;
        
        // Логируем все полученные параметры для отладки
        logger.info('Activation parameters received:', {
            key: key ? key.substring(0, 8) + '***' : 'missing',
            account: account || 'missing',
            broker: broker || 'missing', 
            robot_name: robot_name,
            has_owner: !!account_owner,
            has_balance: !!balance
        });
        
        // Проверка минимальных обязательных полей
        if (!key || !account) {
            logger.warn('Activation failed: missing key or account');
            return {
                success: false,
                error: 'MISSING_PARAMETERS',
                message: 'Required: key and account number'
            };
        }
        
        const maskedKey = key.substring(0, 8) + '***';
        const maskedAccount = account.toString().substring(0, 3) + '***';
        
        try {
            // Проверяем существование лицензии
            const license = await db.get(
                'SELECT * FROM licenses WHERE license_key = ?',
                [key]
            );
            
            if (!license) {
                logger.warn(`License not found: ${maskedKey}`);
                return {
                    success: false,
                    error: 'LICENSE_NOT_FOUND',
                    message: 'Invalid license key'
                };
            }
            
            // Проверка статуса
            if (license.status === 'blocked') {
                logger.warn(`Blocked license activation attempt: ${maskedKey}`);
                await eventLogger.log('ACTIVATION_BLOCKED', maskedKey, robot_name, license.client_name,
                    'Попытка активации заблокированной лицензии', 'high', { ip });
                
                return {
                    success: false,
                    error: 'LICENSE_BLOCKED',
                    message: 'License is blocked'
                };
            }
            
            // Проверка истечения
            if (license.expiry_date && new Date(license.expiry_date) < new Date()) {
                logger.warn(`Expired license activation attempt: ${maskedKey}`);
                return {
                    success: false,
                    error: 'LICENSE_EXPIRED',
                    message: 'License has expired'
                };
            }
            
            // УНИВЕРСАЛЬНАЯ ЛИЦЕНЗИЯ - фиксация при первой активации
            if (!license.robot_name && !license.account_number) {
                // Это первая активация универсальной лицензии
                logger.info(`First activation of universal license ${maskedKey} by robot ${robot_name} on account ${maskedAccount}`);
                
                // Создаем полный отпечаток для аналитики
                const fingerprint = this.createFingerprint({
                    account,
                    broker,
                    account_owner,
                    account_type,
                    robot_name,
                    robot_version
                });
                
                const expiryDate = new Date();
                expiryDate.setMonth(expiryDate.getMonth() + (license.months || 1));
                
                // Фиксируем лицензию за роботом и счетом
                // Сохраняем ВСЕ данные для аналитики
                await db.run(`
                    UPDATE licenses SET
                        robot_name = ?,
                        robot_version = ?,
                        account_number = ?,
                        account_owner = ?,
                        account_type = ?,
                        broker_name = ?,
                        fingerprint = ?,
                        fingerprint_hash = ?,
                        activation_date = datetime('now'),
                        activation_ip = ?,
                        expiry_date = ?,
                        status = 'active',
                        terminal_version = ?,
                        os_info = ?,
                        last_balance = ?,
                        last_check = datetime('now'),
                        check_count = 1
                    WHERE license_key = ?
                `, [
                    robot_name,
                    robot_version,
                    account.toString(),
                    account_owner,
                    account_type,
                    broker || '',
                    fingerprint.full,      // Полный отпечаток для аналитики
                    fingerprint.hash,      // Хэш только от account + robot_name
                    ip,
                    expiryDate.toISOString(),
                    terminal_version,
                    os_info,
                    balance,
                    key
                ]);
                
                await eventLogger.log('LICENSE_ACTIVATED', maskedKey, robot_name, license.client_name,
                    `Универсальная лицензия активирована и зафиксирована за счетом ${maskedAccount}`, 'normal', { 
                        account: maskedAccount,
                        broker: broker,
                        ip 
                    });
                
                logger.info(`✅ License ${maskedKey} successfully activated for robot ${robot_name} on account ${maskedAccount}`);
                
                return {
                    success: true,
                    status: 'active',
                    message: 'License activated successfully',
                    expiry_date: expiryDate.toISOString(),
                    days_left: license.months * 30
                };
            }
            
            // ПРОВЕРКА ПРИВЯЗКИ (если лицензия уже активирована)
            // Проверяем ТОЛЬКО номер счета и название робота!
            
            // Проверка привязки к счету
            if (license.account_number && license.account_number !== account.toString()) {
                logger.error(`License theft attempt: ${maskedKey} from wrong account ${maskedAccount}`);
                await eventLogger.log('LICENSE_THEFT_ATTEMPT', maskedKey, robot_name, license.client_name,
                    'Попытка использовать лицензию с другого счета', 'critical', { 
                        expected_account: license.account_number.substring(0, 3) + '***',
                        actual_account: maskedAccount,
                        ip 
                    });
                
                return {
                    success: false,
                    error: 'WRONG_ACCOUNT',
                    message: 'License is registered to a different account'
                };
            }
            
            // Проверка привязки к роботу
            if (license.robot_name && robot_name && license.robot_name !== robot_name) {
                logger.error(`Robot mismatch: ${robot_name} vs ${license.robot_name}`);
                await eventLogger.log('ROBOT_MISMATCH', maskedKey, robot_name, license.client_name,
                    'Попытка использовать лицензию с другим роботом', 'high', { 
                        expected_robot: license.robot_name,
                        actual_robot: robot_name,
                        ip 
                    });
                
                return {
                    success: false,
                    error: 'WRONG_ROBOT',
                    message: 'License is registered to a different robot'
                };
            }
            
            // Лицензия валидна - обновляем данные для аналитики
            await db.run(`
                UPDATE licenses SET
                    last_check = datetime('now'),
                    last_ip = ?,
                    check_count = check_count + 1,
                    last_balance = ?,
                    terminal_version = COALESCE(?, terminal_version),
                    os_info = COALESCE(?, os_info),
                    account_owner = COALESCE(?, account_owner),
                    broker_name = COALESCE(?, broker_name),
                    account_type = COALESCE(?, account_type)
                WHERE license_key = ?
            `, [ip, balance, terminal_version || null, os_info || null, 
                account_owner || null, broker || null, account_type || null, key]);
            
            // Вычисляем дни до истечения
            let daysLeft = null;
            if (license.expiry_date) {
                const now = new Date();
                const expiry = new Date(license.expiry_date);
                daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
            }
            
            logger.info(`✅ License ${maskedKey} check successful. Days left: ${daysLeft}`);
            
            return {
                success: true,
                status: license.status,
                days_left: daysLeft
            };
            
        } catch (error) {
            logger.error('Activation error:', error);
            await eventLogger.log('ACTIVATION_ERROR', maskedKey, robot_name, '',
                'Ошибка при активации лицензии', 'high', { error: error.message, ip });
            
            return {
                success: false,
                error: 'INTERNAL_ERROR',
                message: 'Activation failed due to internal error'
            };
        }
    }
    
    /**
     * Проверка статуса лицензии
     */
    async check(data) {
        const key = data.key || data.license_key || data.Key;
        const account = data.account || data.AccountNumber || data.Account;
        const robot_name = data.robot_name || data.RobotName || 'FoxterAI';
        const balance = data.balance || data.Balance || 0;
        const ip = data.ip;
        
        if (!key || !account) {
            return {
                success: false,
                error: 'MISSING_PARAMETERS'
            };
        }
        
        const maskedKey = key.substring(0, 8) + '***';
        const maskedAccount = account.toString().substring(0, 3) + '***';
        
        try {
            const license = await db.get(
                'SELECT * FROM licenses WHERE license_key = ?',
                [key]
            );
            
            if (!license) {
                return {
                    success: false,
                    error: 'LICENSE_NOT_FOUND'
                };
            }
            
            // Проверка блокировки
            if (license.status === 'blocked') {
                return {
                    success: false,
                    error: 'LICENSE_BLOCKED'
                };
            }
            
            // Проверка истечения
            const now = new Date();
            const expiryDate = license.expiry_date ? new Date(license.expiry_date) : null;
            
            if (expiryDate && expiryDate < now) {
                await db.run(
                    "UPDATE licenses SET status = 'expired' WHERE license_key = ?",
                    [key]
                );
                
                return {
                    success: false,
                    error: 'LICENSE_EXPIRED'
                };
            }
            
            // Проверка привязки
            if (license.account_number && license.account_number !== account.toString()) {
                await eventLogger.log('CHECK_WRONG_ACCOUNT', maskedKey, robot_name, license.client_name,
                    'Проверка с чужого счета', 'high', { ip });
                
                return {
                    success: false,
                    error: 'WRONG_ACCOUNT'
                };
            }
            
            if (license.robot_name && license.robot_name !== robot_name) {
                await eventLogger.log('CHECK_WRONG_ROBOT', maskedKey, robot_name, license.client_name,
                    'Проверка с другим роботом', 'high', { ip });
                
                return {
                    success: false,
                    error: 'WRONG_ROBOT'
                };
            }
            
            // Обновляем статистику
            await db.run(`
                UPDATE licenses SET
                    last_check = datetime('now'),
                    last_ip = ?,
                    check_count = check_count + 1,
                    last_balance = ?,
                    failed_checks = 0
                WHERE license_key = ?
            `, [ip, balance, key]);
            
            // Логируем успешную проверку
            await db.run(`
                INSERT INTO checks (license_key, ip_address, account_number, robot_name, status, balance)
                VALUES (?, ?, ?, ?, 'success', ?)
            `, [key, ip, account.toString(), robot_name, balance]);
            
            const daysLeft = expiryDate ? Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24)) : null;
            
            return {
                success: true,
                status: 'active',
                days_left: daysLeft,
                next_check_hours: config.CHECK_INTERVAL_HOURS
            };
            
        } catch (error) {
            logger.error('Check error:', error);
            return {
                success: false,
                error: 'INTERNAL_ERROR'
            };
        }
    }
    
    /**
     * Heartbeat - ИСПРАВЛЕНО: сохранение equity и profit
     */
    async heartbeat(data) {
        const key = data.key || data.license_key || data.Key;
        const balance = data.balance || data.Balance || 0;
        const equity = data.equity || data.Equity || 0;  // ДОБАВЛЕНО
        const profit = data.profit || data.Profit || 0;  // ДОБАВЛЕНО
        const ip = data.ip;
        
        if (!key) {
            return { success: false };
        }
        
        try {
            // ИСПРАВЛЕНО: добавлено сохранение equity и profit
            await db.run(`
                UPDATE licenses SET 
                    last_check = datetime('now'),
                    last_ip = ?,
                    heartbeat_count = heartbeat_count + 1,
                    last_balance = ?,
                    last_equity = ?,
                    last_profit = ?
                WHERE license_key = ?
            `, [ip, balance, equity, profit, key]);
            
            return { success: true };
            
        } catch (error) {
            logger.error('Heartbeat error:', error);
            return { success: false };
        }
    }
    
    /**
     * Простая проверка существования ключа
     */
    async verifyKey(key) {
        try {
            const license = await db.get(
                'SELECT id FROM licenses WHERE license_key = ?',
                [key]
            );
            return !!license;
        } catch (error) {
            logger.error('Verify error:', error);
            return false;
        }
    }
}

module.exports = new ActivationService();