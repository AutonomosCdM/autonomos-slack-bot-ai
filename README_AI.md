# 🤖 Slack Bot con IA Multi-LLM

Bot de Slack inteligente que soporta múltiples proveedores de IA (Anthropic, OpenRouter, OpenAI).

## 🌟 Características

- ✅ **Multi-LLM**: Cambia entre Anthropic, OpenRouter y OpenAI dinámicamente
- ✅ **Respuestas inteligentes**: No más respuestas pre-hechas
- ✅ **Socket Mode**: No requiere URL pública
- ✅ **Comandos especiales**: Cambia de proveedor en tiempo real

## 🚀 Instalación Rápida

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus claves
```

Necesitas configurar:
- **Tokens de Slack** (como antes)
- **Al menos un proveedor de IA**:
  - Anthropic: `ANTHROPIC_API_KEY`
  - OpenRouter: `OPENROUTER_API_KEY`
  - OpenAI: `OPENAI_API_KEY`

### 3. Ejecutar el bot con IA

```bash
python app_ai.py
```

## 🔧 Configuración de Proveedores

### Anthropic (Claude)
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_MODEL=claude-3-haiku-20240307  # o claude-3-opus-20240229
```

### OpenRouter
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=anthropic/claude-3-haiku  # o cualquier modelo disponible
```

### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-3.5-turbo  # o gpt-4
```

## 💬 Comandos Especiales

En mensajes directos al bot:
- `/provider` - Ver qué LLM está activo
- `/switch anthropic` - Cambiar a Anthropic
- `/switch openrouter` - Cambiar a OpenRouter
- `/switch openai` - Cambiar a OpenAI

## 🎯 Uso

1. **Menciones**: `@dona explícame qué es Docker`
2. **Comandos**: `/hello cuéntame un chiste`
3. **DMs**: Envía cualquier mensaje directo

## 📝 Personalizar el Bot

Edita `BOT_SYSTEM_PROMPT` en `.env` para cambiar la personalidad:

```env
BOT_SYSTEM_PROMPT="Eres un asistente técnico experto en DevOps y cloud computing..."
```

## 🔍 Debugging

Los logs muestran:
- 🤖 Qué proveedor está usando
- 📝 El mensaje procesado
- ✅ Confirmación de respuesta
- ❌ Errores detallados

## 🚨 Solución de Problemas

### "API key no configurada"
Verifica que hayas configurado la API key del proveedor activo en `.env`

### "Error al comunicarse con [Proveedor]"
- Verifica tu conexión a internet
- Confirma que la API key es válida
- Revisa los límites de tu cuenta

### Cambiar proveedor no funciona
Asegúrate de que el nuevo proveedor tenga su API key configurada

## 🎉 ¡Disfruta tu bot inteligente!

Ahora Dona puede:
- Responder preguntas complejas
- Mantener conversaciones contextuales
- Ayudar con tareas técnicas
- ¡Y mucho más!