const DonaMCP = require('../src/DonaMCP');

describe('DonaMCP Main Class', () => {
    let dona;

    beforeEach(() => {
        dona = new DonaMCP();
    });

    afterEach(async () => {
        if (dona.initialized) {
            await dona.dispose();
        }
    });

    describe('Initialization', () => {
        test('should initialize successfully', async () => {
            const result = await dona.initialize();
            expect(result).toBe(true);
            expect(dona.initialized).toBe(true);
        });

        test('should throw error when calling methods before initialization', () => {
            expect(() => dona.getAvailableCapabilities()).toThrow();
        });
    });

    describe('Capabilities', () => {
        beforeEach(async () => {
            await dona.initialize();
        });

        test('should return available capabilities', () => {
            const capabilities = dona.getAvailableCapabilities();
            expect(capabilities).toHaveProperty('arxiv');
            expect(capabilities.arxiv).toContain('searchPapers');
            expect(capabilities.arxiv).toContain('getPaperDetails');
        });

        test('should execute ArXiv capabilities', async () => {
            const papers = await dona.executeCapability('arxiv', 'searchPapers', 'test', 1);
            expect(Array.isArray(papers)).toBe(true);
        });

        test('should throw error for invalid MCP', async () => {
            await expect(dona.executeCapability('invalid', 'method')).rejects.toThrow();
        });

        test('should throw error for invalid method', async () => {
            await expect(dona.executeCapability('arxiv', 'invalidMethod')).rejects.toThrow();
        });
    });

    describe('High-level Methods', () => {
        beforeEach(async () => {
            await dona.initialize();
        });

        test('should search research papers', async () => {
            const papers = await dona.searchResearchPapers('machine learning', 2);
            expect(Array.isArray(papers)).toBe(true);
            expect(papers.length).toBeLessThanOrEqual(2);
        });

        test('should get ArXiv MCP instance', () => {
            const arxivMCP = dona.getArxivMCP();
            expect(arxivMCP).toBeDefined();
            expect(typeof arxivMCP.searchPapers).toBe('function');
        });
    });

    describe('System Status and Health', () => {
        test('should return system status', async () => {
            await dona.initialize();
            const status = dona.getSystemStatus();
            
            expect(status).toHaveProperty('initialized', true);
            expect(status).toHaveProperty('uptime');
            expect(status).toHaveProperty('availableMCPs');
            expect(status.availableMCPs).toContain('arxiv');
        });

        test('should perform health check', async () => {
            await dona.initialize();
            const health = await dona.healthCheck();
            
            expect(health).toHaveProperty('healthy');
            expect(health).toHaveProperty('timestamp');
            expect(health).toHaveProperty('modules');
            expect(health.modules).toHaveProperty('arxiv');
        });

        test('should return unhealthy status when not initialized', async () => {
            const health = await dona.healthCheck();
            expect(health.healthy).toBe(false);
        });
    });

    describe('Configuration', () => {
        beforeEach(async () => {
            await dona.initialize();
        });

        test('should get configuration', () => {
            const config = dona.getConfiguration();
            expect(config).toHaveProperty('arxiv');
            expect(config).toHaveProperty('general');
        });

        test('should get specific MCP configuration', () => {
            const arxivConfig = dona.getConfiguration('arxiv');
            expect(arxivConfig).toHaveProperty('baseUrl');
            expect(arxivConfig).toHaveProperty('maxResults');
        });

        test('should update configuration', () => {
            const originalConfig = dona.getConfiguration('arxiv');
            dona.updateConfiguration('arxiv', { maxResults: 20 });
            const updatedConfig = dona.getConfiguration('arxiv');
            
            expect(updatedConfig.maxResults).toBe(20);
            expect(updatedConfig.baseUrl).toBe(originalConfig.baseUrl);
        });
    });

    describe('Resource Management', () => {
        test('should dispose properly', async () => {
            await dona.initialize();
            expect(dona.initialized).toBe(true);
            
            await dona.dispose();
            expect(dona.initialized).toBe(false);
            expect(Object.keys(dona.mcps)).toHaveLength(0);
        });

        test('should handle disposal errors gracefully', async () => {
            await dona.initialize();
            
            // Simulate error by corrupting MCP
            const originalClearCache = dona.mcps.arxiv.clearCache;
            dona.mcps.arxiv.clearCache = () => {
                throw new Error('Test error');
            };
            
            try {
                await expect(dona.dispose()).rejects.toThrow();
            } finally {
                // Restore original method for cleanup
                dona.mcps.arxiv.clearCache = originalClearCache;
            }
        });
    });
});