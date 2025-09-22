/**
 * FoxterAI_Server/middleware/encoding.js
 * ПОЛНЫЙ ИСПРАВЛЕННЫЙ ФАЙЛ
 * Middleware для исправления кодировки от MT4 терминалов
 */

const iconv = require('iconv-lite');
const logger = require('../utils/logger');

/**
 * Middleware для исправления проблем с кодировкой от MT4 клиентов
 */
function encodingMiddleware(req, res, next) {
    // Работаем только с POST запросами от MT4 клиентов
    if (req.method !== 'POST') {
        return next();
    }
    
    const userAgent = req.headers['user-agent'] || '';
    if (!userAgent.includes('FoxterAI')) {
        return next();
    }
    
    // Собираем сырые данные
    let rawData = Buffer.alloc(0);
    
    req.on('data', chunk => {
        rawData = Buffer.concat([rawData, chunk]);
    });
    
    req.on('end', () => {
        try {
            // Преобразуем буфер в строку
            let bodyString = rawData.toString('utf8');
            
            // Удаляем нулевые байты и управляющие символы
            bodyString = bodyString
                .replace(/\x00/g, '')  // Удаляем нулевые байты
                .replace(/[\x01-\x1F\x7F]/g, ''); // Удаляем управляющие символы
            
            // Обрезаем всё после последней закрывающей скобки
            const lastBrace = bodyString.lastIndexOf('}');
            if (lastBrace !== -1) {
                bodyString = bodyString.substring(0, lastBrace + 1);
            }
            
            // Пытаемся распарсить JSON
            try {
                const jsonData = JSON.parse(bodyString);
                
                // Транслитерируем кириллицу в полях
                if (jsonData.account_owner) {
                    jsonData.account_owner = transliterate(jsonData.account_owner);
                }
                if (jsonData.broker) {
                    jsonData.broker = transliterate(jsonData.broker);
                }
                
                req.body = jsonData;
                
                logger.debug('MT4 запрос успешно обработан', {
                    account: jsonData.account,
                    broker: jsonData.broker
                });
                
            } catch (parseError) {
                // Если не удалось распарсить, пытаемся восстановить данные
                logger.warn('Ошибка парсинга JSON от MT4, пытаемся восстановить', {
                    error: parseError.message,
                    body: bodyString.substring(0, 200)
                });
                
                // Извлекаем данные регулярками
                const keyMatch = bodyString.match(/"key":"([^"]+)"/);
                const accountMatch = bodyString.match(/"account":"(\d+)"/);
                
                if (keyMatch && accountMatch) {
                    req.body = {
                        key: keyMatch[1],
                        account: accountMatch[1],
                        account_owner: 'Unknown',
                        broker: 'Unknown',
                        account_type: 'Unknown',
                        balance: '0',
                        robot_name: 'FoxterAI',
                        robot_version: '1.6'
                    };
                    
                    logger.info('Данные восстановлены из поврежденного запроса');
                } else {
                    throw new Error('Не удалось извлечь ключевые данные');
                }
            }
            
            next();
            
        } catch (error) {
            logger.error('Критическая ошибка обработки MT4 запроса', {
                error: error.message,
                userAgent: userAgent
            });
            
            return res.status(400).json({
                success: false,
                error: 'INVALID_REQUEST',
                message: 'Не удалось обработать запрос от MT4'
            });
        }
    });
}

/**
 * Транслитерация кириллицы в латиницу
 */
function transliterate(text) {
    if (!text) return text;
    
    const map = {
        'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
        'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
        'Ё': 'E', 'ё': 'e', 'Ж': 'Zh', 'ж': 'zh', 'З': 'Z', 'з': 'z',
        'И': 'I', 'и': 'i', 'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k',
        'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
        'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
        'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u',
        'Ф': 'F', 'ф': 'f', 'Х': 'H', 'х': 'h', 'Ц': 'Ts', 'ц': 'ts',
        'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Sch', 'щ': 'sch',
        'Ъ': '', 'ъ': '', 'Ы': 'Y', 'ы': 'y', 'Ь': '', 'ь': '',
        'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya', 'я': 'ya'
    };
    
    return text.split('').map(char => map[char] || char).join('');
}

module.exports = encodingMiddleware;