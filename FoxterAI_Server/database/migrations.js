/**
 * FoxterAI_Server/database/migrations.js
 * Создание и обновление таблиц БД - РУССКАЯ ВЕРСИЯ
 */

const logger = require('../utils/logger');

const migrations = [
    // Таблица лицензий
    {
        name: 'создание_таблицы_лицензий',
        sql: `
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                
                -- Информация о клиенте
                client_name TEXT,
                client_contact TEXT,
                client_telegram TEXT,
                
                -- Информация о роботе
                robot_name TEXT,
                robot_version TEXT,
                
                -- Информация о счете
                account_number TEXT,
                account_owner TEXT,
                account_type TEXT DEFAULT 'Real',
                broker_name TEXT,
                
                -- Отпечаток и привязка
                fingerprint TEXT,
                fingerprint_hash TEXT,
                
                -- Даты
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                activation_date DATETIME,
                expiry_date DATETIME,
                months INTEGER DEFAULT 1,
                
                -- Статусы
                status TEXT DEFAULT 'created',
                
                -- Технические данные
                last_ip TEXT,
                activation_ip TEXT,
                last_check DATETIME,
                last_balance REAL DEFAULT 0,
                terminal_version TEXT,
                os_info TEXT,
                
                -- Счетчики
                check_count INTEGER DEFAULT 0,
                failed_checks INTEGER DEFAULT 0,
                heartbeat_count INTEGER DEFAULT 0,
                
                -- Дополнительно
                notes TEXT,
                
                -- Уникальный индекс
                UNIQUE(account_number, robot_name)
            )
        `
    },
    
    // Таблица проверок
    {
        name: 'создание_таблицы_проверок',
        sql: `
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT,
                check_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                account_number TEXT,
                broker_name TEXT,
                robot_name TEXT,
                robot_version TEXT,
                status TEXT,
                message TEXT,
                balance REAL
            )
        `
    },
    
    // Таблица событий
    {
        name: 'создание_таблицы_событий',
        sql: `
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                license_key TEXT,
                robot_name TEXT,
                client_name TEXT,
                description TEXT,
                priority TEXT DEFAULT 'normal',
                details TEXT,
                ip_address TEXT
            )
        `
    }
];

// Дополнительные изменения существующих таблиц
const alterations = [
    { table: 'licenses', column: 'robot_name', type: 'TEXT' },
    { table: 'licenses', column: 'account_type', type: 'TEXT DEFAULT "Real"' },
    { table: 'licenses', column: 'fingerprint_hash', type: 'TEXT' },
    { table: 'events', column: 'robot_name', type: 'TEXT' },
    { table: 'events', column: 'client_name', type: 'TEXT' },
    { table: 'events', column: 'priority', type: 'TEXT DEFAULT "normal"' },
    { table: 'events', column: 'details', type: 'TEXT' },
    { table: 'events', column: 'ip_address', type: 'TEXT' }
];

module.exports = {
    async run(db) {
        return new Promise((resolve, reject) => {
            db.serialize(() => {
                // Создаем таблицы
                for (const migration of migrations) {
                    db.run(migration.sql, (err) => {
                        if (err) {
                            logger.error(`Миграция ${migration.name} не удалась:`, err);
                        } else {
                            logger.info(`Миграция ${migration.name} выполнена`);
                        }
                    });
                }
                
                // Добавляем недостающие колонки
                for (const alt of alterations) {
                    const sql = `ALTER TABLE ${alt.table} ADD COLUMN ${alt.column} ${alt.type}`;
                    db.run(sql, (err) => {
                        // Игнорируем ошибку если колонка уже существует
                        if (!err) {
                            logger.info(`Добавлена колонка ${alt.column} в таблицу ${alt.table}`);
                        }
                    });
                }
                
                // Даем время на завершение всех операций
                setTimeout(resolve, 100);
            });
        });
    }
};