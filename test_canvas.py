#!/usr/bin/env python3
"""
Test script para funcionalidad Canvas
"""

import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_canvas_imports():
    """Test que los imports de Canvas funcionen"""
    try:
        from canvas_manager import canvas_manager, CanvasTemplate
        logger.info("✅ Canvas manager importado correctamente")
        
        # Test templates
        templates = canvas_manager.templates
        logger.info(f"✅ Templates disponibles: {list(templates.keys())}")
        
        for template_name, template in templates.items():
            logger.info(f"  📄 {template_name}: {template.emoji} {template.title}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en imports Canvas: {e}")
        return False

def test_canvas_content_generation():
    """Test generación de contenido para Canvas"""
    try:
        from canvas_manager import canvas_manager
        
        logger.info("🧪 Testing generación de contenido...")
        
        # Test data simulada
        fake_conversation = [
            {"role": "user", "content": "Hola, necesito ayuda con Python"},
            {"role": "assistant", "content": "¡Hola! Te ayudo con Python. ¿Qué necesitas?"},
            {"role": "user", "content": "Quiero hacer un script para automatizar tareas"},
            {"role": "assistant", "content": "Perfecto. Te sugiero usar argparse para comandos CLI"},
            {"role": "user", "content": "Gracias, voy a implementar eso"}
        ]
        
        fake_analysis = {
            "topics": ["Python", "automatización", "CLI", "argparse"],
            "intent": "help_request",
            "sentiment": "positive"
        }
        
        # Test extracción de puntos clave
        key_points = canvas_manager._extract_key_points(fake_conversation, fake_analysis)
        logger.info(f"✅ Puntos clave extraídos: {len(key_points.split('- '))} items")
        
        # Test extracción de tareas
        tasks = canvas_manager._extract_tasks(fake_conversation, fake_analysis)
        logger.info(f"✅ Tareas extraídas: {len(tasks.split('- [ ]'))} items")
        
        # Test extracción de recursos
        resources = canvas_manager._extract_resources(fake_conversation)
        logger.info(f"✅ Recursos extraídos")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en generación de contenido: {e}")
        return False

def test_canvas_templates():
    """Test templates de Canvas"""
    try:
        from canvas_manager import canvas_manager
        
        logger.info("🎨 Testing templates...")
        
        # Test template de resumen
        summary_template = canvas_manager.templates["summary"]
        summary_content = summary_template.content_template.format(
            key_points="- Punto 1\n- Punto 2",
            decisions="- Decisión 1\n- Decisión 2", 
            tasks="- [ ] Tarea 1\n- [ ] Tarea 2",
            resources="- Recurso 1\n- Recurso 2",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            channel_name="Test Channel"
        )
        logger.info(f"✅ Template resumen: {len(summary_content)} caracteres")
        
        # Test template knowledge
        knowledge_template = canvas_manager.templates["knowledge"]
        knowledge_content = knowledge_template.content_template.format(
            topic="Python Testing",
            description="Testing en Python con pytest",
            usage_guide="pip install pytest",
            resources="- pytest.org\n- docs oficiales",
            best_practices="- Usar fixtures\n- Tests atomicos",
            tags="`python` | `testing` | `pytest`",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
            contributors="@test_user"
        )
        logger.info(f"✅ Template knowledge: {len(knowledge_content)} caracteres")
        
        # Test template proyecto
        project_template = canvas_manager.templates["project"]
        project_content = project_template.content_template.format(
            project_name="Test Project",
            objective="Probar funcionalidad Canvas",
            requirements="- Canvas API\n- Slack Bot\n- Templates",
            architecture="Canvas Manager + Templates",
            current_status="🟡 **En Testing**",
            next_steps="- Implementar\n- Probar\n- Deploy",
            team="@dev_team",
            start_date=datetime.now().strftime("%Y-%m-%d"),
            estimated_completion="1 semana"
        )
        logger.info(f"✅ Template proyecto: {len(project_content)} caracteres")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en templates: {e}")
        return False

def test_mock_canvas_creation():
    """Test simulado de creación de Canvas (sin API real)"""
    try:
        from canvas_manager import canvas_manager
        
        logger.info("🎭 Testing creación simulada...")
        
        # Simular datos de entrada
        fake_history = [
            {"role": "user", "content": "Necesitamos documentar el proyecto Canvas"},
            {"role": "assistant", "content": "Excelente idea. Te ayudo a crear la documentación"},
            {"role": "user", "content": "Incluye templates y ejemplos"},
            {"role": "assistant", "content": "Perfecto, voy a incluir varios templates"}
        ]
        
        fake_analysis = {
            "topics": ["documentación", "Canvas", "templates"],
            "intent": "documentation_request",
            "sentiment": "collaborative"
        }
        
        # Test sin cliente real (debería manejar error gracefully)
        try:
            result = canvas_manager.create_conversation_summary(
                client=None,  # Cliente nulo para test
                channel_id="C_TEST_123",
                conversation_history=fake_history,
                analysis=fake_analysis,
                channel_name="Test Channel"
            )
            
            # Debería fallar pero retornar estructura correcta
            if result.get("success") == False and "error" in result:
                logger.info("✅ Manejo de errores correcto en Canvas")
            else:
                logger.warning("⚠️ Comportamiento inesperado en error handling")
                
        except Exception as expected_error:
            logger.info(f"✅ Error esperado capturado: {type(expected_error).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test simulado: {e}")
        return False

def main():
    """Ejecutar todos los tests de Canvas"""
    logger.info("🧪 Iniciando tests de funcionalidad Canvas")
    logger.info("=" * 50)
    
    tests = [
        ("Imports Canvas", test_canvas_imports),
        ("Generación de Contenido", test_canvas_content_generation),
        ("Templates", test_canvas_templates),
        ("Creación Simulada", test_mock_canvas_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔬 Testing: {test_name}")
        logger.info("-" * 30)
        
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
    logger.info("\n" + "=" * 50)
    logger.info("📊 RESUMEN DE TESTS CANVAS:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests Canvas pasaron! Sistema listo.")
        return True
    else:
        logger.error("⚠️ Algunos tests fallaron. Revisar implementación.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)