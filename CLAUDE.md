# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a production-ready Slack bot with advanced AI capabilities, hybrid memory system, and MCP integration:
1. **Production bot** (`app_ai_production.py`) - Main bot with OpenRouter integration and MCP capabilities
2. **Development bot** (`app.py`) - Multi-LLM support for testing
3. **Robust memory system** - SQLite + Redis hybrid with intelligent context
4. **MCP toolbox** (`dona-mcp-toolbox/`) - Node.js-based external capabilities (ArXiv, GitHub, etc.)

All bots use Socket Mode via `start.py` for reliable production deployment.

## Key Commands

### Running the Bot
```bash
# Production mode (recommended)
python start.py

# Development mode with multi-LLM support
python app.py

# Convenience script with status info
./run_bot.sh
```

### Development Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for MCP toolbox
cd dona-mcp-toolbox && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env with tokens, API keys, and REDIS_URL

# Test complete system functionality
python test_quick_wins.py

# Test individual components
python test_ai.py           # LLM integration
python test_message.py      # Bot connectivity
```

### Build Commands (Production)
```bash
# Complete build process (used by Render)
./build.sh

# Manual build steps
pip install -r requirements.txt
cd dona-mcp-toolbox && npm install && cd ..
```

### Testing Commands
```bash
# Test complete system functionality
python test_quick_wins.py

# Test MCP integration
python test_mcp_integration.py

# Test individual components
python test_ai.py           # LLM integration
python test_message.py      # Bot connectivity
python test_canvas.py       # Canvas functionality
python test_canvas_api.py   # Direct Canvas API testing

# Test memory system components
python -c "from memory_manager import memory_manager; print(memory_manager.get_memory_stats())"
python -c "from redis_memory import redis_memory; print(redis_memory.get_realtime_stats())"
python -c "from intelligent_memory import intelligent_memory; print(intelligent_memory.analyze_message_context('hello', []))"

# Test MCP components
python -c "from mcp_integration import mcp_integration; mcp_integration.initialize(); print('MCP Ready')"
```

### MCP Toolbox Commands
```bash
# Navigate to MCP directory
cd dona-mcp-toolbox

# Install MCP dependencies
npm install

# Run MCP tests
npm test

# Run MCP examples
npm run example

# Lint MCP code
npm run lint

# Development mode with auto-reload
npm run dev
```

## Architecture

### Core Components

1. **Bot Framework**: Slack Bolt for Python with robust Socket Mode handling
   - `start.py`: Production launcher with auto-reconnection and health checks
   - `app_ai_production.py`: Main production bot with optimized LLM integration
   - Socket Mode eliminates need for public URLs or webhooks

2. **Hybrid Memory System**: Three-tier intelligent memory architecture
   - **SQLite** (`memory_manager.py`): Persistent conversation storage and user preferences
   - **Redis** (`redis_memory.py`): Active sessions, context caching, real-time stats
   - **Intelligent Analysis** (`intelligent_memory.py`): Semantic analysis, intent detection, relevance filtering

3. **LLM Integration**: Production-optimized OpenRouter integration
   - `llm_handler_production.py`: Streamlined OpenRouter-only handler
   - `llm_config_production.py`: Production configuration management
   - Development version supports multiple providers (Anthropic, OpenAI, OpenRouter)

4. **Canvas System**: Intelligent document creation and collaboration
   - **Canvas Manager** (`canvas_manager.py`): Automated Canvas creation with templates
   - **Templates**: Summary, Knowledge Base, Project Documentation, Meeting Notes
   - **Direct API Integration**: Uses REST API directly since Python SDK doesn't support Canvas yet
   - **Smart Content Generation**: Extracts key points, decisions, tasks from conversations

5. **MCP Integration**: Model Context Protocol toolbox for external capabilities
   - **ArXiv Integration** (`mcp_integration.py`): Scientific paper search and retrieval
   - **Node.js Bridge**: Python-to-Node.js bridge for MCP toolbox access
   - **Automatic Detection**: Natural language detection for ArXiv, Weather, GitHub, and Web scraping
   - **Research Commands**: `/papers`, `/mcp` slash commands for scientific research
   - **Smart Formatting**: Automatic Slack-optimized formatting for research results

6. **Interactive Features**: Block Kit UI and contextual responses
   - Interactive buttons with ephemeral messages
   - Automatic thread responses and contextual reactions
   - Intelligent context filtering and tone recommendations

7. **Architecture Flow**:
   ```
   Slack Event → Socket Mode → Memory Logging → Context Analysis → [Automatic MCP Detection] → [MCP Research/LLM Processing] → Enhanced Response
   ```

### Automatic MCP Detection System

The bot automatically detects user intent and routes to appropriate MCP capabilities without requiring slash commands:

- **ArXiv**: "busca papers sobre...", "research on...", "artículos de machine learning"
- **Weather**: "clima en Madrid", "weather in London", "temperatura de Barcelona"  
- **GitHub**: "mis repos", "repositorios populares", "dame repos de Python"
- **Web Scraping**: "extrae contenido de URL", "screenshot de https://..."

Detection happens in `llm_handler_production.py` using keyword matching and regex patterns for Spanish and English.

### Critical Configuration

The bot requires specific Slack app configuration:
- **Events**: `app_mention`, `message.im`, `message.channels`, `reaction_added`
- **OAuth Scopes**: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`, `commands`, `reactions:read`, `reactions:write`, `canvases:write`
- **Socket Mode**: Must be enabled with App-Level Token
- **Slash Commands**: Register `/hello`, `/memory`, `/provider`, `/canvas`, `/papers`, `/mcp` in manifest.json

The bot includes interactive features requiring:
- **Interactivity**: Must be enabled for button responses
- **Block Kit**: Used for interactive menus and ephemeral messages

### Environment Variables

**Required for all deployments:**
- `SLACK_BOT_TOKEN`: Bot User OAuth Token (xoxb-)
- `SLACK_APP_TOKEN`: App-Level Token (xapp-)
- `OPENROUTER_API_KEY`: OpenRouter API key for LLM integration
- `OPENROUTER_MODEL`: Model name (e.g., "meta-llama/llama-3.3-70b-instruct")

**Optional Redis for enhanced performance:**
- `REDIS_URL`: Redis connection string (e.g., from Upstash)
- Without Redis, system falls back to SQLite-only mode

**MCP Requirements:**
- `Node.js`: Required for MCP toolbox functionality (v16+ recommended)
- MCP toolbox automatically available in `dona-mcp-toolbox/` directory
- No additional API keys needed for ArXiv functionality

**Development only (multi-provider support):**
- `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL`
- `OPENAI_API_KEY` + `OPENAI_MODEL`
- `LLM_PROVIDER`: "openrouter" | "anthropic" | "openai"

## Memory System Architecture

The bot implements a sophisticated three-tier memory system:

### FASE 1: SQLite Foundation
- **Persistent storage** for conversations, users, and active contexts
- **Database tables**: `users`, `conversations`, `active_context`
- **Cross-restart persistence** with conversation history and user preferences

### FASE 2: Redis Enhancement  
- **Session management** with automatic TTL (30 min inactivity)
- **Context caching** for fast retrieval (10 min cache)
- **Real-time statistics** and active user tracking
- **Graceful fallback** to SQLite-only mode if Redis unavailable

### FASE 3: Intelligent Context
- **Semantic analysis**: Intent detection, sentiment analysis, urgency assessment
- **Relevance filtering**: Context pruning based on topic similarity and conversation flow
- **Tone recommendations**: Dynamic response style based on message analysis
- **Entity extraction**: Names, technologies, commands automatically identified

### Memory Integration Flow
```
User Message → SQLite Logging → Redis Session Update → Intelligent Analysis → Context Retrieval → LLM Context → Response
```

## Production Deployment

The bot is optimized for **Render.com** deployment:

### Critical Files for Production
- `start.py`: Robust launcher with health checks and auto-reconnection
- `app_ai_production.py`: Streamlined production bot (OpenRouter only)
- `llm_handler_production.py`: Production-optimized LLM integration with automatic MCP detection
- `build.sh`: Build script that installs Python + Node.js dependencies
- `package.json`: Node.js configuration for MCP toolbox
- `requirements.txt`: Pinned dependencies for stability

### Render.com Configuration
```bash
# Build Command
./build.sh

# Start Command  
python start.py
```

### Production vs Development
- **Production**: Uses single LLM provider (OpenRouter) for simplicity and cost control
- **Development**: Supports multiple providers for testing and comparison
- **Memory**: Both use same hybrid SQLite+Redis system
- **Features**: Production includes all interactive features and memory intelligence

## Canvas System Implementation

The Canvas functionality requires special handling due to SDK limitations:

### Canvas API Integration
- **Direct REST API**: Python SDK doesn't support `canvases.create` yet, so we use `requests` directly
- **Authentication**: Uses bot token from Slack client for API calls
- **Error Handling**: Comprehensive logging and fallback for API failures
- **Template System**: Pre-built templates for different Canvas types

### Canvas Types Available
1. **Conversation Summary** (`/canvas resumen`): Auto-extracts key points, decisions, tasks
2. **Knowledge Base** (`/canvas knowledge [topic]`): Collaborative documentation by topic
3. **Project Documentation** (`/canvas proyecto [name]`): Project tracking and requirements
4. **Meeting Notes**: Template for structured meeting documentation

### Usage Patterns
```bash
# Create conversation summary (needs sufficient chat history)
/canvas resumen

# Create knowledge base for specific topic
/canvas knowledge Python Testing

# Document a new project
/canvas proyecto New Feature Implementation
```

## MCP System Architecture

The MCP (Model Context Protocol) integration bridges Python and Node.js to provide external capabilities:

### Python-Node.js Bridge
- **Integration Layer** (`mcp_integration.py`): Python wrapper for Node.js MCP toolbox
- **Subprocess Communication**: JSON-based communication via Node.js subprocess calls
- **Error Handling**: Robust error handling and fallback mechanisms
- **Caching**: Intelligent caching of MCP results for performance

### MCP Toolbox Structure
```
dona-mcp-toolbox/
├── src/
│   ├── DonaMCP.js              # Main orchestrator
│   ├── mcps/                   # Individual MCP modules
│   │   ├── ArxivMCP.js         # Scientific paper search
│   │   ├── GitHubMCP.js        # Repository management
│   │   ├── PuppeteerMCP.js     # Web scraping
│   │   └── WeatherMCP.js       # Weather data
│   ├── utils/logger.js         # Centralized logging
│   └── config/mcpConfig.js     # Configuration management
├── tests/                      # Comprehensive test suite
└── examples/                   # Usage examples
```

### MCP Integration Flow
```
Slack Message → Intent Detection → mcp_integration.py → Node.js Subprocess → MCP Module → External API → Response Processing → Slack Response
```

### Troubleshooting MCP Issues

Common issues and solutions:

1. **"Error iniciando sistema" messages in Slack**:
   This indicates MCP initialization is failing. Run diagnostics:
   ```bash
   # Quick diagnosis
   python diagnose_mcp.py
   
   # Full diagnosis
   python test_mcp_production.py
   ```

2. **Node.js dependencies missing in production**:
   - Ensure `build.sh` is set as Build Command in Render
   - Check that `npm install` runs in `dona-mcp-toolbox/` during build
   - Verify build logs show "✅ MCP dependencies installed"

3. **MCP initialization fails locally**:
   ```bash
   # Test Node.js availability
   which node
   
   # Test MCP toolbox directly
   cd dona-mcp-toolbox && npm test
   
   # Test Python integration
   python -c "from mcp_integration import mcp_integration; print(mcp_integration.initialize())"
   ```

4. **Detection not working**:
   - Check logs for "🔬", "🌤️", "🐙", "🕷️" detection messages
   - Verify keywords in detection methods match user input
   - Test with explicit examples from detection patterns

5. **Production deployment issues**:
   - Verify Render build command is set to: `./build.sh`
   - Check Render build logs for Node.js installation
   - Ensure both Python and Node.js environments are available
   - Run `python diagnose_mcp.py` after deployment to verify setup

## Key Design Decisions

1. **Hybrid Memory System**: SQLite for persistence + Redis for performance + AI for intelligence
2. **Production Simplification**: Single LLM provider in production, multi-provider in development
3. **Socket Mode Architecture**: Eliminates webhooks and public URL requirements
4. **Interactive UI**: Block Kit buttons and ephemeral messages for better UX
5. **Contextual Intelligence**: AI-driven context filtering and response optimization
6. **Canvas Direct API**: Bypass SDK limitations with direct REST calls
7. **MCP Hybrid Architecture**: Python-Node.js bridge for extending capabilities
8. **Graceful Degradation**: System functions even if Redis or MCP components are unavailable
9. **Automatic MCP Routing**: Natural language intent detection eliminates need for slash commands