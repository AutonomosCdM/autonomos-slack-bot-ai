const ArxivMCP = require('./mcps/ArxivMCP');
const logger = require('./utils/logger').createModuleLogger('DonaMCP');
const mcpConfig = require('./config/mcpConfig');

/**
 * DonaMCP - Main orchestrator class for all MCP capabilities
 * Provides unified interface to access various MCP modules
 */
class DonaMCP {
    constructor() {
        this.mcps = {};
        this.initialized = false;
        this.startTime = Date.now();
        
        logger.info('DonaMCP instance created');
    }

    /**
     * Initialize all MCP modules and their dependencies
     * @returns {Promise<boolean>} Success status
     */
    async initialize() {
        try {
            logger.info('Initializing DonaMCP and all MCP modules...');
            
            // Validate configuration
            const configValidation = mcpConfig.validateConfig();
            if (configValidation.warnings.length > 0) {
                configValidation.warnings.forEach(warning => {
                    logger.warn(`Configuration warning: ${warning}`);
                });
            }

            // Initialize ArXiv MCP
            this.mcps.arxiv = new ArxivMCP();
            logger.info('ArXiv MCP initialized successfully');

            // TODO: Initialize other MCPs when implemented
            // this.mcps.puppeteer = new PuppeteerMCP();
            // this.mcps.github = new GitHubMCP();
            // this.mcps.weather = new WeatherMCP();

            this.initialized = true;
            
            const initTime = Date.now() - this.startTime;
            logger.info(`DonaMCP initialization completed in ${initTime}ms`, {
                modules: Object.keys(this.mcps),
                initTime
            });

            return true;

        } catch (error) {
            logger.error(`Failed to initialize DonaMCP: ${error.message}`, {
                error: error.stack
            });
            throw new Error(`DonaMCP initialization failed: ${error.message}`);
        }
    }

    /**
     * Get list of all available MCP capabilities
     * @returns {Object} Available capabilities by MCP
     */
    getAvailableCapabilities() {
        if (!this.initialized) {
            throw new Error('DonaMCP not initialized. Call initialize() first.');
        }

        const capabilities = {
            arxiv: [
                'searchPapers',
                'getPaperDetails', 
                'downloadPaper',
                'getCategories',
                'getRecentPapers'
            ]
            // TODO: Add other MCP capabilities when implemented
        };

        logger.debug('Returning available capabilities', { capabilities });
        return capabilities;
    }

    /**
     * Execute a specific MCP method with given parameters
     * @param {string} mcpName - Name of the MCP (e.g., 'arxiv')
     * @param {string} method - Method name to execute
     * @param {...any} params - Parameters to pass to the method
     * @returns {Promise<any>} Result from the MCP method
     */
    async executeCapability(mcpName, method, ...params) {
        if (!this.initialized) {
            throw new Error('DonaMCP not initialized. Call initialize() first.');
        }

        const startTime = Date.now();
        
        try {
            logger.info(`Executing ${mcpName}.${method}`, { 
                params: params.length > 0 ? JSON.stringify(params) : 'none'
            });

            const mcp = this.mcps[mcpName];
            if (!mcp) {
                throw new Error(`MCP '${mcpName}' not found or not initialized`);
            }

            if (typeof mcp[method] !== 'function') {
                throw new Error(`Method '${method}' not found in MCP '${mcpName}'`);
            }

            const result = await mcp[method](...params);
            
            const duration = Date.now() - startTime;
            logger.info(`Successfully executed ${mcpName}.${method}`, { 
                duration: `${duration}ms`
            });

            return result;

        } catch (error) {
            const duration = Date.now() - startTime;
            logger.error(`Failed to execute ${mcpName}.${method}: ${error.message}`, {
                duration: `${duration}ms`,
                error: error.stack
            });
            throw error;
        }
    }

    /**
     * Get direct access to ArXiv MCP instance
     * @returns {ArxivMCP} ArXiv MCP instance
     */
    getArxivMCP() {
        if (!this.initialized) {
            throw new Error('DonaMCP not initialized. Call initialize() first.');
        }
        return this.mcps.arxiv;
    }

    /**
     * High-level method for research paper searches
     * @param {string} query - Search query
     * @param {number} maxResults - Maximum number of results
     * @param {string} category - Optional category filter
     * @returns {Promise<Array>} Array of papers
     */
    async searchResearchPapers(query, maxResults = 10, category = null) {
        return await this.executeCapability('arxiv', 'searchPapers', query, maxResults, category);
    }

    /**
     * Get system status and statistics
     * @returns {Object} System status information
     */
    getSystemStatus() {
        const uptime = Date.now() - this.startTime;
        
        const status = {
            initialized: this.initialized,
            uptime: `${Math.floor(uptime / 1000)}s`,
            uptimeMs: uptime,
            availableMCPs: Object.keys(this.mcps),
            mcpCount: Object.keys(this.mcps).length
        };

        // Add MCP-specific stats if available
        if (this.mcps.arxiv) {
            status.arxivCache = this.mcps.arxiv.getCacheStats();
        }

        return status;
    }

    /**
     * Health check for all MCP modules
     * @returns {Promise<Object>} Health status of all modules
     */
    async healthCheck() {
        if (!this.initialized) {
            return { healthy: false, error: 'Not initialized' };
        }

        const health = {
            healthy: true,
            timestamp: new Date().toISOString(),
            modules: {}
        };

        try {
            // Test ArXiv MCP
            if (this.mcps.arxiv) {
                const categories = this.mcps.arxiv.getCategories();
                health.modules.arxiv = {
                    healthy: Object.keys(categories).length > 0,
                    categories: Object.keys(categories).length
                };
            }

            // TODO: Add health checks for other MCPs when implemented

            logger.info('Health check completed', { health });
            return health;

        } catch (error) {
            health.healthy = false;
            health.error = error.message;
            logger.error(`Health check failed: ${error.message}`);
            return health;
        }
    }

    /**
     * Cleanup and dispose of all MCP resources
     * @returns {Promise<void>}
     */
    async dispose() {
        try {
            logger.info('Disposing DonaMCP and cleaning up resources...');

            // Clear caches
            if (this.mcps.arxiv) {
                this.mcps.arxiv.clearCache();
            }

            // TODO: Cleanup other MCPs when implemented
            // if (this.mcps.puppeteer) {
            //     await this.mcps.puppeteer.close();
            // }

            this.mcps = {};
            this.initialized = false;

            const totalUptime = Date.now() - this.startTime;
            logger.info(`DonaMCP disposed successfully after ${Math.floor(totalUptime / 1000)}s uptime`);

        } catch (error) {
            logger.error(`Error during disposal: ${error.message}`, {
                error: error.stack
            });
            throw error;
        }
    }

    /**
     * Get configuration for all or specific MCP
     * @param {string} mcpName - Optional MCP name to get specific config
     * @returns {Object} Configuration object
     */
    getConfiguration(mcpName = null) {
        if (mcpName) {
            return mcpConfig.getMCPConfig(mcpName);
        }
        return mcpConfig.getAllConfig();
    }

    /**
     * Update configuration for a specific MCP
     * @param {string} mcpName - Name of the MCP
     * @param {Object} newConfig - New configuration values
     */
    updateConfiguration(mcpName, newConfig) {
        mcpConfig.updateMCPConfig(mcpName, newConfig);
        logger.info(`Configuration updated for ${mcpName}`, { newConfig });
    }
}

module.exports = DonaMCP;