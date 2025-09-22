/**
 * FoxterAI Сервер Лицензий v4.0 - РУССКАЯ ВЕРСИЯ
 * ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Server/server.js
 * Модульная архитектура с защитой от падений
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const rateLimit = require('express-rate-limit');
const fs = require('fs');

// Импорт модулей
const config = require('./config/config');
const database = require('./database/connection');
const logger = require('./utils/logger');

// =====================
// ГЛОБАЛЬНАЯ ЗАЩИТА ОТ ПАДЕНИЙ
// =====================
process.on('uncaughtException', (error) => {
    logger.error(`НЕОБРАБОТАННОЕ ИСКЛЮЧЕНИЕ: ${error.message}`, { stack: error.stack });
    // НЕ завершаем процесс - сервер продолжает работать
});

process.on('unhandledRejection', (reason, promise) => {
    logger.error(`НЕОБРАБОТАННЫЙ ОТКАЗ: ${reason}`, { promise });
    // НЕ завершаем процесс - сервер продолжает работать
});

// Создание приложения Express
const app = express();

// =====================
// СОЗДАНИЕ НЕОБХОДИМЫХ ПАПОК
// =====================
const publicDir = path.join(__dirname, 'public');
if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
    logger.info('Создана папка public');
}

// Создание простого favicon.ico если его нет
const faviconPath = path.join(publicDir, 'favicon.ico');
if (!fs.existsSync(faviconPath)) {
    // Создаем минимальный валидный ICO файл (1x1 прозрачный пиксель)
    const icoData = Buffer.from([
        0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x18, 0x00,
        0x30, 0x00, 0x00, 0x00, 0x16, 0x00, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x01, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00
    ]);
    fs.writeFileSync(faviconPath, icoData);
    logger.info('Создан файл favicon.ico');
}

// =====================
// MIDDLEWARE
// =====================

// Безопасность
app.use(helmet({
    contentSecurityPolicy: false,
}));

// CORS - разрешаем запросы от всех источников
const corsOptions = {
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key']
};
app.use(cors(corsOptions));

// Rate limiting для API
const limiter = rateLimit({
    windowMs: config.RATE_LIMIT.windowMs || 900000, // 15 минут
    max: config.RATE_LIMIT.max || 100,
    message: 'Слишком много запросов с этого IP',
    standardHeaders: true,
    legacyHeaders: false,
});
app.use('/api/', limiter);

// Логирование запросов
app.use(morgan('combined', {
    stream: {
        write: (message) => logger.info(message.trim())
    },
    skip: (req, res) => req.url === '/favicon.ico' // Пропускаем логирование favicon
}));

// =====================
// ВАЖНО: СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ MT4
// =====================

// Кастомные middleware
const encodingMiddleware = require('./middleware/encoding');
const errorHandler = require('./middleware/errorHandler');

// Применяем middleware для исправления кодировки ОТ MT4 КЛИЕНТОВ
app.use(encodingMiddleware);

// Парсинг JSON только для обычных клиентов (не MT4)
app.use((req, res, next) => {
    // Если тело уже обработано MT4 middleware - пропускаем
    if (req.body && Object.keys(req.body).length > 0) {
        return next();
    }
    
    // Для обычных клиентов используем стандартный парсер
    express.json({ 
        limit: '10mb',
        verify: (req, res, buf) => {
            req.rawBody = buf.toString('utf8');
        }
    })(req, res, next);
});

app.use(express.urlencoded({ extended: true }));

// Статические файлы
app.use(express.static(publicDir));

// Специальная обработка для favicon.ico
app.get('/favicon.ico', (req, res) => {
    res.sendFile(faviconPath);
});

// =====================
// МАРШРУТЫ
// =====================

// Корневой маршрут - информация о сервере
app.get('/', (req, res) => {
    res.json({
        название: 'FoxterAI Сервер Лицензий',
        версия: '4.0.0',
        статус: 'работает',
        время_работы: process.uptime(),
        время: new Date().toISOString()
    });
});

// Проверка здоровья сервера
app.get('/health', (req, res) => {
    res.json({ 
        статус: 'здоров',
        база_данных: database.isConnected() ? 'подключена' : 'отключена',
        время_работы: process.uptime()
    });
});

// Версия API
app.get('/api/version', (req, res) => {
    res.json({
        версия: '4.0.0',
        версия_api: '2.0',
        функции: [
            'универсальные_лицензии',
            'отпечатки',
            'автономный_режим',
            'логирование_событий',
            'ограничение_запросов'
        ]
    });
});

// Статус сервера
app.get('/api/status', (req, res) => {
    res.json({
        статус: 'работает',
        база_данных: database.isConnected() ? 'подключена' : 'отключена',
        время_работы: process.uptime(),
        память: process.memoryUsage(),
        время: new Date().toISOString()
    });
});

// Подключение маршрутов
try {
    // Публичные маршруты (для роботов MT4)
    const activationRoutes = require('./routes/activation');
    app.use('/', activationRoutes); // /activate, /check, /heartbeat
    
    // API маршруты (требуют авторизации)
    const licensesRoutes = require('./routes/licenses');
    const statisticsRoutes = require('./routes/statistics');
    const adminRoutes = require('./routes/admin');
    
    app.use('/api/licenses', licensesRoutes);
    app.use('/api/statistics', statisticsRoutes);
    app.use('/api/admin', adminRoutes);
    
    // Дополнительные API маршруты
    const apiRoutes = require('./routes/api');
    app.use('/api', apiRoutes);
    
} catch (error) {
    logger.error('Не удалось загрузить маршруты:', error);
    // Продолжаем работу даже если не все маршруты загрузились
}

// 404 обработчик для несуществующих маршрутов
app.use((req, res, next) => {
    // Игнорируем favicon.ico если он все еще вызывает 404
    if (req.url === '/favicon.ico') {
        return res.status(204).end();
    }
    
    const error = new Error(`Не найдено - ${req.originalUrl}`);
    error.status = 404;
    error.code = 'NOT_FOUND';
    next(error);
});

// =====================
// ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК (должен быть последним)
// =====================
app.use(errorHandler);

// =====================
// ИНИЦИАЛИЗАЦИЯ И ЗАПУСК СЕРВЕРА
// =====================

async function startServer() {
    try {
        // Подключаемся к базе данных
        await database.initialize();
        logger.info('База данных успешно инициализирована');
        
        // Запускаем HTTP сервер
        const server = app.listen(config.PORT, '0.0.0.0', () => {
            const port = server.address().port;
            
            console.log('\n╔════════════════════════════════════════════════╗');
            console.log('║     FoxterAI Сервер Лицензий v4.0             ║');
            console.log('║       МОДУЛЬНАЯ АРХИТЕКТУРА                   ║');
            console.log('╠════════════════════════════════════════════════╣');
            console.log('║  Статус: ✅ РАБОТАЕТ                          ║');
            console.log(`║  Порт: ${port}${' '.repeat(41 - port.toString().length)}║`);
            console.log(`║  Окружение: ${config.NODE_ENV === 'production' ? 'продакшен' : 'разработка'}${' '.repeat(27)}║`);
            console.log('║  База данных: ✅ Подключена                   ║');
            console.log(`║  API ключ: ${config.API_KEY ? config.API_KEY.substring(0, 10) + '...' : 'Не установлен'}${' '.repeat(24)}║`);
            console.log('║                                                ║');
            console.log('║  Возможности:                                  ║');
            console.log(`║  - Интервал проверок: ${config.CHECK_INTERVAL_HOURS} часов${' '.repeat(18)}║`);
            console.log(`║  - Период автономности: ${config.AUTONOMY_HOURS} часов${' '.repeat(15)}║`);
            console.log('║  - Защита от падений: ✅                       ║');
            console.log('║  - Ограничение запросов: ✅                    ║');
            console.log('║  - Логирование событий: ✅                     ║');
            console.log('║                                                ║');
            console.log('║  Эндпоинты:                                    ║');
            console.log(`║  - http://localhost:${port}/                    ║`);
            console.log(`║  - http://localhost:${port}/health              ║`);
            console.log(`║  - http://localhost:${port}/api/version         ║`);
            console.log(`║  - http://localhost:${port}/api/status          ║`);
            console.log('╚════════════════════════════════════════════════╝');
            
            logger.info('Сервер успешно запущен');
        });
        
        // Graceful shutdown
        process.on('SIGTERM', async () => {
            logger.info('SIGTERM получен, начинаем плавное завершение...');
            
            server.close(() => {
                logger.info('HTTP сервер закрыт');
            });
            
            await database.close();
            logger.info('Соединение с базой данных закрыто');
            
            process.exit(0);
        });
        
        process.on('SIGINT', async () => {
            logger.info('SIGINT получен (Ctrl+C), начинаем плавное завершение...');
            
            server.close(() => {
                logger.info('HTTP сервер закрыт');
            });
            
            await database.close();
            logger.info('Соединение с базой данных закрыто');
            
            process.exit(0);
        });
        
    } catch (error) {
        logger.error('Критическая ошибка при запуске сервера:', error);
        process.exit(1);
    }
}

// =====================
// ЗАПУСК
// =====================
startServer().catch(error => {
    logger.error('Не удалось запустить сервер:', error);
    process.exit(1);
});