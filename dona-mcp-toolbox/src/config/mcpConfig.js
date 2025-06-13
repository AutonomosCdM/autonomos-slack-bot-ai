const path = require('path');
require('dotenv').config();

/**
 * Configuration management for MCP modules
 */
class MCPConfig {
    constructor() {
        this.config = {
            // ArXiv MCP Configuration
            arxiv: {
                baseUrl: 'http://export.arxiv.org/api/query',
                maxResults: 10,
                timeout: 30000
            },

            // GitHub MCP Configuration
            github: {
                token: process.env.GITHUB_TOKEN,
                baseUrl: 'https://api.github.com',
                timeout: 15000
            },

            // Weather MCP Configuration
            weather: {
                apiKey: process.env.WEATHER_API_KEY,
                baseUrl: 'https://api.openweathermap.org/data/2.5',
                timeout: 10000
            },

            // Puppeteer MCP Configuration
            puppeteer: {
                headless: true,
                timeout: 30000,
                viewport: {
                    width: 1920,
                    height: 1080
                },
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },

            // General Configuration
            general: {
                logLevel: process.env.LOG_LEVEL || 'info',
                maxRetries: 3,
                retryDelay: 1000,
                cacheEnabled: true,
                cacheTTL: 300000 // 5 minutes
            }
        };
    }

    /**
     * Get configuration for a specific MCP
     * @param {string} mcpName - Name of the MCP
     * @returns {Object} Configuration object
     */
    getMCPConfig(mcpName) {
        return this.config[mcpName] || {};
    }

    /**
     * Update configuration for a specific MCP
     * @param {string} mcpName - Name of the MCP
     * @param {Object} newConfig - New configuration values
     */
    updateMCPConfig(mcpName, newConfig) {
        if (this.config[mcpName]) {
            this.config[mcpName] = { ...this.config[mcpName], ...newConfig };
        } else {
            this.config[mcpName] = newConfig;
        }
    }

    /**
     * Get all configuration
     * @returns {Object} Complete configuration object
     */
    getAllConfig() {
        return this.config;
    }

    /**
     * Validate required environment variables
     * @returns {Object} Validation results
     */
    validateConfig() {
        const validation = {
            valid: true,
            missing: [],
            warnings: []
        };

        // Check GitHub token
        if (!this.config.github.token) {
            validation.warnings.push('GITHUB_TOKEN not set - GitHub MCP will have limited functionality');
        }

        // Check Weather API key
        if (!this.config.weather.apiKey) {
            validation.warnings.push('WEATHER_API_KEY not set - Weather MCP will not function');
        }

        return validation;
    }
}

module.exports = new MCPConfig();