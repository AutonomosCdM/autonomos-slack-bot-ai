"""
Manejador de LLMs para el bot de Slack
Abstrae la comunicación con diferentes proveedores de IA
"""

import os
import logging
from typing import Optional, List, Dict, Any
import aiohttp
import json

from llm_config import llm_config

logger = logging.getLogger(__name__)

class LLMHandler:
    """Maneja las llamadas a diferentes LLMs de forma unificada"""
    
    def __init__(self):
        self.config = llm_config
        
    async def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene una respuesta del LLM activo
        
        Args:
            message: El mensaje del usuario
            context: Historial de conversación opcional
            
        Returns:
            La respuesta del LLM
        """
        provider = self.config.active_provider
        
        logger.info(f"🤖 Usando proveedor: {provider}")
        logger.info(f"📝 Mensaje: {message}")
        
        try:
            if provider == "anthropic":
                return await self._call_anthropic(message, context)
            elif provider == "openrouter":
                return await self._call_openrouter(message, context)
            elif provider == "openai":
                return await self._call_openai(message, context)
            else:
                return "❌ Proveedor de IA no configurado correctamente."
                
        except Exception as e:
            logger.error(f"Error llamando a {provider}: {e}")
            return f"😅 Ups, tuve un problema técnico. ¿Podrías repetir tu pregunta?"
    
    async def _call_anthropic(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Llama a la API de Anthropic"""
        config = self.config.get_active_config()
        
        if not config.get("api_key"):
            return "❌ API key de Anthropic no configurada."
        
        headers = {
            "x-api-key": config["api_key"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Construir mensajes
        messages = []
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": config["model"],
            "messages": messages,
            "system": self.config.system_prompt,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["content"][0]["text"]
                else:
                    error = await response.text()
                    logger.error(f"Error de Anthropic: {error}")
                    return "❌ Error al comunicarse con Anthropic."
    
    async def _call_openrouter(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Llama a la API de OpenRouter"""
        config = self.config.get_active_config()
        
        if not config.get("api_key"):
            return "❌ API key de OpenRouter no configurada."
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "HTTP-Referer": config.get("site_url", "https://slack.com"),
            "X-Title": config.get("app_name", "Dona Bot"),
            "Content-Type": "application/json"
        }
        
        # Construir mensajes
        messages = [{"role": "system", "content": self.config.system_prompt}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": config["model"],
            "messages": messages,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    logger.error(f"Error de OpenRouter: {error}")
                    return "❌ Error al comunicarse con OpenRouter."
    
    async def _call_openai(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Llama a la API de OpenAI"""
        config = self.config.get_active_config()
        
        if not config.get("api_key"):
            return "❌ API key de OpenAI no configurada."
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Construir mensajes
        messages = [{"role": "system", "content": self.config.system_prompt}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": config["model"],
            "messages": messages,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    logger.error(f"Error de OpenAI: {error}")
                    return "❌ Error al comunicarse con OpenAI."

# Para uso síncrono en el bot
import asyncio

def get_llm_response_sync(message: str, context: Optional[List[Dict]] = None) -> str:
    """Versión síncrona para usar en el bot de Slack"""
    handler = LLMHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(handler.get_response(message, context))
    finally:
        loop.close()