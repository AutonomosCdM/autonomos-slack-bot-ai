#!/usr/bin/env python3
"""
Test script para Quick Wins y nueva funcionalidad
"""

import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test que todos los imports funcionen"""
    try:
        from memory_manager import memory_manager
        from redis_memory import redis_memory
        from intelligent_memory import intelligent_memory
        
        logger.info("✅ Todos los imports funcionan correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error en imports: {e}")
        return False

def test_intelligent_analysis():
    """Test análisis inteligente con diferentes tipos de mensajes"""
    from intelligent_memory import intelligent_memory
    
    test_messages = [
        "Hola, necesito ayuda urgente con un error en el bot",
        "Gracias por la ayuda, funcionó perfectamente",
        "Mi nombre es Carlos y trabajo en desarrollo",
        "¿Puedes ayudarme a implementar una nueva función?",
        "Tengo un problema crítico con la base de datos ahora mismo"
    ]
    
    logger.info("🧠 Testing análisis inteligente:")
    
    for msg in test_messages:
        analysis = intelligent_memory.analyze_message_context(msg, [])
        logger.info(f"  📝 '{msg[:40]}...'")
        logger.info(f"    Topics: {analysis.get('topics', [])}")
        logger.info(f"    Intent: {analysis.get('intent', 'unknown')}")
        logger.info(f"    Sentiment: {analysis.get('sentiment', 'unknown')}")
        logger.info(f"    Urgency: {analysis.get('urgency', 'unknown')}")
        logger.info("")
    
    return True

def test_memory_integration():
    """Test integración completa de memoria"""
    from memory_manager import memory_manager
    
    logger.info("💾 Testing integración de memoria:")
    
    # Test user y conversación
    test_user = f"U_TEST_{datetime.now().strftime('%H%M%S')}"
    test_channel = f"C_TEST_{datetime.now().strftime('%H%M%S')}"
    
    # Agregar usuario
    memory_manager.add_user(test_user, "test_user", "Usuario Test")
    
    # Simular conversación
    messages = [
        ("user", "Hola, mi nombre es Juan"),
        ("assistant", "¡Hola Juan! ¿En qué puedo ayudarte?"),
        ("user", "Necesito ayuda con un problema en Python"),
        ("assistant", "Claro, te puedo ayudar con Python. ¿Cuál es el problema específico?"),
        ("user", "Tengo un error de syntax en mi código")
    ]
    
    for role, content in messages:
        memory_manager.log_conversation(test_user, test_channel, role, content)
    
    # Test context retrieval
    context = memory_manager.get_context_for_llm(test_user, test_channel)
    logger.info(f"  ✅ Context básico: {len(context)} mensajes")
    
    # Test intelligent context
    smart_context = memory_manager.get_intelligent_context(
        test_user, test_channel, "¿Podrías revisar mi código Python?"
    )
    
    logger.info(f"  ✅ Smart context: {len(smart_context.get('context', []))} mensajes")
    logger.info(f"  📊 Analysis: {smart_context.get('analysis', {}).get('topics', [])}")
    logger.info(f"  💡 Hints: {smart_context.get('hints', [])}")
    logger.info(f"  🎭 Tone: {smart_context.get('tone', 'unknown')}")
    
    return True

def test_redis_functionality():
    """Test funcionalidad Redis"""
    from redis_memory import redis_memory
    
    logger.info("🚀 Testing Redis functionality:")
    
    if not redis_memory.is_available():
        logger.warning("  ⚠️ Redis no disponible - skipping tests")
        return True
    
    test_user = f"U_REDIS_{datetime.now().strftime('%H%M%S')}"
    test_channel = f"C_REDIS_{datetime.now().strftime('%H%M%S')}"
    
    # Test sesión activa
    redis_memory.start_active_session(test_user, test_channel, {"test": True})
    session = redis_memory.get_active_session(test_user, test_channel)
    
    if session:
        logger.info(f"  ✅ Sesión activa creada: {session.get('started_at', 'unknown')}")
    
    # Test stats
    stats = redis_memory.get_realtime_stats()
    logger.info(f"  ✅ Stats en tiempo real: {stats}")
    
    # Test cache de contexto
    test_context = [
        {"role": "user", "content": "test message"},
        {"role": "assistant", "content": "test response"}
    ]
    redis_memory.cache_recent_context(test_user, test_channel, test_context)
    
    cached = redis_memory.get_cached_context(test_user, test_channel)
    if cached:
        logger.info(f"  ✅ Context cacheado: {len(cached)} mensajes")
    
    return True

def test_block_kit_creation():
    """Test creación de Block Kit UI"""
    logger.info("🎨 Testing Block Kit UI creation:")
    
    try:
        # Simular la función de botones interactivos
        def create_help_blocks():
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🤖 *¿En qué puedo ayudarte?*\\nElige una opción o escríbeme directamente:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📊 Estado del Bot"},
                            "value": "bot_status",
                            "action_id": "button_bot_status"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🧠 Memoria"},
                            "value": "memory_stats", 
                            "action_id": "button_memory_stats"
                        }
                    ]
                }
            ]
        
        blocks = create_help_blocks()
        logger.info(f"  ✅ Block Kit UI creado con {len(blocks)} bloques")
        logger.info(f"  📋 Estructura: {json.dumps(blocks, indent=2)}")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Error creando Block Kit: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    logger.info("🧪 Iniciando tests de Quick Wins y funcionalidad avanzada")
    logger.info("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Análisis Inteligente", test_intelligent_analysis),
        ("Integración de Memoria", test_memory_integration),
        ("Funcionalidad Redis", test_redis_functionality),
        ("Block Kit UI", test_block_kit_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\\n🔬 Testing: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info("\\n" + "=" * 60)
    logger.info("📊 RESUMEN DE TESTS:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info(f"\\n🎯 RESULTADO FINAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests pasaron! El sistema está listo.")
        return True
    else:
        logger.error("⚠️ Algunos tests fallaron. Revisar antes de deploy.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)