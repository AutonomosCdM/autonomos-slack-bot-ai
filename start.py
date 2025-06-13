#!/usr/bin/env python3
"""
Script de inicio robusto para producción en Render
Maneja reconexiones automáticas y logging optimizado
"""

import os
import sys
import time
import signal
import logging
from typing import Optional
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging para producción
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Variable global para manejo de shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Maneja señales de shutdown gracefully"""
    global shutdown_requested
    logger.info(f"🛑 Señal recibida: {signum}. Iniciando shutdown graceful...")
    shutdown_requested = True

def validate_environment() -> bool:
    """Valida que todas las variables de entorno necesarias estén configuradas"""
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN", 
        "OPENROUTER_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        return False
    
    return True

def create_bot_app():
    """Crea la instancia del bot"""
    # Import aquí para evitar problemas con variables de entorno
    from app_ai_production import app
    return app

def run_bot_with_retry(max_retries: int = 5, retry_delay: int = 30) -> None:
    """
    Ejecuta el bot con reintentos automáticos en caso de desconexión
    """
    global shutdown_requested
    
    app = create_bot_app()
    
    # Inicializar monitor de salud MCP
    try:
        from mcp_integration import mcp_integration
        from mcp_health_monitor import initialize_health_monitor
        
        monitor = initialize_health_monitor(mcp_integration)
        monitor.start_monitoring(interval=300)  # Check cada 5 minutos
        logger.info("🔍 MCP Health Monitor iniciado")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo inicializar MCP Health Monitor: {e}")
    
    retry_count = 0
    
    while not shutdown_requested and retry_count < max_retries:
        try:
            logger.info("🚀 Iniciando Slack Bot con IA...")
            logger.info("🤖 Proveedor: OpenRouter (Llama 3.3)")
            logger.info("📡 Modo: Socket Mode")
            
            # Crear handler de Socket Mode
            handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
            
            logger.info("✅ Bot conectado exitosamente!")
            logger.info("💬 Listo para recibir mensajes")
            
            # Resetear contador de reintentos en conexión exitosa
            retry_count = 0
            
            # Iniciar el bot (esto bloquea hasta desconexión)
            handler.start()
            
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción manual detectada")
            shutdown_requested = True
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"❌ Error en conexión del bot (intento {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries and not shutdown_requested:
                logger.info(f"🔄 Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                logger.error("💀 Máximo número de reintentos alcanzado")
                break
    
    logger.info("🏁 Bot detenido")

def health_check() -> bool:
    """Verifica que el bot esté configurado correctamente"""
    try:
        # Verificar que podemos importar el módulo del bot
        import app_ai_production
        
        # Verificar configuración de LLM
        from llm_config_production import llm_config
        if not llm_config.is_configured():
            logger.error("❌ LLM no configurado correctamente")
            return False
            
        logger.info("✅ Health check passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def main():
    """Función principal con manejo completo de errores"""
    
    # Configurar handlers de señales
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("=" * 50)
    logger.info("🤖 DONA BOT - INICIANDO EN RENDER")
    logger.info("=" * 50)
    
    # 1. Validar variables de entorno
    if not validate_environment():
        logger.error("💥 Fallo en validación de entorno")
        sys.exit(1)
    
    # 2. Health check
    if not health_check():
        logger.error("💥 Fallo en health check")
        sys.exit(1)
    
    # 3. Ejecutar bot con reintentos
    try:
        run_bot_with_retry()
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
        sys.exit(1)
    
    logger.info("👋 Shutdown completado")

if __name__ == "__main__":
    main()