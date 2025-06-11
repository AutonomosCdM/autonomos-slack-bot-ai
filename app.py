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
        
        # Responder en el canal con botones interactivos
        # Si es parte de un hilo, responder en el hilo
        thread_ts = body["event"].get("thread_ts") or body["event"]["ts"]
        say_with_feedback_buttons(say, response, user, thread_ts)
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
        
        # Responder con botones de feedback
        respond_with_feedback_buttons(respond, response, user_id)
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
            
            # En DMs, usar botones de feedback simples
            say_with_feedback_buttons(say, response, user)
            logger.info("✅ Respuesta enviada")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.exception("Stack trace:")

# ============================================================================
# FUNCIONALIDADES INTERACTIVAS
# ============================================================================

def say_with_feedback_buttons(say_func, message, user_id, thread_ts=None):
    """Envía mensaje con botones de feedback"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👍 Útil",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": f"helpful_{user_id}",
                    "action_id": "feedback_helpful"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👎 No útil",
                        "emoji": True
                    },
                    "value": f"not_helpful_{user_id}",
                    "action_id": "feedback_not_helpful"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Regenerar",
                        "emoji": True
                    },
                    "value": f"regenerate_{user_id}",
                    "action_id": "regenerate_response"
                }
            ]
        }
    ]
    
    # Si hay thread_ts, responder en el hilo
    if thread_ts:
        say_func(blocks=blocks, thread_ts=thread_ts)
    else:
        say_func(blocks=blocks)

def respond_with_feedback_buttons(respond_func, message, user_id):
    """Responde a comando slash con botones de feedback"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👍 Útil",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": f"helpful_{user_id}",
                    "action_id": "feedback_helpful"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👎 No útil",
                        "emoji": True
                    },
                    "value": f"not_helpful_{user_id}",
                    "action_id": "feedback_not_helpful"
                }
            ]
        }
    ]
    respond_func(blocks=blocks)

# Manejadores de botones interactivos
@app.action("feedback_helpful")
def handle_helpful_feedback(ack, body, logger):
    """Maneja feedback positivo"""
    ack()
    user_id = body["user"]["id"]
    logger.info(f"👍 Feedback positivo de {user_id}")
    
    # Actualizar el mensaje para mostrar que se registró el feedback
    try:
        # Mensaje ephemeral de confirmación
        app.client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text="¡Gracias por tu feedback positivo! 😊 Esto me ayuda a mejorar."
        )
    except Exception as e:
        logger.error(f"Error enviando confirmación: {e}")

@app.action("feedback_not_helpful")
def handle_not_helpful_feedback(ack, body, logger):
    """Maneja feedback negativo"""
    ack()
    user_id = body["user"]["id"]
    logger.info(f"👎 Feedback negativo de {user_id}")
    
    try:
        # Mensaje ephemeral pidiendo más detalles
        app.client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text="Gracias por el feedback. ¿Puedes decirme qué puedo mejorar? Envíame un DM con más detalles. 🤔"
        )
    except Exception as e:
        logger.error(f"Error enviando seguimiento: {e}")

@app.action("regenerate_response")
def handle_regenerate_response(ack, body, logger):
    """Regenera la respuesta"""
    ack()
    user_id = body["user"]["id"]
    logger.info(f"🔄 Regenerando respuesta para {user_id}")
    
    try:
        # Mensaje ephemeral mientras regenera
        app.client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text="🔄 Regenerando respuesta... Un momento por favor."
        )
        
        # Aquí podrías implementar regeneración con el último mensaje
        # Por ahora, respuesta simple
        app.client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text="Para regenerar, menciona nuevamente @dona con tu pregunta. Próximamente mejoraré esto. 😅"
        )
    except Exception as e:
        logger.error(f"Error regenerando: {e}")

# Manejo de reacciones
@app.event("reaction_added")
def handle_reaction_added(event, logger):
    """Responde a reacciones específicas"""
    try:
        reaction = event.get("reaction")
        user = event.get("user")
        channel = event.get("item", {}).get("channel")
        
        logger.info(f"👍 Reacción {reaction} de {user} en {channel}")
        
        # Responder a reacciones específicas
        if reaction == "wave":
            app.client.chat_postMessage(
                channel=channel,
                text=f"¡Hola <@{user}>! 👋 ¿En qué puedo ayudarte?"
            )
        elif reaction == "question":
            app.client.chat_postEphemeral(
                channel=channel,
                user=user,
                text="¿Tienes una pregunta? Menciona @dona seguido de tu pregunta y te ayudo. 🤔"
            )
        elif reaction == "heavy_check_mark":
            app.client.chat_postEphemeral(
                channel=channel,
                user=user,
                text="¡Genial! Me alegra que hayas marcado esto como completado. ✅"
            )
        
    except Exception as e:
        logger.error(f"Error manejando reacción: {e}")

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