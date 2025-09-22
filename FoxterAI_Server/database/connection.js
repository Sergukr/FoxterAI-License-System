/**
 * FoxterAI_Server/database/connection.js
 * Подключение к базе данных - РУССКАЯ ВЕРСИЯ
 */

const sqlite3 = require('sqlite3').verbose();
const config = require('../config/config');
const logger = require('../utils/logger');

class Database {
    constructor() {
        this.db = null;
        this._isConnected = false;
    }
    
    async initialize() {
        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(config.DATABASE.filename, (err) => {
                if (err) {
                    logger.error('Не удалось подключиться к базе данных:', err);
                    reject(err);
                    return;
                }
                
                this._isConnected = true;
                logger.info('База данных успешно подключена');
                
                // Запускаем миграции
                const migrations = require('./migrations');
                migrations.run(this.db)
                    .then(() => {
                        logger.info('Миграции базы данных завершены');
                        resolve();
                    })
                    .catch(err => {
                        logger.error('Ошибка миграции:', err);
                        // НЕ отклоняем промис - продолжаем работу даже если миграции не прошли
                        resolve();
                    });
            });
        });
    }
    
    isConnected() {
        return this._isConnected;
    }
    
    get() {
        if (!this.db) {
            throw new Error('База данных не инициализирована');
        }
        return this.db;
    }
    
    async close() {
        return new Promise((resolve) => {
            if (!this.db) {
                resolve();
                return;
            }
            
            this.db.close((err) => {
                if (err) {
                    logger.error('Ошибка при закрытии базы данных:', err);
                }
                this._isConnected = false;
                logger.info('Соединение с базой данных закрыто');
                resolve();
            });
        });
    }
    
    // Обертка для безопасного выполнения run
    async run(sql, params = []) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('База данных не подключена'));
                return;
            }
            
            this.db.run(sql, params, function(err) {
                if (err) {
                    logger.error(`Ошибка SQL: ${err.message}`, { sql: sql.substring(0, 100) });
                    reject(err);
                    return;
                }
                resolve({ id: this.lastID, changes: this.changes });
            });
        });
    }
    
    // Обертка для безопасного выполнения get
    async get(sql, params = []) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('База данных не подключена'));
                return;
            }
            
            this.db.get(sql, params, (err, row) => {
                if (err) {
                    logger.error(`Ошибка SQL: ${err.message}`, { sql: sql.substring(0, 100) });
                    reject(err);
                    return;
                }
                resolve(row);
            });
        });
    }
    
    // Обертка для безопасного выполнения all
    async all(sql, params = []) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('База данных не подключена'));
                return;
            }
            
            this.db.all(sql, params, (err, rows) => {
                if (err) {
                    logger.error(`Ошибка SQL: ${err.message}`, { sql: sql.substring(0, 100) });
                    reject(err);
                    return;
                }
                resolve(rows || []);
            });
        });
    }
}

module.exports = new Database();