#!/usr/bin/env python3
"""
Slack Bot con IA usando Bolt para Python con Socket Mode
Soporta múltiples LLMs: Anthropic, OpenRouter, OpenAI
"""

import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Importar el manejador de LLM
from llm_handler import get_llm_response_sync
from llm_config import llm_config

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging para debugging
logging.basicConfig(level=logging.DEBUG)

# Inicializar la app con el token del bot
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# ============================================================================
# MANEJO DE MENCIONES (@bot) CON IA
# ============================================================================
@app.event("app_mention")
def handle_mention(body, say, logger):
    """
    Responde cuando el bot es mencionado usando IA
    """
    try:
        logger.info("===============================")
        logger.info("🔍 MENCIÓN RECIBIDA")
        
        user = body["event"]["user"]
        text = body["event"]["text"]
        channel = body["event"]["channel"]
        
        logger.info(f"Usuario: {user}, Canal: {channel}")
        logger.info(f"Texto: {text}")
        
        # Limpiar el mensaje (quitar la mención del bot)
        # El texto incluye <@BOTID> al inicio, lo removemos
        bot_id = body["event"].get("bot_id") or body["authorizations"][0]["user_id"]
        clean_text = text.replace(f"<@{bot_id}>", "").strip()
        
        if not clean_text:
            say("¡Hola! 👋 ¿En qué puedo ayudarte? Puedes preguntarme cualquier cosa.")
            return
        
        # Obtener respuesta del LLM
        logger.info(f"🤖 Enviando a LLM: {clean_text}")
        logger.info(f"📡 Proveedor activo: {llm_config.active_provider}")
        
        response = get_llm_response_sync(clean_text)
        
        # Responder en el canal
        say(response)
        logger.info("✅ Respuesta enviada")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.exception("Stack trace:")
        say("😅 Disculpa, tuve un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?")

# ============================================================================
# COMANDO SLASH CON IA
# ============================================================================
@app.command("/hello")
def handle_hello_command(ack, respond, command, logger):
    """
    Maneja el comando slash /hello con respuestas inteligentes
    """
    try:
        ack()
        
        logger.info("===============================")
        logger.info("🔍 COMANDO /hello RECIBIDO")
        
        user_id = command["user_id"]
        text = command.get("text", "")
        
        if not text:
            respond("¡Hola! 👋 Usa `/hello [tu mensaje]` y te responderé con IA.")
            return
        
        # Obtener respuesta del LLM
        logger.info(f"🤖 Procesando con IA: {text}")
        response = get_llm_response_sync(text)
        
        respond(response)
        logger.info("✅ Comando procesado")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        respond("😅 Hubo un error procesando tu comando. Intenta de nuevo.")

# ============================================================================
# MENSAJES DIRECTOS CON IA
# ============================================================================
@app.event("message")
def handle_message_events(body, logger, say):
    """
    Maneja mensajes directos con respuestas de IA
    """
    try:
        event = body.get("event", {})
        
        # Ignorar mensajes del propio bot
        if event.get("bot_id"):
            return
        
        channel_type = event.get("channel_type")
        
        # Solo procesar DMs
        if channel_type == "im":
            logger.info("===============================")
            logger.info("📨 MENSAJE DIRECTO RECIBIDO")
            
            user = event.get("user")
            text = event.get("text", "")
            
            logger.info(f"Usuario: {user}")
            logger.info(f"Texto: {text}")
            
            if not text:
                return
            
            # Comandos especiales
            if text.lower() == "/provider":
                say(f"🤖 Proveedor actual: **{llm_config.active_provider}**\n" +
                    "Disponibles: anthropic, openrouter, openai\n" +
                    "Usa `/switch [provider]` para cambiar.")
                return
            
            if text.lower().startswith("/switch "):
                provider = text[8:].strip()
                if llm_config.switch_provider(provider):
                    say(f"✅ Cambiado a: **{provider}**")
                else:
                    say(f"❌ Proveedor no válido. Usa: anthropic, openrouter, o openai")
                return
            
            # Respuesta con IA
            logger.info(f"🤖 Procesando con {llm_config.active_provider}")
            response = get_llm_response_sync(text)
            
            say(response)
            logger.info("✅ Respuesta enviada")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.exception("Stack trace:")

# ============================================================================
# MANEJO DE ERRORES GLOBALES
# ============================================================================
@app.error
def global_error_handler(error, body, logger):
    """
    Maneja errores globales del bot
    """
    logger.exception(f"Error global: {error}")
    logger.info(f"Body: {body}")

# ============================================================================
# INICIALIZACIÓN Y EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    # Verificar variables de entorno de Slack
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ ERROR: Variables de Slack no configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        exit(1)
    
    # Verificar que al menos un LLM esté configurado
    providers_status = {
        "anthropic": llm_config.is_configured("anthropic"),
        "openrouter": llm_config.is_configured("openrouter"),
        "openai": llm_config.is_configured("openai")
    }
    
    print("🤖 Estado de proveedores de IA:")
    for provider, configured in providers_status.items():
        status = "✅ Configurado" if configured else "❌ No configurado"
        print(f"   {provider}: {status}")
    
    if not any(providers_status.values()):
        print("\n❌ ERROR: Ningún proveedor de IA está configurado.")
        print("Configura al menos uno en tu archivo .env")
        exit(1)
    
    print(f"\n🚀 Iniciando Slack Bot con IA...")
    print(f"🤖 Proveedor activo: {llm_config.active_provider}")
    print(f"📡 Usando Socket Mode")
    
    try:
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        
        print("✅ Bot conectado exitosamente!")
        print("💬 El bot está listo para conversaciones inteligentes")
        print("\n💡 Comandos especiales en DM:")
        print("   /provider - Ver proveedor actual")
        print("   /switch [provider] - Cambiar proveedor")
        print("\n🛑 Presiona Ctrl+C para detener")
        
        handler.start()
        
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        exit(1)