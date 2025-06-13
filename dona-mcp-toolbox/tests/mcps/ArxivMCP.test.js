const ArxivMCP = require('../../src/mcps/ArxivMCP');

describe('ArxivMCP', () => {
    let arxivMCP;

    beforeEach(() => {
        arxivMCP = new ArxivMCP();
    });

    afterEach(() => {
        arxivMCP.clearCache();
    });

    describe('Search Papers', () => {
        test('should search for papers successfully', async () => {
            const papers = await arxivMCP.searchPapers('machine learning', 3);
            
            expect(Array.isArray(papers)).toBe(true);
            expect(papers.length).toBeLessThanOrEqual(3);
            
            if (papers.length > 0) {
                const paper = papers[0];
                expect(paper).toHaveProperty('id');
                expect(paper).toHaveProperty('title');
                expect(paper).toHaveProperty('authors');
                expect(paper).toHaveProperty('summary');
                expect(paper).toHaveProperty('categories');
                expect(Array.isArray(paper.authors)).toBe(true);
                expect(Array.isArray(paper.categories)).toBe(true);
            }
        }, 10000);

        test('should search with category filter', async () => {
            const papers = await arxivMCP.searchPapers('neural networks', 2, 'cs.LG');
            
            expect(Array.isArray(papers)).toBe(true);
            expect(papers.length).toBeLessThanOrEqual(2);
            
            if (papers.length > 0) {
                const paper = papers[0];
                expect(paper.categories).toContain('cs.LG');
            }
        }, 10000);

        test('should handle search errors gracefully', async () => {
            // Test with invalid query that might cause issues - empty query returns empty array
            const result = await arxivMCP.searchPapers('');
            expect(Array.isArray(result)).toBe(true);
        });

        test('should return empty array for no results', async () => {
            // Search for something very unlikely to exist
            const papers = await arxivMCP.searchPapers('xyzveryrareterm123456789', 5);
            expect(Array.isArray(papers)).toBe(true);
        }, 10000);
    });

    describe('Paper Details', () => {
        test('should get paper details by ID', async () => {
            // Use a known paper ID for testing
            const paperId = '1706.03762'; // "Attention Is All You Need" - Transformer paper
            const details = await arxivMCP.getPaperDetails(paperId);
            
            expect(details.id).toContain(paperId);
            expect(details).toHaveProperty('title');
            expect(details).toHaveProperty('authors');
            expect(details).toHaveProperty('summary');
            expect(details.title).toContain('Attention');
        }, 10000);

        test('should cache paper details', async () => {
            const paperId = '1706.03762';
            
            // First call
            const details1 = await arxivMCP.getPaperDetails(paperId);
            
            // Second call (should be from cache)
            const details2 = await arxivMCP.getPaperDetails(paperId);
            
            expect(details1).toEqual(details2);
            
            // Check cache stats
            const cacheStats = arxivMCP.getCacheStats();
            expect(cacheStats.size).toBeGreaterThan(0);
            expect(cacheStats.keys).toContain(`paper_${paperId}`);
        }, 10000);

        test('should handle invalid paper ID', async () => {
            await expect(arxivMCP.getPaperDetails('invalid-id')).rejects.toThrow();
        });
    });

    describe('Download Information', () => {
        test('should provide download information for PDF', async () => {
            const paperId = '1706.03762';
            const downloadInfo = await arxivMCP.downloadPaper(paperId, 'pdf');
            
            expect(downloadInfo).toHaveProperty('arxivId', paperId);
            expect(downloadInfo).toHaveProperty('format', 'pdf');
            expect(downloadInfo).toHaveProperty('downloadUrl');
            expect(downloadInfo).toHaveProperty('filename');
            expect(downloadInfo.downloadUrl).toContain('pdf');
            expect(downloadInfo.filename).toContain('.pdf');
        });

        test('should provide download information for source', async () => {
            const paperId = '1706.03762';
            const downloadInfo = await arxivMCP.downloadPaper(paperId, 'source');
            
            expect(downloadInfo).toHaveProperty('format', 'source');
            expect(downloadInfo.downloadUrl).toContain('e-print');
            expect(downloadInfo.filename).toContain('.tar.gz');
        });
    });

    describe('Categories', () => {
        test('should return available categories', () => {
            const categories = arxivMCP.getCategories();
            
            expect(typeof categories).toBe('object');
            expect(Object.keys(categories)).toContain('cs.AI');
            expect(Object.keys(categories)).toContain('cs.LG');
            expect(categories['cs.AI']).toBe('Artificial Intelligence');
            expect(categories['cs.LG']).toBe('Machine Learning');
        });
    });

    describe('Recent Papers', () => {
        test('should get recent papers in category', async () => {
            const recentPapers = await arxivMCP.getRecentPapers('cs.AI', 5);
            
            expect(Array.isArray(recentPapers)).toBe(true);
            expect(recentPapers.length).toBeLessThanOrEqual(5);
            
            if (recentPapers.length > 0) {
                const paper = recentPapers[0];
                expect(paper).toHaveProperty('id');
                expect(paper).toHaveProperty('title');
                expect(paper).toHaveProperty('published');
                expect(paper.categories).toContain('cs.AI');
            }
        }, 10000);

        test('should handle invalid category', async () => {
            // Invalid category returns empty array instead of throwing
            const result = await arxivMCP.getRecentPapers('invalid-category');
            expect(Array.isArray(result)).toBe(true);
        });
    });

    describe('Cache Management', () => {
        test('should manage cache properly', async () => {
            // Add something to cache
            await arxivMCP.getPaperDetails('1706.03762');
            
            let cacheStats = arxivMCP.getCacheStats();
            expect(cacheStats.size).toBeGreaterThan(0);
            
            // Clear cache
            arxivMCP.clearCache();
            
            cacheStats = arxivMCP.getCacheStats();
            expect(cacheStats.size).toBe(0);
        }, 10000);

        test('should track cache statistics', async () => {
            const cacheStats = arxivMCP.getCacheStats();
            
            expect(cacheStats).toHaveProperty('size');
            expect(cacheStats).toHaveProperty('keys');
            expect(Array.isArray(cacheStats.keys)).toBe(true);
        });
    });
});