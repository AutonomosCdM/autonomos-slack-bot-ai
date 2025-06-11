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

# Importar memory manager y canvas
from memory_manager import memory_manager
from canvas_manager import canvas_manager

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
def handle_mention(body, say, client, logger):
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
            # Respuesta con botones interactivos
            say({
                "text": "¡Hola! 👋",
                "blocks": create_help_blocks()
            })
            return
        
        # MEMORIA: Registrar usuario y mensaje
        thread_ts = body["event"].get("thread_ts") or body["event"]["ts"]
        memory_manager.add_user(user)
        memory_manager.log_conversation(
            user_id=user,
            channel_id=channel,
            role="user",
            content=clean_text,
            thread_ts=thread_ts,
            message_ts=body["event"]["ts"]
        )
        
        # MEMORIA: Obtener contexto previo
        context = memory_manager.get_context_for_llm(user, channel, max_messages=10)
        logger.info(f"🧠 Contexto: {len(context)} mensajes")
        
        # Obtener respuesta del LLM con contexto
        response = get_llm_response_sync(clean_text, context=context)
        
        # MEMORIA: Guardar respuesta
        memory_manager.log_conversation(
            user_id=user,
            channel_id=channel,
            role="assistant",
            content=response,
            thread_ts=thread_ts,
            metadata={"provider": llm_config.active_provider}
        )
        
        # QUICK WIN: Responder en hilo si es parte de uno
        if body["event"].get("thread_ts"):
            say(response, thread_ts=body["event"]["thread_ts"])
        else:
            say(response)
        
        # QUICK WIN: Reacción automática según contexto
        try:
            if any(word in clean_text.lower() for word in ['gracias', 'thank']):
                client.reactions_add(
                    channel=channel,
                    timestamp=body["event"]["ts"],
                    name="heart"
                )
            elif any(word in clean_text.lower() for word in ['problema', 'error', 'bug']):
                client.reactions_add(
                    channel=channel,
                    timestamp=body["event"]["ts"],
                    name="wrench"
                )
            elif any(word in clean_text.lower() for word in ['bueno', 'excelente', 'genial']):
                client.reactions_add(
                    channel=channel,
                    timestamp=body["event"]["ts"],
                    name="thumbsup"
                )
        except Exception as reaction_error:
            logger.warning(f"⚠️ Error agregando reacción: {reaction_error}")
        
        logger.info("✅ Respuesta enviada")
        
    except Exception as e:
        logger.error(f"❌ Error en mención: {e}")
        try:
            say("😅 Disculpa, tuve un problema. ¿Podrías intentarlo de nuevo?")
        except:
            pass

# ============================================================================
# QUICK WINS: BOTONES INTERACTIVOS
# ============================================================================

def create_help_blocks():
    """Crea bloques con botones para help menu"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🤖 *¿En qué puedo ayudarte?*\nElige una opción o escríbeme directamente:"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Estado del Bot"
                    },
                    "value": "bot_status",
                    "action_id": "button_bot_status"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🧠 Memoria"
                    },
                    "value": "memory_stats",
                    "action_id": "button_memory_stats"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "💡 Tips de Uso"
                    },
                    "value": "usage_tips",
                    "action_id": "button_usage_tips"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Crear Resumen"
                    },
                    "value": "create_summary",
                    "action_id": "button_create_summary"
                }
            ]
        }
    ]

@app.action("button_bot_status")
def handle_bot_status_button(ack, body, client, logger):
    """Maneja click del botón de estado"""
    try:
        ack()
        user_id = body["user"]["id"]
        
        # Enviar mensaje efímero con estado
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text=f"🟢 *Bot Estado: Activo*\n" +
                 f"🤖 Proveedor: OpenRouter\n" +
                 f"🔧 Modelo: {llm_config.config['model']}\n" +
                 f"💾 Memoria: Activada\n" +
                 f"⚡ Funciones: Todas operativas"
        )
        
        logger.info(f"✅ Estado enviado a {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en botón estado: {e}")

@app.action("button_memory_stats")
def handle_memory_stats_button(ack, body, client, logger):
    """Maneja click del botón de memoria"""
    try:
        ack()
        user_id = body["user"]["id"]
        
        stats = memory_manager.get_memory_stats()
        
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text=f"🧠 *Estadísticas de Memoria*\n" +
                 f"👥 Usuarios: {stats.get('total_users', 0)}\n" +
                 f"💬 Conversaciones: {stats.get('total_conversations', 0)}\n" +
                 f"🎯 Contextos activos: {stats.get('active_contexts', 0)}\n" +
                 f"💾 DB: {stats.get('db_size_mb', 0)} MB"
        )
        
        logger.info(f"✅ Memoria stats enviadas a {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en botón memoria: {e}")

@app.action("button_usage_tips")
def handle_usage_tips_button(ack, body, client, logger):
    """Maneja click del botón de tips"""
    try:
        ack()
        user_id = body["user"]["id"]
        
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text="💡 *Tips de Uso*\n" +
                 "• Menciónala con `@dona` para hacer preguntas\n" +
                 "• Habla en DM para conversaciones privadas\n" +
                 "• Tengo memoria: recuerdo conversaciones anteriores\n" +
                 "• Uso `/memory` para ver estadísticas\n" +
                 "• Respondo en hilos para mantener contexto\n" +
                 "• Reacciono con emojis según el contexto"
        )
        
        logger.info(f"✅ Tips enviados a {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en botón tips: {e}")

@app.action("button_create_summary")
def handle_create_summary_button(ack, body, client, logger):
    """Maneja click del botón de crear resumen"""
    try:
        ack()
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Obtener historial de conversación
        history = memory_manager.get_conversation_history(user_id, channel_id, limit=20)
        
        if len(history) < 3:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="📊 *Necesito más conversación*\n" +
                     "No hay suficiente historial para crear un resumen. " +
                     "Conversa un poco más y luego intenta de nuevo."
            )
            return
        
        # Obtener análisis inteligente
        analysis = memory_manager.get_intelligent_context(
            user_id, channel_id, "crear resumen"
        ).get("analysis", {})
        
        # Crear Canvas de resumen
        canvas_result = canvas_manager.create_conversation_summary(
            client=client,
            channel_id=channel_id,
            conversation_history=history,
            analysis=analysis,
            channel_name=f"Conversación con {user_id}"
        )
        
        if canvas_result.get("success"):
            # Compartir Canvas
            canvas_manager.share_canvas_in_channel(
                client=client,
                canvas_url=canvas_result["canvas_url"],
                channel_id=channel_id,
                title=canvas_result["title"],
                canvas_type="summary"
            )
            
            # Mensaje efímero de confirmación
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"✅ *Canvas creado exitosamente*\n" +
                     f"📊 {canvas_result['title']}\n" +
                     f"🔗 Revisa el Canvas compartido arriba para ver el resumen detallado."
            )
        else:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"❌ *Error creando Canvas*\n" +
                     f"No pude crear el resumen. Error: {canvas_result.get('error', 'Desconocido')}"
            )
        
        logger.info(f"✅ Canvas de resumen procesado para {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en botón resumen: {e}")
        try:
            client.chat_postEphemeral(
                channel=body["channel"]["id"],
                user=body["user"]["id"],
                text="❌ Error interno creando resumen. Intenta más tarde."
            )
        except:
            pass

# ============================================================================
# COMANDO SLASH CON IA
# ============================================================================
@app.command("/hello")
def handle_hello_command(ack, respond, command, logger):
    """Comando slash con IA y botones interactivos"""
    try:
        ack()
        
        user_id = command["user_id"]
        text = command.get("text", "")
        
        logger.info(f"💬 Comando /hello de {user_id}")
        
        if not text:
            # Mostrar menú interactivo
            respond({
                "text": "¡Hola! 👋",
                "blocks": create_help_blocks()
            })
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
# COMANDO SLASH CANVAS
# ============================================================================
@app.command("/canvas")
def handle_canvas_command(ack, body, client, logger, respond):
    """Comando para crear diferentes tipos de Canvas"""
    try:
        ack()
        
        user_id = body["user_id"]
        channel_id = body["channel_id"]
        text = body.get("text", "").strip()
        
        logger.info(f"📄 Comando /canvas de {user_id}: '{text}'")
        
        # Parse comando
        if not text:
            # Mostrar ayuda
            respond({
                "response_type": "ephemeral",
                "text": "📄 *Comando Canvas*\n\n" +
                       "*Uso:*\n" +
                       "• `/canvas resumen` - Crear resumen de conversación\n" +
                       "• `/canvas knowledge [tema]` - Crear base de conocimiento\n" +
                       "• `/canvas proyecto [nombre]` - Documentar proyecto\n\n" +
                       "*Ejemplos:*\n" +
                       "• `/canvas resumen`\n" +
                       "• `/canvas knowledge Python`\n" +
                       "• `/canvas proyecto Nueva Feature`"
            })
            return
        
        parts = text.split(maxsplit=1)
        canvas_type = parts[0].lower()
        
        if canvas_type == "resumen":
            # Crear resumen de conversación
            history = memory_manager.get_conversation_history(user_id, channel_id, limit=25)
            
            if len(history) < 3:
                respond({
                    "response_type": "ephemeral", 
                    "text": "📊 *Necesito más conversación*\n" +
                           "No hay suficiente historial para crear un resumen. " +
                           "Conversa un poco más y luego intenta de nuevo."
                })
                return
            
            analysis = memory_manager.get_intelligent_context(
                user_id, channel_id, "crear resumen canvas"
            ).get("analysis", {})
            
            canvas_result = canvas_manager.create_conversation_summary(
                client=client,
                channel_id=channel_id,
                conversation_history=history,
                analysis=analysis,
                channel_name=f"Canal {channel_id[-4:]}"
            )
            
        elif canvas_type == "knowledge":
            # Crear knowledge base
            topic = parts[1] if len(parts) > 1 else "Nuevo Tema"
            
            canvas_result = canvas_manager.create_knowledge_base(
                client=client,
                topic=topic,
                description=f"Base de conocimiento colaborativa sobre {topic}",
                resources=[],
                tags=[topic.lower()]
            )
            
        elif canvas_type == "proyecto":
            # Crear documentación de proyecto
            project_name = parts[1] if len(parts) > 1 else "Nuevo Proyecto"
            
            canvas_result = canvas_manager.create_project_documentation(
                client=client,
                project_name=project_name,
                objective=f"Documentar y gestionar el proyecto {project_name}",
                requirements=[]
            )
            
        else:
            respond({
                "response_type": "ephemeral",
                "text": f"❌ *Tipo desconocido: '{canvas_type}'*\n\n" +
                       "Tipos válidos: `resumen`, `knowledge`, `proyecto`"
            })
            return
        
        # Procesar resultado
        if canvas_result.get("success"):
            # Compartir Canvas en canal
            canvas_manager.share_canvas_in_channel(
                client=client,
                canvas_url=canvas_result["canvas_url"],
                channel_id=channel_id,
                title=canvas_result["title"],
                canvas_type=canvas_result["type"]
            )
            
            respond({
                "response_type": "ephemeral",
                "text": f"✅ *Canvas creado exitosamente*\n" +
                       f"📄 {canvas_result['title']}\n" +
                       f"🔗 Canvas compartido en el canal para colaboración."
            })
        else:
            respond({
                "response_type": "ephemeral",
                "text": f"❌ *Error creando Canvas*\n" +
                       f"No pude crear el Canvas. Error: {canvas_result.get('error', 'Desconocido')}"
            })
        
        logger.info(f"✅ Comando /canvas procesado: {canvas_type}")
        
    except Exception as e:
        logger.error(f"❌ Error en comando /canvas: {e}")
        try:
            respond("😅 Error procesando comando Canvas. Intenta de nuevo.")
        except:
            pass

# ============================================================================
# MENSAJES DIRECTOS CON IA
# ============================================================================
@app.event("message")
def handle_message_events(body, logger, say, client):
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
            
            # Comando para ver memoria con mensaje efímero
            if text.lower() == "/memory":
                stats = memory_manager.get_memory_stats()
                history = memory_manager.get_conversation_history(user, limit=5)
                
                # QUICK WIN: Mensaje efímero (solo visible para el usuario)
                client.chat_postEphemeral(
                    channel=event.get("channel"),
                    user=user,
                    text=f"🧠 **Estadísticas de Memoria**\n" +
                         f"👥 Usuarios: {stats.get('total_users', 0)}\n" +
                         f"💬 Conversaciones: {stats.get('total_conversations', 0)}\n" +
                         f"🎯 Contextos activos: {stats.get('active_contexts', 0)}\n" +
                         f"💾 DB: {stats.get('db_size_mb', 0)} MB\n" +
                         f"📚 Últimas {len(history)} conversaciones registradas"
                )
                return
            
            # MEMORIA: Registrar mensaje
            memory_manager.add_user(user)
            memory_manager.log_conversation(
                user_id=user,
                channel_id=event.get("channel"),
                role="user",
                content=text,
                message_ts=event.get("ts")
            )
            
            # MEMORIA: Obtener contexto
            context = memory_manager.get_context_for_llm(user, event.get("channel"), max_messages=10)
            logger.info(f"🧠 Contexto DM: {len(context)} mensajes")
            
            # Respuesta con IA y contexto
            response = get_llm_response_sync(text, context=context)
            
            # MEMORIA: Guardar respuesta
            memory_manager.log_conversation(
                user_id=user,
                channel_id=event.get("channel"),
                role="assistant",
                content=response,
                metadata={"provider": llm_config.active_provider}
            )
            
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