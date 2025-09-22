/**
 * FoxterAI_Server/utils/logger.js
 * Система логирования на русском языке
 */

const fs = require('fs');
const path = require('path');
const config = require('../config/config');

class Logger {
    constructor() {
        this.logDir = config.LOG_DIR;
        this.ensureLogDirectory();
        
        // Уровни логирования на русском
        this.levels = {
            'INFO': 'ИНФО',
            'WARN': 'ПРЕДУПРЕЖДЕНИЕ',
            'ERROR': 'ОШИБКА',
            'DEBUG': 'ОТЛАДКА'
        };
    }
    
    ensureLogDirectory() {
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }
    }
    
    getLogFile() {
        const date = new Date().toISOString().split('T')[0];
        return path.join(this.logDir, `server-${date}.log`);
    }
    
    write(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const russianLevel = this.levels[level] || level;
        
        const logEntry = {
            время: timestamp,
            уровень: russianLevel,
            сообщение: message,
            данные: data
        };
        
        // Консоль
        const consoleMsg = `[${timestamp}] [${russianLevel}] ${message}`;
        
        switch(level) {
            case 'ERROR':
                console.error(consoleMsg, data || '');
                break;
            case 'WARN':
                console.warn(consoleMsg, data || '');
                break;
            default:
                console.log(consoleMsg, data || '');
        }
        
        // Файл
        try {
            const logFile = this.getLogFile();
            const fileEntry = JSON.stringify(logEntry, null, 2) + '\n---\n';
            fs.appendFileSync(logFile, fileEntry);
        } catch (err) {
            console.error('Не удалось записать в файл логов:', err);
        }
    }
    
    info(message, data) {
        this.write('INFO', message, data);
    }
    
    warn(message, data) {
        this.write('WARN', message, data);
    }
    
    error(message, data) {
        this.write('ERROR', message, data);
    }
    
    debug(message, data) {
        if (config.LOG_LEVEL === 'debug') {
            this.write('DEBUG', message, data);
        }
    }
}

module.exports = new Logger();