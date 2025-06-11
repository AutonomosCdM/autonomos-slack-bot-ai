# 🚀 Deployment en Render

Guía completa para desplegar el bot de Slack con IA en Render.

## 📋 Pre-requisitos

1. **Cuenta en Render**: [render.com](https://render.com)
2. **Render CLI instalado**: `render --version` debe funcionar
3. **API Keys configuradas**:
   - Tokens de Slack (bot y app)
   - API key de OpenRouter

## 🔧 Archivos de Producción

El deployment usa versiones optimizadas:
- `start.py` - Script de inicio robusto con reintentos
- `app_ai_production.py` - Bot optimizado (menos logs)
- `llm_config_production.py` - Solo OpenRouter
- `llm_handler_production.py` - Manejo de errores mejorado
- `render.yaml` - Configuración Infrastructure as Code

## 🚀 Deployment Steps

### 1. Login a Render
```bash
render login
```

### 2. Deploy desde repositorio
```bash
# Opción A: Deploy automático con render.yaml
render services create --config render.yaml

# Opción B: Deploy manual via CLI
render services create
# Seleccionar: Background Worker
# Runtime: Python
# Build: pip install -r requirements.txt
# Start: python start.py
```

### 3. Configurar variables de entorno
```bash
# Tokens de Slack (OBLIGATORIOS)
render env set SLACK_BOT_TOKEN=xoxb-your-token --service-name slack-bot-dona-ai
render env set SLACK_APP_TOKEN=xapp-your-token --service-name slack-bot-dona-ai

# OpenRouter (OBLIGATORIO)
render env set OPENROUTER_API_KEY=sk-or-v1-your-key --service-name slack-bot-dona-ai
```

**⚠️ IMPORTANTE**: Las variables con valores sensibles NO están en `render.yaml` por seguridad.

### 4. Verificar deployment
```bash
# Ver logs en tiempo real
render logs --service-name slack-bot-dona-ai --follow

# Ver estado del servicio
render services list
```

## 📊 Monitoring

### Logs importantes a verificar:
```
✅ Health check passed
🚀 Iniciando Slack Bot con IA...
✅ Bot conectado exitosamente!
💬 Listo para recibir mensajes
```

### Errores comunes:
```
❌ Variables de entorno faltantes
❌ LLM no configurado correctamente
❌ Error en conexión del bot
```

## 🔄 Updates

Para actualizar el bot:

```bash
# Commit cambios
git add .
git commit -m "Update bot"
git push

# Render detecta automáticamente y redeploya
# O forzar redeploy:
render deploy --service-name slack-bot-dona-ai
```

## 💰 Costos

- **Plan Starter**: $7/mes (recomendado para producción)
- **Plan Free**: Disponible pero con limitaciones de horas

## 🔧 Configuración Avanzada

### Variables disponibles en render.yaml:
```yaml
# Configuración del bot
LLM_PROVIDER: openrouter
OPENROUTER_MODEL: meta-llama/llama-3.3-8b-instruct:free
LOG_LEVEL: INFO  # Menos verbose en producción

# Personalización
BOT_SYSTEM_PROMPT: "Tu prompt personalizado..."
OPENROUTER_APP_NAME: "Dona Bot"
```

### Escalabilidad:
- Background Worker maneja múltiples canales simultáneamente
- Socket Mode es eficiente para bots de equipos pequeños/medianos
- Para equipos grandes, considerar migrar a webhook mode

## 🆘 Troubleshooting

### Bot no responde:
1. Verificar logs: `render logs --follow`
2. Verificar que está corriendo: `render services list`
3. Verificar variables de entorno en dashboard

### Errores de API:
- **429 (Rate Limit)**: Llama 3.3 free tiene límites, esperar o upgradar
- **401 (Auth)**: Verificar OPENROUTER_API_KEY
- **Timeout**: Red lenta, debería auto-reintentar

### Desconexiones:
- Socket Mode se reconecta automáticamente
- Script `start.py` incluye reintentos automáticos
- Render reinicia el servicio si se cierra

## 📱 Comandos del Bot en Producción

Una vez desplegado, el bot responde a:
- Menciones: `@dona pregunta algo`
- Comando slash: `/hello mensaje`
- DMs directos
- Comando especial: `/provider` (muestra configuración actual)