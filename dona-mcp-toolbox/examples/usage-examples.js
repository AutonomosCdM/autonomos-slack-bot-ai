#!/usr/bin/env node

const DonaMCP = require('../src/DonaMCP');

/**
 * Comprehensive usage examples for Dona MCP Toolbox
 * Demonstrates all major capabilities and use cases
 */

async function demonstrateUsage() {
    console.log('🚀 Dona MCP Toolbox - Usage Examples');
    console.log('====================================\n');

    const dona = new DonaMCP();

    try {
        // Initialize the toolbox
        console.log('📦 Initializing Dona MCP...');
        await dona.initialize();
        console.log('✅ Initialization complete!\n');

        // Show system status
        console.log('📊 System Status:');
        const status = dona.getSystemStatus();
        console.log(JSON.stringify(status, null, 2));
        console.log('');

        // List available capabilities
        console.log('🔧 Available Capabilities:');
        const capabilities = dona.getAvailableCapabilities();
        console.log(JSON.stringify(capabilities, null, 2));
        console.log('');

        // Example 1: ArXiv Research Papers
        await demonstrateArxivMCP(dona);

        // Example 2: GitHub Integration (commented out - requires token)
        // await demonstrateGitHubMCP(dona);

        // Example 3: Web Scraping (commented out - resource intensive)
        // await demonstratePuppeteerMCP(dona);

        // Example 4: Weather Data (commented out - requires API key)
        // await demonstrateWeatherMCP(dona);

        // Health check
        console.log('🏥 Health Check:');
        const health = await dona.healthCheck();
        console.log(JSON.stringify(health, null, 2));
        console.log('');

    } catch (error) {
        console.error('❌ Error during demonstration:', error.message);
    } finally {
        // Cleanup
        console.log('🧹 Cleaning up...');
        await dona.dispose();
        console.log('✅ Cleanup complete!');
    }
}

/**
 * Demonstrate ArXiv MCP capabilities
 */
async function demonstrateArxivMCP(dona) {
    console.log('📚 ArXiv MCP Examples');
    console.log('---------------------');

    try {
        // Search for papers using high-level method
        console.log('🔍 Searching for AI papers...');
        const papers = await dona.searchResearchPapers("artificial intelligence", 3);
        console.log(`Found ${papers.length} papers:`);
        papers.forEach((paper, index) => {
            console.log(`  ${index + 1}. ${paper.title}`);
            console.log(`     Authors: ${paper.authors.join(', ')}`);
            console.log(`     Categories: ${paper.categories.join(', ')}`);
            console.log(`     URL: ${paper.arxivUrl}`);
            console.log('');
        });

        // Get paper details using executeCapability
        if (papers.length > 0) {
            console.log('📄 Getting detailed paper information...');
            const firstPaper = papers[0];
            const details = await dona.executeCapability('arxiv', 'getPaperDetails', firstPaper.id);
            console.log(`Title: ${details.title}`);
            console.log(`Summary: ${details.summary.substring(0, 200)}...`);
            console.log('');
        }

        // Get ArXiv categories
        console.log('📂 Available ArXiv categories:');
        const arxivMCP = dona.getArxivMCP();
        const categories = arxivMCP.getCategories();
        Object.entries(categories).slice(0, 5).forEach(([code, name]) => {
            console.log(`  ${code}: ${name}`);
        });
        console.log('');

        // Get recent papers in a category
        console.log('🆕 Recent papers in Computer Vision:');
        const recentPapers = await arxivMCP.getRecentPapers('cs.CV', 2);
        recentPapers.forEach((paper, index) => {
            console.log(`  ${index + 1}. ${paper.title}`);
            console.log(`     Published: ${paper.published}`);
        });
        console.log('');

    } catch (error) {
        console.error('❌ ArXiv demonstration error:', error.message);
    }
}

/**
 * Demonstrate GitHub MCP capabilities (requires GITHUB_TOKEN)
 */
async function demonstrateGitHubMCP(dona) {
    console.log('🐙 GitHub MCP Examples');
    console.log('----------------------');

    try {
        // Search repositories
        console.log('🔍 Searching for React repositories...');
        const searchResults = await dona.executeCapability('github', 'searchRepositories', 'react', {
            limit: 3,
            sort: 'stars'
        });
        
        console.log(`Found ${searchResults.totalCount} total repositories, showing top ${searchResults.repositories.length}:`);
        searchResults.repositories.forEach((repo, index) => {
            console.log(`  ${index + 1}. ${repo.fullName}`);
            console.log(`     ⭐ ${repo.stars} stars | 🍴 ${repo.forks} forks`);
            console.log(`     ${repo.description}`);
            console.log('');
        });

        // Get repository details
        if (searchResults.repositories.length > 0) {
            const firstRepo = searchResults.repositories[0];
            console.log(`📋 Getting details for ${firstRepo.fullName}...`);
            const repoDetails = await dona.executeCapability('github', 'getRepository', 
                firstRepo.owner.login, firstRepo.name);
            
            console.log(`Language: ${repoDetails.language}`);
            console.log(`License: ${repoDetails.license?.name || 'None'}`);
            console.log(`Root files: ${repoDetails.rootContents?.length || 0} items`);
            console.log('');
        }

    } catch (error) {
        console.error('❌ GitHub demonstration error:', error.message);
        console.log('💡 Tip: Set GITHUB_TOKEN environment variable for full GitHub access');
    }
}

/**
 * Demonstrate Puppeteer MCP capabilities
 */
async function demonstratePuppeteerMCP(dona) {
    console.log('🕷️ Puppeteer MCP Examples');
    console.log('-------------------------');

    try {
        // Create a scraping session
        console.log('🌐 Creating web scraping session...');
        const sessionId = await dona.executeCapability('puppeteer', 'createSession', {
            blockResources: ['image', 'stylesheet', 'font']
        });
        console.log(`Session created: ${sessionId}`);

        // Scrape a website
        console.log('📄 Scraping example website...');
        const scrapingResult = await dona.executeCapability('puppeteer', 'scrapeUrl', 
            'https://example.com', {
                sessionId,
                persistent: true,
                includeLinks: true,
                selectors: {
                    headings: 'h1, h2',
                    paragraphs: 'p'
                }
            });

        console.log(`Page title: ${scrapingResult.metadata.title}`);
        console.log(`Found ${scrapingResult.content.links?.length || 0} links`);
        console.log(`Scraping time: ${scrapingResult.scrapingTime}ms`);
        console.log('');

        // Take a screenshot
        console.log('📸 Taking screenshot...');
        const screenshot = await dona.executeCapability('puppeteer', 'takeScreenshot', sessionId, {
            format: 'png',
            fullPage: true
        });
        console.log(`Screenshot captured: ${screenshot.length} bytes`);

        // Close session
        await dona.executeCapability('puppeteer', 'closeSession', sessionId);
        console.log('Session closed');
        console.log('');

    } catch (error) {
        console.error('❌ Puppeteer demonstration error:', error.message);
    }
}

/**
 * Demonstrate Weather MCP capabilities (requires WEATHER_API_KEY)
 */
async function demonstrateWeatherMCP(dona) {
    console.log('🌤️ Weather MCP Examples');
    console.log('-----------------------');

    try {
        // Get current weather
        console.log('🌡️ Getting current weather for London...');
        const currentWeather = await dona.executeCapability('weather', 'getCurrentWeather', 'London,UK');
        
        console.log(`Location: ${currentWeather.location.name}, ${currentWeather.location.country}`);
        console.log(`Temperature: ${currentWeather.temperature.current}°C (feels like ${currentWeather.temperature.feelsLike}°C)`);
        console.log(`Condition: ${currentWeather.condition.description}`);
        console.log(`Humidity: ${currentWeather.humidity}%`);
        console.log(`Wind: ${currentWeather.wind.speed} m/s`);
        console.log('');

        // Get weather forecast
        console.log('📅 Getting 3-day forecast...');
        const forecast = await dona.executeCapability('weather', 'getForecast', 'London,UK', 3);
        
        console.log(`Forecast for ${forecast.location.name}:`);
        forecast.periods.slice(0, 6).forEach((period, index) => {
            const date = new Date(period.datetime);
            console.log(`  ${date.toLocaleDateString()} ${date.toLocaleTimeString()}: ${period.temperature.current}°C, ${period.condition.description}`);
        });
        console.log('');

        // Search locations
        console.log('🔍 Searching for locations named "Paris"...');
        const locations = await dona.executeCapability('weather', 'searchLocations', 'Paris', 3);
        
        locations.forEach((location, index) => {
            console.log(`  ${index + 1}. ${location.name}, ${location.country} ${location.state ? `(${location.state})` : ''}`);
            console.log(`     Coordinates: ${location.lat}, ${location.lon}`);
        });
        console.log('');

    } catch (error) {
        console.error('❌ Weather demonstration error:', error.message);
        console.log('💡 Tip: Set WEATHER_API_KEY environment variable for weather access');
    }
}

/**
 * Run the demonstration
 */
if (require.main === module) {
    demonstrateUsage().catch(error => {
        console.error('💥 Fatal error:', error);
        process.exit(1);
    });
}

module.exports = {
    demonstrateUsage,
    demonstrateArxivMCP,
    demonstrateGitHubMCP,
    demonstratePuppeteerMCP,
    demonstrateWeatherMCP
};