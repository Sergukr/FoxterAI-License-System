/**
 * FoxterAI_Server/database/create_fresh_db.js
 * Создание новой базы данных с правильной структурой
 * Включает поля equity и profit
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Путь к базе данных
const dbPath = path.join(__dirname, '../licenses.db');
const backupPath = path.join(__dirname, '../licenses_backup.db');

console.log('🔨 Создание новой базы данных FoxterAI...\n');

// Делаем бэкап если БД существует
if (fs.existsSync(dbPath)) {
    console.log('⚠️  Найдена существующая БД');
    console.log(`📦 Создаю бэкап: ${backupPath}`);
    
    try {
        fs.copyFileSync(dbPath, backupPath);
        console.log('✅ Бэкап создан\n');
        
        // Удаляем старую БД
        fs.unlinkSync(dbPath);
        console.log('🗑️  Старая БД удалена\n');
    } catch (err) {
        console.error('❌ Ошибка при создании бэкапа:', err);
        process.exit(1);
    }
}

// Создаем новую БД
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('❌ Не удалось создать БД:', err);
        process.exit(1);
    }
    console.log('✅ Новая БД создана');
});

// SQL для создания таблиц с правильной структурой
const createTables = [
    {
        name: 'licenses',
        sql: `
            CREATE TABLE licenses (
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
                
                -- Финансовые показатели (НОВЫЕ ПОЛЯ)
                last_balance REAL DEFAULT 0,
                last_equity REAL DEFAULT 0,
                last_profit REAL DEFAULT 0,
                
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
                terminal_version TEXT,
                os_info TEXT,
                
                -- Счетчики
                check_count INTEGER DEFAULT 0,
                failed_checks INTEGER DEFAULT 0,
                heartbeat_count INTEGER DEFAULT 0,
                
                -- Дополнительно
                notes TEXT
            )
        `
    },
    {
        name: 'checks',
        sql: `
            CREATE TABLE checks (
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
                balance REAL,
                equity REAL,
                profit REAL
            )
        `
    },
    {
        name: 'events',
        sql: `
            CREATE TABLE events (
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

// Создаем индексы для оптимизации
const createIndexes = [
    'CREATE INDEX idx_licenses_status ON licenses(status)',
    'CREATE INDEX idx_licenses_robot ON licenses(robot_name)',
    'CREATE INDEX idx_licenses_account ON licenses(account_number)',
    'CREATE INDEX idx_checks_date ON checks(check_date)',
    'CREATE INDEX idx_checks_key ON checks(license_key)',
    'CREATE INDEX idx_events_date ON events(event_date)',
    'CREATE INDEX idx_events_type ON events(event_type)'
];

// Выполняем создание таблиц
db.serialize(() => {
    console.log('\n📋 Создание таблиц:');
    
    // Создаем таблицы
    for (const table of createTables) {
        db.run(table.sql, (err) => {
            if (err) {
                console.error(`❌ Ошибка создания таблицы ${table.name}:`, err);
                process.exit(1);
            } else {
                console.log(`  ✅ Таблица ${table.name} создана`);
            }
        });
    }
    
    // Создаем индексы
    console.log('\n🚀 Создание индексов:');
    for (const indexSql of createIndexes) {
        db.run(indexSql, (err) => {
            if (!err) {
                const indexName = indexSql.match(/INDEX (\w+)/)[1];
                console.log(`  ✅ Индекс ${indexName} создан`);
            }
        });
    }
    
    // Проверяем структуру
    setTimeout(() => {
        console.log('\n📊 Проверка структуры таблицы licenses:');
        db.all("PRAGMA table_info(licenses)", (err, rows) => {
            if (!err) {
                const importantColumns = rows.filter(r => 
                    r.name.includes('balance') || 
                    r.name.includes('equity') || 
                    r.name.includes('profit') ||
                    r.name.includes('account') ||
                    r.name.includes('robot')
                );
                
                console.log('\n  Ключевые поля:');
                importantColumns.forEach(col => {
                    console.log(`    • ${col.name}: ${col.type}`);
                });
            }
            
            // Закрываем БД
            db.close((err) => {
                if (err) {
                    console.error('\n❌ Ошибка закрытия БД:', err);
                } else {
                    console.log('\n✨ База данных успешно создана!');
                    console.log('📁 Файл: licenses.db');
                    
                    if (fs.existsSync(backupPath)) {
                        console.log(`📦 Бэкап старой БД: ${backupPath}`);
                        console.log('   (можете удалить после проверки)');
                    }
                    
                    console.log('\n🚀 Теперь можно запускать сервер!');
                }
            });
        });
    }, 500);
});