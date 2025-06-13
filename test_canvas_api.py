#!/usr/bin/env python3
"""
Test directo de Canvas API para debugging
"""

import os
import logging
from slack_bolt import App
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_canvas_api_direct():
    """Test directo de Canvas API"""
    try:
        # Crear app de Slack
        app = App(token=os.getenv("SLACK_BOT_TOKEN"))
        
        logger.info("🔗 Conexión Slack establecida")
        
        # Contenido de prueba simple
        test_content = """# 🧪 Test Canvas
        
Este es un Canvas de prueba para verificar la API.

## ✅ Funcionalidades
- Creación automática
- Contenido markdown
- Integración Slack

---
*Generado por test_canvas_api.py*
"""
        
        logger.info("🎨 Intentando crear Canvas de prueba...")
        
        # Intentar crear Canvas
        response = app.client.canvases_create(
            document_content={
                "type": "markdown",
                "markdown": test_content
            }
        )
        
        logger.info(f"📋 Response completa: {response}")
        
        # Verificar response
        if response:
            canvas_id = response.get("canvas_id")
            canvas_url = response.get("url") 
            
            if canvas_id:
                logger.info(f"✅ Canvas creado exitosamente!")
                logger.info(f"🆔 Canvas ID: {canvas_id}")
                logger.info(f"🔗 Canvas URL: {canvas_url}")
                
                # Verificar si el Canvas existe
                try:
                    canvas_info = app.client.canvases_sections_lookup(canvas_id=canvas_id)
                    logger.info(f"✅ Canvas verificado: {canvas_info}")
                except Exception as verify_error:
                    logger.warning(f"⚠️ No se pudo verificar Canvas: {verify_error}")
                
                return True
            else:
                logger.error("❌ Response sin canvas_id")
                return False
        else:
            logger.error("❌ Response vacía")
            return False
            
    except Exception as e:
        logger.error(f"💥 Error en test Canvas API: {e}")
        logger.error(f"💥 Tipo de error: {type(e).__name__}")
        
        # Verificar permisos específicos
        if "missing_scope" in str(e):
            logger.error("🔒 Error de permisos - Verificar scope 'canvases:write'")
        elif "invalid_auth" in str(e):
            logger.error("🔑 Error de autenticación - Verificar tokens")
        
        return False

def test_permissions():
    """Test básico de permisos y conexión"""
    try:
        app = App(token=os.getenv("SLACK_BOT_TOKEN"))
        
        # Test básico de auth
        auth_test = app.client.auth_test()
        logger.info(f"🔐 Auth test: {auth_test}")
        
        # Verificar scopes
        scopes = auth_test.get("response_metadata", {}).get("scopes", [])
        logger.info(f"🎯 Scopes disponibles: {scopes}")
        
        if "canvases:write" in scopes:
            logger.info("✅ Scope canvases:write disponible")
        else:
            logger.error("❌ Scope canvases:write NO disponible")
            logger.error("🔧 Actualizar manifest y reinstalar app")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando permisos: {e}")
        return False

def main():
    """Ejecutar tests de Canvas API"""
    logger.info("🧪 Testing Canvas API directamente")
    logger.info("=" * 50)
    
    # Test 1: Permisos
    logger.info("\n🔒 Test 1: Verificando permisos...")
    perms_ok = test_permissions()
    
    if not perms_ok:
        logger.error("❌ Test de permisos falló - abortando")
        return False
    
    # Test 2: Canvas API
    logger.info("\n🎨 Test 2: Canvas API...")
    canvas_ok = test_canvas_api_direct()
    
    if canvas_ok:
        logger.info("\n🎉 ¡Canvas API funciona correctamente!")
        return True
    else:
        logger.error("\n💥 Canvas API tiene problemas")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)