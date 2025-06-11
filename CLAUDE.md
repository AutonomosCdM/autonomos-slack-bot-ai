# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Slack bot project with two main implementations:
1. **Basic bot** (`app.py`) - Hardcoded responses for testing
2. **AI-enhanced bot** (`app_ai.py`) - Multi-LLM support with intelligent responses

Both use Socket Mode, eliminating the need for public URLs or ngrok.

## Key Commands

### Running the Bot
```bash
# Basic bot
python app.py

# AI-enhanced bot  
python app_ai.py

# Or use the convenience scripts
./run_bot.sh      # Basic bot
./run_ai_bot.sh   # AI bot
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens and API keys

# Test LLM integration
python test_ai.py
```

### Testing Bot Connectivity
```bash
# Send test message to channel
python test_message.py

# Setup bot in specific channel
python setup_bot.py

# Reactivate if messaging disabled
python send_reactivation_message.py
```

## Architecture

### Core Components

1. **Bot Framework**: Uses Slack Bolt for Python with Socket Mode
   - `app.event()` decorators handle Slack events
   - `app.command()` decorators handle slash commands
   - Socket Mode handler manages WebSocket connection

2. **LLM Integration** (AI bot only):
   - `llm_config.py`: Manages provider configurations and switching
   - `llm_handler.py`: Unified interface for all LLM providers
   - Supports Anthropic, OpenRouter, and OpenAI
   - Runtime provider switching via `/switch [provider]` command

3. **Event Flow**:
   ```
   Slack Event → Socket Mode → Event Handler → [LLM Processing] → Response
   ```

### Critical Configuration

The bot requires specific Slack app configuration:
- **Events**: `app_mention`, `message.im`, `message.channels`
- **OAuth Scopes**: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`, `commands`
- **Socket Mode**: Must be enabled with App-Level Token

If the bot receives events but doesn't respond, check:
1. Bot is invited to the channel (`/invite @dona`)
2. Events are properly configured in Slack app settings
3. App is reinstalled after permission changes

### Environment Variables

Required for both bots:
- `SLACK_BOT_TOKEN`: Bot User OAuth Token (xoxb-)
- `SLACK_APP_TOKEN`: App-Level Token (xapp-)

For AI bot, at least one LLM provider:
- `OPENROUTER_API_KEY` + `OPENROUTER_MODEL`
- `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL`
- `OPENAI_API_KEY` + `OPENAI_MODEL`

Active provider set via `LLM_PROVIDER` (defaults to "anthropic")

## Common Issues and Solutions

1. **"Mensajes desactivados"**: Bot can send but not receive
   - User must reactivate messaging in DM with bot
   - Click "¿Cómo funciona dona?" and enable messaging

2. **Bot not responding to mentions**:
   - Ensure bot is member of channel
   - Verify `app_mention` event is configured
   - Check logs for "MENCIÓN RECIBIDA" entries

3. **Slash command fails with "dispatch_failed"**:
   - Command must be registered in Slack app config
   - URL can be dummy value with Socket Mode
   - `ack()` must be called within 3 seconds

## Key Design Decisions

1. **Socket Mode over HTTP**: Simplifies deployment, no public URL needed
2. **Multi-LLM support**: Allows cost optimization and fallback options  
3. **Extensive logging**: All events logged with full context for debugging
4. **Sync wrapper for async LLM calls**: Maintains compatibility with Bolt's sync handlers
5. **Configuration-driven prompts**: System prompt customizable via environment