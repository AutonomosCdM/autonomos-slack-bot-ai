"""
Manejador de LLM simplificado para producción - Solo OpenRouter
"""

import os
import logging
from typing import Optional, List, Dict, Any
import aiohttp
import asyncio

from llm_config_production import llm_config

logger = logging.getLogger(__name__)

class ProductionLLMHandler:
    """Maneja las llamadas a OpenRouter de forma optimizada para producción"""
    
    def __init__(self):
        self.config = llm_config.get_config()
        
    async def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene una respuesta de OpenRouter
        
        Args:
            message: El mensaje del usuario
            context: Historial de conversación opcional
            
        Returns:
            La respuesta del LLM
        """
        
        if not self.config.get("api_key"):
            return "❌ Bot no configurado correctamente. Contacta al administrador."
        
        logger.info(f"🤖 Procesando mensaje: {message[:100]}...")
        
        try:
            return await self._call_openrouter(message, context)
                
        except Exception as e:
            logger.error(f"❌ Error llamando a OpenRouter: {e}")
            return "😅 Disculpa, tuve un problema técnico. ¿Podrías repetir tu pregunta?"
    
    async def _call_openrouter(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Llama a la API de OpenRouter con manejo robusto de errores"""
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "HTTP-Referer": self.config.get("site_url", "https://slack.com"),
            "X-Title": self.config.get("app_name", "Dona Bot"),
            "Content-Type": "application/json"
        }
        
        # Construir mensajes
        messages = [{"role": "system", "content": llm_config.system_prompt}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"]
        }
        
        # Timeout más largo para requests en producción
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result["choices"][0]["message"]["content"]
                        logger.info("✅ Respuesta recibida de OpenRouter")
                        return response_text
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error HTTP {response.status}: {error_text}")
                        
                        # Respuestas específicas según el error
                        if response.status == 429:
                            return "⏳ El servicio está muy ocupado. Intenta de nuevo en unos segundos."
                        elif response.status == 401:
                            return "🔐 Error de autenticación. Contacta al administrador."
                        else:
                            return "🔧 Error del servicio. Intenta de nuevo más tarde."
                            
        except asyncio.TimeoutError:
            logger.error("⏰ Timeout en request a OpenRouter")
            return "⏰ La respuesta está tardando mucho. Intenta con una pregunta más simple."
        except Exception as e:
            logger.error(f"💥 Error inesperado: {e}")
            return "💥 Error inesperado. Intenta de nuevo."

# Para uso síncrono en el bot
def get_llm_response_sync(message: str, context: Optional[List[Dict]] = None) -> str:
    """Versión síncrona optimizada para producción"""
    handler = ProductionLLMHandler()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(handler.get_response(message, context))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"💥 Error en wrapper síncrono: {e}")
        return "😅 Error interno. Por favor intenta de nuevo."