const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const logger = require('../utils/logger').createModuleLogger('PuppeteerMCP');
const mcpConfig = require('../config/mcpConfig');

/**
 * Puppeteer MCP - Advanced web scraping and browser automation
 * Provides headless browser capabilities for complex web interactions
 */
class PuppeteerMCP {
    constructor() {
        this.config = mcpConfig.getMCPConfig('puppeteer');
        this.browser = null;
        this.activeSessions = new Map();
        this.initialized = false;
    }

    /**
     * Initialize Puppeteer browser instance
     * @returns {Promise<boolean>} Success status
     */
    async initialize() {
        try {
            logger.info('Initializing Puppeteer browser...');
            
            this.browser = await puppeteer.launch({
                headless: this.config.headless,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            });

            this.initialized = true;
            logger.info('Puppeteer browser initialized successfully');
            return true;

        } catch (error) {
            logger.error(`Failed to initialize Puppeteer: ${error.message}`);
            throw new Error(`Puppeteer initialization failed: ${error.message}`);
        }
    }

    /**
     * Create a new browser page session
     * @param {Object} options - Page configuration options
     * @returns {Promise<string>} Session ID
     */
    async createSession(options = {}) {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            const page = await this.browser.newPage();

            // Configure page
            await page.setViewport(this.config.viewport);
            await page.setUserAgent(this.config.userAgent);

            // Set additional options
            if (options.timeout) {
                page.setDefaultTimeout(options.timeout);
            }

            if (options.blockResources) {
                await page.setRequestInterception(true);
                page.on('request', (req) => {
                    const resourceType = req.resourceType();
                    if (options.blockResources.includes(resourceType)) {
                        req.abort();
                    } else {
                        req.continue();
                    }
                });
            }

            this.activeSessions.set(sessionId, {
                page,
                created: Date.now(),
                lastUsed: Date.now()
            });

            logger.info(`Created new Puppeteer session: ${sessionId}`);
            return sessionId;

        } catch (error) {
            logger.error(`Error creating session: ${error.message}`);
            throw new Error(`Session creation failed: ${error.message}`);
        }
    }

    /**
     * Navigate to a URL and extract content
     * @param {string} url - Target URL
     * @param {Object} options - Scraping options
     * @returns {Promise<Object>} Scraped content and metadata
     */
    async scrapeUrl(url, options = {}) {
        const startTime = Date.now();
        let sessionId = options.sessionId;

        try {
            // Create session if not provided
            if (!sessionId) {
                sessionId = await this.createSession(options);
            }

            const session = this.activeSessions.get(sessionId);
            if (!session) {
                throw new Error(`Session ${sessionId} not found`);
            }

            const { page } = session;
            session.lastUsed = Date.now();

            logger.info(`Scraping URL: ${url}`, { sessionId });

            // Navigate to URL
            const response = await page.goto(url, {
                waitUntil: options.waitUntil || 'networkidle2',
                timeout: options.timeout || this.config.timeout
            });

            // Wait for additional conditions if specified
            if (options.waitForSelector) {
                await page.waitForSelector(options.waitForSelector, {
                    timeout: options.selectorTimeout || 5000
                });
            }

            if (options.waitForFunction) {
                await page.waitForFunction(options.waitForFunction, {
                    timeout: options.functionTimeout || 5000
                });
            }

            // Extract content based on options
            const content = await this._extractContent(page, options);
            
            // Get page metadata
            const metadata = await this._getPageMetadata(page, response);

            const result = {
                url,
                success: true,
                content,
                metadata,
                scrapingTime: Date.now() - startTime,
                sessionId
            };

            logger.info(`Successfully scraped ${url}`, {
                contentLength: JSON.stringify(content).length,
                duration: result.scrapingTime
            });

            // Auto-close session if not persistent
            if (!options.persistent) {
                await this.closeSession(sessionId);
            }

            return result;

        } catch (error) {
            logger.error(`Error scraping ${url}: ${error.message}`, {
                error: error.stack,
                sessionId
            });

            // Cleanup on error
            if (sessionId && !options.persistent) {
                await this.closeSession(sessionId).catch(() => {});
            }

            throw new Error(`Scraping failed: ${error.message}`);
        }
    }

    /**
     * Execute custom JavaScript on a page
     * @param {string} sessionId - Session ID
     * @param {string} script - JavaScript code to execute
     * @param {Array} args - Arguments to pass to the script
     * @returns {Promise<any>} Script execution result
     */
    async executeScript(sessionId, script, args = []) {
        try {
            const session = this.activeSessions.get(sessionId);
            if (!session) {
                throw new Error(`Session ${sessionId} not found`);
            }

            const { page } = session;
            session.lastUsed = Date.now();

            logger.info(`Executing script in session ${sessionId}`);

            const result = await page.evaluate(script, ...args);
            
            logger.info(`Script executed successfully in session ${sessionId}`);
            return result;

        } catch (error) {
            logger.error(`Error executing script: ${error.message}`, { sessionId });
            throw new Error(`Script execution failed: ${error.message}`);
        }
    }

    /**
     * Take a screenshot of the current page
     * @param {string} sessionId - Session ID
     * @param {Object} options - Screenshot options
     * @returns {Promise<Buffer>} Screenshot buffer
     */
    async takeScreenshot(sessionId, options = {}) {
        try {
            const session = this.activeSessions.get(sessionId);
            if (!session) {
                throw new Error(`Session ${sessionId} not found`);
            }

            const { page } = session;
            session.lastUsed = Date.now();

            logger.info(`Taking screenshot in session ${sessionId}`);

            const screenshotOptions = {
                type: options.format || 'png',
                quality: options.quality || 90,
                fullPage: options.fullPage || false,
                clip: options.clip
            };

            const screenshot = await page.screenshot(screenshotOptions);
            
            logger.info(`Screenshot taken successfully in session ${sessionId}`, {
                size: screenshot.length,
                format: screenshotOptions.type
            });

            return screenshot;

        } catch (error) {
            logger.error(`Error taking screenshot: ${error.message}`, { sessionId });
            throw new Error(`Screenshot failed: ${error.message}`);
        }
    }

    /**
     * Interact with page elements (click, type, etc.)
     * @param {string} sessionId - Session ID
     * @param {string} action - Action type ('click', 'type', 'select', etc.)
     * @param {string} selector - Element selector
     * @param {any} value - Value for the action (text for type, option for select)
     * @returns {Promise<boolean>} Success status
     */
    async interactWithElement(sessionId, action, selector, value = null) {
        try {
            const session = this.activeSessions.get(sessionId);
            if (!session) {
                throw new Error(`Session ${sessionId} not found`);
            }

            const { page } = session;
            session.lastUsed = Date.now();

            logger.info(`Performing ${action} on ${selector}`, { sessionId, value });

            // Wait for element to be available
            await page.waitForSelector(selector, { timeout: 10000 });

            switch (action.toLowerCase()) {
                case 'click':
                    await page.click(selector);
                    break;
                case 'type':
                    await page.type(selector, value);
                    break;
                case 'clear':
                    await page.evaluate((sel) => {
                        document.querySelector(sel).value = '';
                    }, selector);
                    break;
                case 'select':
                    await page.select(selector, value);
                    break;
                case 'hover':
                    await page.hover(selector);
                    break;
                default:
                    throw new Error(`Unknown action: ${action}`);
            }

            logger.info(`Successfully performed ${action} on ${selector}`, { sessionId });
            return true;

        } catch (error) {
            logger.error(`Error interacting with element: ${error.message}`, {
                sessionId, action, selector, value
            });
            throw new Error(`Element interaction failed: ${error.message}`);
        }
    }

    /**
     * Extract content from page based on options
     * @private
     */
    async _extractContent(page, options) {
        const content = {};

        // Get HTML content
        if (options.includeHtml !== false) {
            content.html = await page.content();
        }

        // Get text content
        if (options.includeText !== false) {
            content.text = await page.evaluate(() => document.body.innerText);
        }

        // Custom selectors
        if (options.selectors) {
            content.elements = {};
            for (const [key, selector] of Object.entries(options.selectors)) {
                try {
                    const elements = await page.$$eval(selector, els => 
                        els.map(el => ({
                            text: el.textContent.trim(),
                            html: el.innerHTML,
                            attributes: Array.from(el.attributes).reduce((acc, attr) => {
                                acc[attr.name] = attr.value;
                                return acc;
                            }, {})
                        }))
                    );
                    content.elements[key] = elements;
                } catch (error) {
                    logger.warn(`Failed to extract ${key}: ${error.message}`);
                    content.elements[key] = [];
                }
            }
        }

        // Links
        if (options.includeLinks) {
            content.links = await page.$$eval('a[href]', links =>
                links.map(link => ({
                    text: link.textContent.trim(),
                    url: link.href,
                    title: link.title
                }))
            );
        }

        // Images
        if (options.includeImages) {
            content.images = await page.$$eval('img[src]', images =>
                images.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    title: img.title
                }))
            );
        }

        return content;
    }

    /**
     * Get page metadata
     * @private
     */
    async _getPageMetadata(page, response) {
        const metadata = {
            statusCode: response.status(),
            url: response.url(),
            headers: response.headers(),
            loadTime: Date.now()
        };

        try {
            // Get title
            metadata.title = await page.title();

            // Get meta tags
            metadata.meta = await page.$$eval('meta', metas =>
                metas.reduce((acc, meta) => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    if (name) {
                        acc[name] = meta.getAttribute('content');
                    }
                    return acc;
                }, {})
            );

        } catch (error) {
            logger.warn(`Error extracting metadata: ${error.message}`);
        }

        return metadata;
    }

    /**
     * Close a specific session
     * @param {string} sessionId - Session ID to close
     * @returns {Promise<boolean>} Success status
     */
    async closeSession(sessionId) {
        try {
            const session = this.activeSessions.get(sessionId);
            if (!session) {
                return false;
            }

            await session.page.close();
            this.activeSessions.delete(sessionId);

            logger.info(`Closed session: ${sessionId}`);
            return true;

        } catch (error) {
            logger.error(`Error closing session ${sessionId}: ${error.message}`);
            return false;
        }
    }

    /**
     * Get active sessions info
     * @returns {Object} Sessions information
     */
    getActiveSessions() {
        const sessions = {};
        for (const [id, session] of this.activeSessions.entries()) {
            sessions[id] = {
                created: session.created,
                lastUsed: session.lastUsed,
                age: Date.now() - session.created
            };
        }
        return sessions;
    }

    /**
     * Cleanup expired sessions
     * @param {number} maxAge - Maximum age in milliseconds (default: 1 hour)
     * @returns {Promise<number>} Number of sessions cleaned up
     */
    async cleanupSessions(maxAge = 3600000) {
        let cleaned = 0;
        const now = Date.now();
        
        for (const [sessionId, session] of this.activeSessions.entries()) {
            if (now - session.lastUsed > maxAge) {
                await this.closeSession(sessionId);
                cleaned++;
            }
        }

        if (cleaned > 0) {
            logger.info(`Cleaned up ${cleaned} expired sessions`);
        }

        return cleaned;
    }

    /**
     * Close browser and cleanup all resources
     * @returns {Promise<void>}
     */
    async close() {
        try {
            logger.info('Closing Puppeteer browser and all sessions...');

            // Close all active sessions
            const sessionIds = Array.from(this.activeSessions.keys());
            await Promise.all(sessionIds.map(id => this.closeSession(id)));

            // Close browser
            if (this.browser) {
                await this.browser.close();
                this.browser = null;
            }

            this.initialized = false;
            logger.info('Puppeteer browser closed successfully');

        } catch (error) {
            logger.error(`Error closing Puppeteer: ${error.message}`);
            throw error;
        }
    }
}

module.exports = PuppeteerMCP;