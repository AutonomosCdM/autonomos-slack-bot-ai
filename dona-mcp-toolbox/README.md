# Dona MCP Toolbox

A comprehensive Model Context Protocol (MCP) toolbox for the Dona AI Assistant, providing unified access to various external services and capabilities.

## 🚀 Features

- **ArXiv Integration**: Search and retrieve scientific papers
- **GitHub API**: Repository management and code analysis
- **Web Scraping**: Advanced browser automation with Puppeteer
- **Weather Data**: Real-time weather information and forecasts
- **Unified Interface**: Single API to access all MCP capabilities
- **Intelligent Caching**: Optimized performance with smart caching
- **Comprehensive Logging**: Detailed logging and monitoring
- **Robust Error Handling**: Graceful error recovery and reporting

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd dona-mcp-toolbox

# Install dependencies
npm install

# Copy environment variables template
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# GitHub Integration (optional)
GITHUB_TOKEN=your_github_token_here

# Weather API (optional)
WEATHER_API_KEY=your_openweathermap_api_key_here

# Logging level
LOG_LEVEL=info
```

## 🎯 Quick Start

```javascript
const DonaMCP = require('./src/DonaMCP');

async function main() {
    const dona = new DonaMCP();
    
    // Initialize all MCP modules
    await dona.initialize();
    
    // Search for research papers
    const papers = await dona.searchResearchPapers("machine learning", 5);
    console.log(`Found ${papers.length} papers`);
    
    // Get system status
    const status = dona.getSystemStatus();
    console.log('System status:', status);
    
    // Cleanup
    await dona.dispose();
}

main().catch(console.error);
```

## 📚 Available MCPs

### ArXiv MCP
Search and retrieve scientific papers from arXiv.org

```javascript
// Search papers
const papers = await dona.executeCapability('arxiv', 'searchPapers', 'neural networks', 10);

// Get paper details
const details = await dona.executeCapability('arxiv', 'getPaperDetails', '1706.03762');

// Get recent papers in category
const recent = await dona.executeCapability('arxiv', 'getRecentPapers', 'cs.AI', 5);
```

### GitHub MCP
Interact with GitHub repositories and users

```javascript
// Search repositories
const repos = await dona.executeCapability('github', 'searchRepositories', 'react', { limit: 10 });

// Get repository details
const repo = await dona.executeCapability('github', 'getRepository', 'facebook', 'react');

// Get file content
const file = await dona.executeCapability('github', 'getFileContent', 'owner', 'repo', 'README.md');
```

### Puppeteer MCP
Advanced web scraping and browser automation

```javascript
// Create session
const sessionId = await dona.executeCapability('puppeteer', 'createSession');

// Scrape website
const result = await dona.executeCapability('puppeteer', 'scrapeUrl', 'https://example.com', {
    sessionId,
    includeLinks: true,
    selectors: { headings: 'h1, h2' }
});

// Take screenshot
const screenshot = await dona.executeCapability('puppeteer', 'takeScreenshot', sessionId);
```

### Weather MCP
Real-time weather data and forecasts

```javascript
// Get current weather
const weather = await dona.executeCapability('weather', 'getCurrentWeather', 'London,UK');

// Get forecast
const forecast = await dona.executeCapability('weather', 'getForecast', 'New York', 5);

// Search locations
const locations = await dona.executeCapability('weather', 'searchLocations', 'Paris');
```

## 🔍 API Reference

### DonaMCP Class

#### Methods

- `initialize()` - Initialize all MCP modules
- `getAvailableCapabilities()` - List all available capabilities
- `executeCapability(mcpName, method, ...params)` - Execute MCP method
- `searchResearchPapers(query, maxResults)` - High-level paper search
- `getSystemStatus()` - Get system status and statistics
- `healthCheck()` - Perform health check on all modules
- `dispose()` - Cleanup and dispose resources

### Configuration Management

```javascript
// Get configuration
const config = dona.getConfiguration('arxiv');

// Update configuration
dona.updateConfiguration('arxiv', { maxResults: 20 });
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run specific test file
npm test tests/DonaMCP.test.js

# Run with coverage
npm test -- --coverage
```

## 📖 Examples

Run the comprehensive examples:

```bash
# Run usage examples
npm run example

# Or directly
node examples/usage-examples.js
```

## 🔧 Development

```bash
# Install development dependencies
npm install

# Run linting
npm run lint

# Start development mode with auto-reload
npm run dev
```

## 📁 Project Structure

```
dona-mcp-toolbox/
├── src/
│   ├── DonaMCP.js              # Main orchestrator class
│   ├── mcps/                   # Individual MCP implementations
│   │   ├── ArxivMCP.js
│   │   ├── GitHubMCP.js
│   │   ├── PuppeteerMCP.js
│   │   └── WeatherMCP.js
│   ├── utils/
│   │   └── logger.js           # Logging utility
│   └── config/
│       └── mcpConfig.js        # Configuration management
├── tests/                      # Test files
├── examples/                   # Usage examples
├── package.json
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [examples](examples/) directory for usage patterns
- Run tests to verify functionality: `npm test`
- Enable debug logging: `LOG_LEVEL=debug`
- Review error logs in the `logs/` directory

## 🔮 Roadmap

- [ ] **Email MCP**: Email composition and management
- [ ] **Calendar MCP**: Calendar integration and scheduling
- [ ] **Database MCP**: Database query capabilities
- [ ] **Translation MCP**: Multi-language translation services
- [ ] **Image Processing MCP**: Image analysis and manipulation
- [ ] **Crypto MCP**: Cryptocurrency market data
- [ ] **News MCP**: News aggregation and filtering
- [ ] **Plugin System**: Easy addition of custom MCPs
- [ ] **Rate Limiting**: Advanced rate limiting and throttling
- [ ] **Caching Layer**: Distributed caching with Redis
- [ ] **Monitoring**: Comprehensive metrics and monitoring
- [ ] **WebSocket Support**: Real-time capabilities
- [ ] **CLI Interface**: Command-line interface for direct usage

## 📊 Performance

The toolbox is designed for optimal performance:

- **Intelligent Caching**: Reduces API calls and improves response times
- **Connection Pooling**: Efficient resource management
- **Async/Await**: Non-blocking operations throughout
- **Error Recovery**: Automatic retry mechanisms
- **Memory Management**: Proper cleanup and resource disposal
- **Logging**: Configurable logging levels for production optimization

## 🛡️ Security

- **API Key Management**: Secure storage of sensitive credentials
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Protection against API abuse
- **Error Handling**: Secure error messages without data leakage
- **Resource Cleanup**: Proper disposal of sensitive resources