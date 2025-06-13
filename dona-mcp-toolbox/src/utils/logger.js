const winston = require('winston');
const mcpConfig = require('../config/mcpConfig');

/**
 * Centralized logging utility for MCP modules
 */
class Logger {
    constructor() {
        const logLevel = mcpConfig.getMCPConfig('general').logLevel;
        
        this.logger = winston.createLogger({
            level: logLevel,
            format: winston.format.combine(
                winston.format.timestamp({
                    format: 'YYYY-MM-DD HH:mm:ss'
                }),
                winston.format.errors({ stack: true }),
                winston.format.printf(({ level, message, timestamp, stack, module }) => {
                    const modulePrefix = module ? `[${module}] ` : '';
                    const logMessage = `${timestamp} ${level.toUpperCase()}: ${modulePrefix}${message}`;
                    return stack ? `${logMessage}\n${stack}` : logMessage;
                })
            ),
            transports: [
                new winston.transports.Console({
                    format: winston.format.combine(
                        winston.format.colorize(),
                        winston.format.simple()
                    )
                }),
                new winston.transports.File({
                    filename: 'logs/error.log',
                    level: 'error',
                    maxsize: 5242880, // 5MB
                    maxFiles: 5
                }),
                new winston.transports.File({
                    filename: 'logs/combined.log',
                    maxsize: 5242880, // 5MB
                    maxFiles: 5
                })
            ]
        });
    }

    /**
     * Create a module-specific logger
     * @param {string} moduleName - Name of the module
     * @returns {Object} Logger with module context
     */
    createModuleLogger(moduleName) {
        return {
            info: (message, meta = {}) => this.logger.info(message, { module: moduleName, ...meta }),
            warn: (message, meta = {}) => this.logger.warn(message, { module: moduleName, ...meta }),
            error: (message, meta = {}) => this.logger.error(message, { module: moduleName, ...meta }),
            debug: (message, meta = {}) => this.logger.debug(message, { module: moduleName, ...meta })
        };
    }

    /**
     * Log MCP operation start
     * @param {string} mcpName - Name of the MCP
     * @param {string} operation - Operation being performed
     * @param {Object} params - Operation parameters
     */
    logMCPOperation(mcpName, operation, params = {}) {
        this.logger.info(`MCP Operation Started`, {
            module: mcpName,
            operation,
            params: JSON.stringify(params, null, 2)
        });
    }

    /**
     * Log MCP operation completion
     * @param {string} mcpName - Name of the MCP
     * @param {string} operation - Operation that was performed
     * @param {boolean} success - Whether operation was successful
     * @param {number} duration - Operation duration in ms
     */
    logMCPResult(mcpName, operation, success, duration) {
        const level = success ? 'info' : 'error';
        const status = success ? 'Completed' : 'Failed';
        
        this.logger[level](`MCP Operation ${status}`, {
            module: mcpName,
            operation,
            success,
            duration: `${duration}ms`
        });
    }

    /**
     * Get the underlying Winston logger
     * @returns {winston.Logger} Winston logger instance
     */
    getLogger() {
        return this.logger;
    }
}

module.exports = new Logger();