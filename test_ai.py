#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que OpenRouter funciona
"""

import asyncio
from llm_handler import LLMHandler
from llm_config import llm_config

async def test_openrouter():
    print("🧪 Probando OpenRouter con Llama 3.3...")
    print(f"📡 Proveedor activo: {llm_config.active_provider}")
    print(f"🤖 Modelo: {llm_config.get_active_config()['model']}")
    
    handler = LLMHandler()
    
    # Prueba simple
    test_message = "Hola! Dime un dato curioso sobre los gatos en una sola línea."
    print(f"\n💬 Pregunta: {test_message}")
    
    response = await handler.get_response(test_message)
    print(f"🤖 Respuesta: {response}")
    
    # Prueba con contexto
    print("\n--- Prueba con contexto ---")
    context = [
        {"role": "user", "content": "Mi nombre es Carlos"},
        {"role": "assistant", "content": "¡Hola Carlos! Es un placer conocerte."}
    ]
    
    test_message2 = "¿Recuerdas mi nombre?"
    print(f"💬 Pregunta: {test_message2}")
    
    response2 = await handler.get_response(test_message2, context)
    print(f"🤖 Respuesta: {response2}")

if __name__ == "__main__":
    print("=" * 50)
    print("TEST DE OPENROUTER CON LLAMA 3.3")
    print("=" * 50)
    
    asyncio.run(test_openrouter())
    
    print("\n✅ Test completado!")