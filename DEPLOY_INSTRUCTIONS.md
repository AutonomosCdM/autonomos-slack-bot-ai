# 🚀 Instrucciones de Deployment Manual

Como el CLI no puede usar interfaz interactiva, sigue estos pasos en el dashboard web:

## 📱 Deployment via Dashboard

### 1. Ve al Dashboard de Render
🔗 **URL**: https://dashboard.render.com

### 2. Crear Nuevo Servicio
1. Click **"New +"** → **"Background Worker"**
2. Conectar repositorio: **AutonomosCdM/autonomos-slack-bot-ai**
3. Configurar servicio:

### 3. Configuración del Servicio
```
Service Name: slack-bot-dona-ai
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python start.py
```

### 4. Variables de Entorno (CRÍTICO)
**Agregar estas variables en "Environment" tab:**

#### Tokens de Slack (OBLIGATORIOS):
```
SLACK_BOT_TOKEN = xoxb-tu-bot-token-aqui
SLACK_APP_TOKEN = xapp-tu-app-token-aqui
```
*Usa tus tokens reales de Slack desde el archivo .env*

#### OpenRouter (OBLIGATORIO):
```
OPENROUTER_API_KEY = sk-or-v1-tu-api-key-aqui
```
*Usa tu API key real de OpenRouter*

#### Configuración del Bot (OPCIONAL - ya están en render.yaml):
```
LLM_PROVIDER = openrouter
OPENROUTER_MODEL = meta-llama/llama-3.3-8b-instruct:free
OPENROUTER_MAX_TOKENS = 1000
OPENROUTER_TEMPERATURE = 0.7
LOG_LEVEL = INFO
BOT_SYSTEM_PROMPT = Eres Dona, un asistente útil y amigable en Slack para el equipo de Autonomos.
```

### 5. Deploy!
1. Click **"Create Background Worker"**
2. Render automáticamente:
   - Clona el repo
   - Instala dependencias
   - Inicia el bot con `python start.py`

## 📊 Verificar Deployment

### 1. Revisar Logs
En el dashboard, ve a **Logs** tab y busca:
```
✅ Health check passed
🚀 Iniciando Slack Bot con IA...
✅ Bot conectado exitosamente!
💬 Listo para recibir mensajes
```

### 2. Probar el Bot
Una vez que veas "✅ Bot conectado exitosamente!":
- Ve a Slack
- Menciona: `@dona hola desde Render!`
- El bot debería responder con IA

## ⚠️ Si algo falla:

### Error común: "Variables de entorno faltantes"
- Verifica que agregaste TODAS las variables requeridas
- Los tokens deben estar EXACTOS (sin espacios extra)

### Error: "LLM no configurado"
- Verifica OPENROUTER_API_KEY
- Modelo debe ser: `meta-llama/llama-3.3-8b-instruct:free`

### Error: "Health check failed"
- Revisa logs completos
- Puede ser problema de red (se auto-reintenta)

## 🎉 Una vez funcionando:

El bot estará disponible 24/7 en tu Slack workspace!

**Comandos disponibles:**
- Menciones: `@dona pregunta algo`
- Slash command: `/hello mensaje`
- DMs directos al bot
- `/provider` (en DM) - muestra configuración

**Costo**: ~$7/mes en plan Starter (recomendado para producción)