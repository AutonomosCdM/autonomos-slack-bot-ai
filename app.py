#!/usr/bin/env python3
"""
Slack Bot usando Bolt para Python con Socket Mode
Bot funcional con capacidades básicas de respuesta a menciones, comandos slash y mensajes directos.
"""

import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging para debugging
logging.basicConfig(level=logging.DEBUG)

# Inicializar la app con el token del bot
# CRITICAL: Asegúrate de que SLACK_BOT_TOKEN esté configurado correctamente
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# ============================================================================
# MANEJO DE MENCIONES (@bot)
# ============================================================================
@app.event("app_mention")
def handle_mention(body, say, logger):
    """
    Responde cuando el bot es mencionado en cualquier canal.
    Ejemplo: @dona hola
    """
    try:
        # Logging extenso para debugging
        logger.info("===============================")
        logger.info("🔍 MENCIÓN RECIBIDA")
        logger.info(f"Evento completo: {body}")
        logger.info(f"Tipo de evento: {body.get('event', {}).get('type')}")
        logger.info(f"Usuario: {body.get('event', {}).get('user')}")
        logger.info(f"Texto: {body.get('event', {}).get('text')}")
        logger.info(f"Canal: {body.get('event', {}).get('channel')}")
        logger.info("===============================")
        
        user = body["event"]["user"]
        text = body["event"]["text"]
        channel = body["event"]["channel"]
        
        logger.info(f"Mención recibida de {user} en {channel}: {text}")
        
        # Respuesta simple a menciones
        say(f"¡Hola <@{user}>! 👋 Escuché que me mencionaste. ¿En qué puedo ayudarte?")
        logger.info("✅ Respuesta enviada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error manejando mención: {e}")
        logger.exception("Stack trace completo:")
        try:
            say("¡Hola! Hubo un pequeño error, pero estoy aquí 🤖")
        except Exception as say_error:
            logger.error(f"❌ Error enviando respuesta de error: {say_error}")

# ============================================================================
# COMANDO SLASH BÁSICO
# ============================================================================
@app.command("/hello")
def handle_hello_command(ack, respond, command, logger):
    """
    Maneja el comando slash /hello
    IMPORTANTE: Debes registrar este comando en tu app de Slack en api.slack.com
    """
    try:
        # Acknowledgment DEBE ser lo primero (menos de 3 segundos)
        ack()
        
        # Logging completo
        logger.info("===============================")
        logger.info("🔍 COMANDO /hello RECIBIDO")
        logger.info(f"Comando completo: {command}")
        logger.info(f"Usuario ID: {command.get('user_id')}")
        logger.info(f"Texto: {command.get('text', '')}")
        logger.info(f"Canal ID: {command.get('channel_id')}")
        logger.info("===============================")
        
        user_id = command["user_id"]
        text = command.get("text", "")
        
        # Respuesta al comando
        if text:
            respond(f"¡Hola <@{user_id}>! Dijiste: *{text}* 🎉")
        else:
            respond(f"¡Hola <@{user_id}>! Usa `/hello [mensaje]` para que pueda responder algo específico 😊")
            
        logger.info("✅ Comando procesado exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error manejando comando /hello: {e}")
        logger.exception("Stack trace completo:")
        # Intenta responder aunque haya un error
        try:
            respond("¡Ups! Ocurrió un error procesando el comando.")
        except:
            pass

# ============================================================================
# MANEJO DE MENSAJES DIRECTOS
# ============================================================================
@app.event("message")
def handle_message_events(body, logger, say):
    """
    Maneja todos los eventos de tipo mensaje.
    """
    try:
        logger.info("===============================")
        logger.info("🔍 MENSAJE RECIBIDO")
        logger.info(f"Evento completo: {body}")
        
        event = body.get("event", {})
        channel_type = event.get("channel_type")
        user = event.get("user")
        text = event.get("text", "")
        
        logger.info(f"Canal tipo: {channel_type}")
        logger.info(f"Usuario: {user}")
        logger.info(f"Texto: {text}")
        logger.info("===============================")
        
        # Ignorar mensajes del propio bot
        if event.get("bot_id"):
            logger.info("Ignorando mensaje de bot")
            return
            
        # Respuesta según tipo de canal
        if channel_type == "im":
            logger.info("📨 Procesando mensaje directo")
            
            # Respuesta inteligente básica
            if "hola" in text.lower():
                say("¡Hola! ¿Cómo estás? 👋")
            elif "ayuda" in text.lower():
                say("""
¡Puedo ayudarte! Aquí tienes algunas cosas que puedo hacer:

• Mencióname en cualquier canal: `@dona mensaje`
• Usa el comando slash: `/hello [mensaje]`
• Envíame un mensaje directo como este
• Pregúntame cualquier cosa 🤖
                """)
            elif "adiós" in text.lower() or "bye" in text.lower():
                say("¡Hasta luego! Que tengas un buen día 👋")
            else:
                say(f"Recibí tu mensaje: *{text}*\n\nEscribe 'ayuda' para ver qué puedo hacer 🤖")
            
            logger.info("✅ Respuesta a DM enviada")
        
    except Exception as e:
        logger.error(f"❌ Error manejando mensaje: {e}")
        logger.exception("Stack trace completo:")

# ============================================================================
# MANEJO DE ERRORES GLOBALES
# ============================================================================
@app.error
def global_error_handler(error, body, logger):
    """
    Maneja errores globales del bot para evitar crashes.
    CRÍTICO: Esto evita que el bot se rompa por errores inesperados.
    """
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")

# ============================================================================
# INICIALIZACIÓN Y EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    # Verificar que las variables de entorno estén configuradas
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ ERROR: Las siguientes variables de entorno no están configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Revisa tu archivo .env y asegúrate de que esté cargado correctamente.")
        exit(1)
    
    print("🚀 Iniciando Slack Bot...")
    print("📡 Usando Socket Mode (no necesita URL pública)")
    print("🔗 Conectando a Slack...")
    
    try:
        # Socket Mode Handler - NO necesita ngrok ni URL pública
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        
        print("✅ Bot conectado exitosamente!")
        print("💬 El bot está listo para recibir mensajes")
        print("🛑 Presiona Ctrl+C para detener el bot")
        
        # Iniciar el bot
        handler.start()
        
    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")
        print("🔍 Revisa la sección de troubleshooting en el README")
        exit(1)