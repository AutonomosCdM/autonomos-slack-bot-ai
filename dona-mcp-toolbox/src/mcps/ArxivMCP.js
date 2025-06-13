const axios = require('axios');
const xml2js = require('xml2js');
const logger = require('../utils/logger').createModuleLogger('ArxivMCP');
const mcpConfig = require('../config/mcpConfig');

/**
 * ArXiv MCP - Research paper search and retrieval system
 * Provides access to arXiv.org scientific papers database
 */
class ArxivMCP {
    constructor() {
        this.config = mcpConfig.getMCPConfig('arxiv');
        this.parser = new xml2js.Parser();
        this.cache = new Map();
        this.categories = {
            'cs.AI': 'Artificial Intelligence',
            'cs.LG': 'Machine Learning',
            'cs.CL': 'Computation and Language',
            'cs.CV': 'Computer Vision',
            'cs.RO': 'Robotics',
            'stat.ML': 'Machine Learning (Statistics)',
            'math.OC': 'Optimization and Control',
            'eess.AS': 'Audio and Speech Processing',
            'eess.IV': 'Image and Video Processing'
        };
    }

    /**
     * Search for papers on ArXiv
     * @param {string} query - Search query
     * @param {number} maxResults - Maximum number of results (default: 10)
     * @param {string} category - ArXiv category filter (optional)
     * @returns {Promise<Array>} Array of paper objects
     */
    async searchPapers(query, maxResults = 10, category = null) {
        const startTime = Date.now();
        
        try {
            logger.info(`Searching ArXiv for: "${query}"`, { maxResults, category });
            
            // Build search query
            let searchQuery = `all:${query}`;
            if (category) {
                searchQuery = `cat:${category} AND ${searchQuery}`;
            }
            
            const url = `${this.config.baseUrl}?search_query=${encodeURIComponent(searchQuery)}&start=0&max_results=${maxResults}&sortBy=relevance&sortOrder=descending`;
            
            const response = await axios.get(url, {
                timeout: this.config.timeout,
                headers: {
                    'User-Agent': 'DonaMCP-ArxivClient/1.0'
                }
            });
            
            const parsedData = await this.parser.parseStringPromise(response.data);
            const entries = parsedData.feed.entry || [];
            
            const papers = entries.map(entry => this._parseArxivEntry(entry));
            
            logger.info(`Found ${papers.length} papers`, { 
                query, 
                duration: Date.now() - startTime 
            });
            
            return papers;
            
        } catch (error) {
            logger.error(`Error searching ArXiv: ${error.message}`, { 
                query, 
                error: error.stack 
            });
            throw new Error(`ArXiv search failed: ${error.message}`);
        }
    }

    /**
     * Get detailed information about a specific paper
     * @param {string} arxivId - ArXiv paper ID (e.g., "2106.04554")
     * @returns {Promise<Object>} Detailed paper information
     */
    async getPaperDetails(arxivId) {
        const startTime = Date.now();
        
        try {
            // Check cache first
            const cacheKey = `paper_${arxivId}`;
            if (this.cache.has(cacheKey)) {
                logger.debug(`Returning cached paper details for ${arxivId}`);
                return this.cache.get(cacheKey);
            }
            
            logger.info(`Fetching paper details for: ${arxivId}`);
            
            const url = `${this.config.baseUrl}?id_list=${arxivId}`;
            const response = await axios.get(url, {
                timeout: this.config.timeout
            });
            
            const parsedData = await this.parser.parseStringPromise(response.data);
            const entry = parsedData.feed.entry?.[0];
            
            if (!entry) {
                throw new Error(`Paper not found: ${arxivId}`);
            }
            
            const paperDetails = this._parseArxivEntry(entry, true);
            
            // Cache the result
            this.cache.set(cacheKey, paperDetails);
            
            logger.info(`Retrieved paper details for ${arxivId}`, {
                duration: Date.now() - startTime
            });
            
            return paperDetails;
            
        } catch (error) {
            logger.error(`Error fetching paper details: ${error.message}`, {
                arxivId,
                error: error.stack
            });
            throw new Error(`Failed to get paper details: ${error.message}`);
        }
    }

    /**
     * Download paper in specified format
     * @param {string} arxivId - ArXiv paper ID
     * @param {string} format - Format ('pdf' or 'source')
     * @returns {Promise<Object>} Download information
     */
    async downloadPaper(arxivId, format = 'pdf') {
        try {
            logger.info(`Preparing download for ${arxivId} in ${format} format`);
            
            const baseUrl = 'https://arxiv.org';
            const downloadUrl = format === 'pdf' 
                ? `${baseUrl}/pdf/${arxivId}.pdf`
                : `${baseUrl}/e-print/${arxivId}`;
            
            return {
                arxivId,
                format,
                downloadUrl,
                filename: `${arxivId}.${format === 'pdf' ? 'pdf' : 'tar.gz'}`,
                instructions: `Use the downloadUrl to download the paper. For PDF: direct download. For source: contains LaTeX source files.`
            };
            
        } catch (error) {
            logger.error(`Error preparing download: ${error.message}`, { arxivId, format });
            throw new Error(`Download preparation failed: ${error.message}`);
        }
    }

    /**
     * Get available ArXiv categories
     * @returns {Object} Category codes and descriptions
     */
    getCategories() {
        logger.debug('Returning ArXiv categories');
        return { ...this.categories };
    }

    /**
     * Get recently published papers in a category
     * @param {string} category - ArXiv category
     * @param {number} maxResults - Maximum results
     * @returns {Promise<Array>} Recent papers
     */
    async getRecentPapers(category, maxResults = 10) {
        try {
            logger.info(`Fetching recent papers in category: ${category}`);
            
            const url = `${this.config.baseUrl}?search_query=cat:${category}&start=0&max_results=${maxResults}&sortBy=submittedDate&sortOrder=descending`;
            
            const response = await axios.get(url, {
                timeout: this.config.timeout
            });
            
            const parsedData = await this.parser.parseStringPromise(response.data);
            const entries = parsedData.feed.entry || [];
            
            const papers = entries.map(entry => this._parseArxivEntry(entry));
            
            logger.info(`Found ${papers.length} recent papers in ${category}`);
            return papers;
            
        } catch (error) {
            logger.error(`Error fetching recent papers: ${error.message}`, { category });
            throw new Error(`Failed to get recent papers: ${error.message}`);
        }
    }

    /**
     * Parse ArXiv XML entry into structured object
     * @param {Object} entry - XML entry from ArXiv API
     * @param {boolean} detailed - Whether to include detailed information
     * @returns {Object} Parsed paper object
     */
    _parseArxivEntry(entry, detailed = false) {
        const paper = {
            id: entry.id[0].split('/').pop(),
            title: entry.title[0].trim(),
            authors: entry.author ? entry.author.map(a => a.name[0]) : [],
            summary: entry.summary[0].trim(),
            categories: entry.category ? entry.category.map(c => c.$.term) : [],
            published: entry.published[0],
            updated: entry.updated[0],
            pdfUrl: entry.link ? entry.link.find(l => l.$.type === 'application/pdf')?.$.href : null,
            arxivUrl: entry.link ? entry.link.find(l => l.$.rel === 'alternate')?.$.href : null
        };

        if (detailed) {
            paper.comment = entry.comment?.[0];
            paper.journalRef = entry['arxiv:journal_ref']?.[0];
            paper.doi = entry['arxiv:doi']?.[0];
            paper.primaryCategory = entry['arxiv:primary_category']?.[0]?.$.term;
        }

        return paper;
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        logger.info('ArXiv cache cleared');
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

module.exports = ArxivMCP;