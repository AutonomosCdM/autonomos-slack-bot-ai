# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a production-ready Slack bot with advanced AI capabilities and hybrid memory system:
1. **Production bot** (`app_ai_production.py`) - Main bot with OpenRouter integration
2. **Development bot** (`app.py`) - Multi-LLM support for testing
3. **Robust memory system** - SQLite + Redis hybrid with intelligent context

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
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with tokens, API keys, and REDIS_URL

# Test complete system functionality
python test_quick_wins.py

# Test individual components
python test_ai.py           # LLM integration
python test_message.py      # Bot connectivity
```

### Memory System Testing
```bash
# Test memory functionality
python -c "from memory_manager import memory_manager; print(memory_manager.get_memory_stats())"

# Test Redis connectivity
python -c "from redis_memory import redis_memory; print(redis_memory.get_realtime_stats())"

# Test intelligent analysis
python -c "from intelligent_memory import intelligent_memory; print(intelligent_memory.analyze_message_context('hello', []))"
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

4. **Interactive Features**: Block Kit UI and contextual responses
   - Interactive buttons with ephemeral messages
   - Automatic thread responses and contextual reactions
   - Intelligent context filtering and tone recommendations

5. **Architecture Flow**:
   ```
   Slack Event → Socket Mode → Memory Logging → Context Analysis → LLM Processing → Enhanced Response
   ```

### Critical Configuration

The bot requires specific Slack app configuration:
- **Events**: `app_mention`, `message.im`, `message.channels`, `reaction_added`
- **OAuth Scopes**: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`, `commands`, `reactions:read`, `reactions:write`
- **Socket Mode**: Must be enabled with App-Level Token
- **Slash Commands**: Register `/hello`, `/memory`, `/provider` in manifest.json

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
- `llm_handler_production.py`: Production-optimized LLM integration
- `requirements.txt`: Pinned dependencies for stability

### Production vs Development
- **Production**: Uses single LLM provider (OpenRouter) for simplicity and cost control
- **Development**: Supports multiple providers for testing and comparison
- **Memory**: Both use same hybrid SQLite+Redis system
- **Features**: Production includes all interactive features and memory intelligence

## Key Design Decisions

1. **Hybrid Memory System**: SQLite for persistence + Redis for performance + AI for intelligence
2. **Production Simplification**: Single LLM provider in production, multi-provider in development
3. **Socket Mode Architecture**: Eliminates webhooks and public URL requirements
4. **Interactive UI**: Block Kit buttons and ephemeral messages for better UX
5. **Contextual Intelligence**: AI-driven context filtering and response optimization
6. **Graceful Degradation**: System functions even if Redis is unavailable