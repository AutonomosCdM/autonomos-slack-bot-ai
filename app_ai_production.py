#!/usr/bin/env python3
"""
Slack Bot con IA optimizado para producción en Render
Solo OpenRouter - Sin debugging extenso
"""

import os
import logging
from slack_bolt import App
from dotenv import load_dotenv

# Importar handlers de producción
from llm_handler_production import get_llm_response_sync
from llm_config_production import llm_config

# Cargar variables de entorno
load_dotenv()

# Configurar logging para producción
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Inicializar la app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# ============================================================================
# MANEJO DE MENCIONES (@bot) CON IA
# ============================================================================
@app.event("app_mention")
def handle_mention(body, say, logger):
    """Responde a menciones con IA"""
    try:
        user = body["event"]["user"]
        text = body["event"]["text"]
        channel = body["event"]["channel"]
        
        logger.info(f"📢 Mención de {user} en {channel}")
        
        # Limpiar mención del bot
        clean_text = text
        if "<@" in text:
            # Remover todas las menciones del texto
            import re
            clean_text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        if not clean_text:
            say("¡Hola! 👋 ¿En qué puedo ayudarte?")
            return
        
        # Obtener respuesta del LLM
        response = get_llm_response_sync(clean_text)
        say(response)
        
        logger.info("✅ Respuesta enviada")
        
    except Exception as e:
        logger.error(f"❌ Error en mención: {e}")
        try:
            say("😅 Disculpa, tuve un problema. ¿Podrías intentarlo de nuevo?")
        except:
            pass

# ============================================================================
# COMANDO SLASH CON IA
# ============================================================================
@app.command("/hello")
def handle_hello_command(ack, respond, command, logger):
    """Comando slash con IA"""
    try:
        ack()
        
        user_id = command["user_id"]
        text = command.get("text", "")
        
        logger.info(f"💬 Comando /hello de {user_id}")
        
        if not text:
            respond("¡Hola! 👋 Usa `/hello [tu mensaje]` y te responderé con IA.")
            return
        
        # Obtener respuesta del LLM
        response = get_llm_response_sync(text)
        respond(response)
        
        logger.info("✅ Comando procesado")
        
    except Exception as e:
        logger.error(f"❌ Error en comando: {e}")
        try:
            respond("😅 Error procesando comando. Intenta de nuevo.")
        except:
            pass

# ============================================================================
# MENSAJES DIRECTOS CON IA
# ============================================================================
@app.event("message")
def handle_message_events(body, logger, say):
    """Maneja mensajes directos con IA"""
    try:
        event = body.get("event", {})
        
        # Ignorar mensajes del bot
        if event.get("bot_id"):
            return
        
        channel_type = event.get("channel_type")
        
        # Solo DMs
        if channel_type == "im":
            user = event.get("user")
            text = event.get("text", "")
            
            logger.info(f"📨 DM de {user}")
            
            if not text:
                return
            
            # Comando especial para ver proveedor
            if text.lower() == "/provider":
                say(f"🤖 **Proveedor activo**: OpenRouter\n" +
                    f"🔧 **Modelo**: {llm_config.config['model']}")
                return
            
            # Respuesta con IA
            response = get_llm_response_sync(text)
            say(response)
            
            logger.info("✅ DM respondido")
        
    except Exception as e:
        logger.error(f"❌ Error en mensaje: {e}")

# ============================================================================
# MANEJO DE ERRORES GLOBALES
# ============================================================================
@app.error
def global_error_handler(error, body, logger):
    """Maneja errores globales"""
    logger.error(f"💥 Error global: {error}")

# ============================================================================
# HEALTH CHECK ENDPOINT (para monitoreo)
# ============================================================================
def health_check():
    """Verifica que el bot esté funcionando"""
    try:
        # Verificar configuración
        if not llm_config.is_configured():
            return False
        
        # Verificar tokens de Slack
        required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
        if not all(os.getenv(var) for var in required_vars):
            return False
            
        return True
    except:
        return False

# ============================================================================
# INICIALIZACIÓN
# ============================================================================
if __name__ == "__main__":
    logger.error("❌ No ejecutes este archivo directamente.")
    logger.error("🚀 Usa: python start.py")
    exit(1)