"""
Manejador de LLM simplificado para producción - Solo OpenRouter
"""

import os
import logging
from typing import Optional, List, Dict, Any
import aiohttp
import asyncio
import re

from llm_config_production import llm_config
from mcp_integration import mcp_integration

logger = logging.getLogger(__name__)

class ProductionLLMHandler:
    """Maneja las llamadas a OpenRouter de forma optimizada para producción"""
    
    def __init__(self):
        self.config = llm_config.get_config()
        
    async def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene una respuesta de OpenRouter con capacidades MCP automáticas
        
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
            # 🔍 DETECCIÓN AUTOMÁTICA: Búsquedas científicas
            scientific_keywords = [
                'paper', 'papers', 'artículo', 'artículos', 'estudio', 'estudios',
                'investigación', 'research', 'arxiv', 'científico', 'científicos',
                'publicación', 'publicaciones', 'journal', 'ieee', 'acm',
                'machine learning', 'deep learning', 'artificial intelligence',
                'inteligencia artificial', 'neural network', 'redes neuronales'
            ]
            
            # Detectar si el usuario busca papers científicos
            if self._detect_scientific_query(message, scientific_keywords):
                logger.info("🔬 Búsqueda científica detectada - usando MCP")
                return await self._handle_scientific_query(message)
            
            # Respuesta normal del LLM
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
    
    def _detect_scientific_query(self, message: str, keywords: List[str]) -> bool:
        """Detecta si el mensaje es una consulta científica"""
        message_lower = message.lower()
        
        # Buscar palabras clave científicas
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        # Patrones específicos de búsqueda
        search_patterns = [
            r'busca.*paper',
            r'encuentra.*artículo',
            r'necesito.*investigación',
            r'qué.*estudios',
            r'hay.*papers.*sobre',
            r'artículos.*sobre',
            r'investigación.*en',
            r'papers.*de'
        ]
        
        for pattern in search_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    async def _handle_scientific_query(self, message: str) -> str:
        """Maneja consultas científicas usando MCP"""
        try:
            # Extraer términos de búsqueda del mensaje
            search_query = self._extract_search_terms(message)
            logger.info(f"🔍 Términos extraídos: {search_query}")
            
            # Inicializar MCP si no está listo
            if not mcp_integration.initialize():
                return "🔧 Error iniciando sistema de búsqueda científica. Intenta más tarde."
            
            # Buscar papers usando MCP
            result = mcp_integration.search_papers(search_query, max_results=5)
            
            if result.get("success") and result.get("papers"):
                papers = result["papers"]
                
                # Formatear respuesta con contexto
                response = f"🔬 **Encontré {len(papers)} papers sobre '{search_query}':**\n\n"
                
                for i, paper in enumerate(papers[:3], 1):  # Máximo 3 para no saturar
                    title = paper.get('title', 'Sin título')
                    authors = paper.get('authors', ['Desconocido'])
                    published = paper.get('published', 'Fecha desconocida')
                    
                    # Tomar solo primeros 2 autores para brevedad
                    author_text = ', '.join(authors[:2])
                    if len(authors) > 2:
                        author_text += f" et al."
                    
                    response += f"**{i}. {title}**\n"
                    response += f"📝 *{author_text}*\n"
                    response += f"📅 {published}\n\n"
                
                # Agregar sugerencia de comandos para más detalles
                response += f"💡 *Usa `/papers {search_query}` para ver más resultados o `/mcp` para opciones avanzadas*"
                
                return response
            else:
                error_msg = result.get("error", "Error desconocido")
                return f"🔍 No encontré papers sobre '{search_query}'. Error: {error_msg}\n\n💡 *Intenta con términos más específicos o en inglés*"
                
        except Exception as e:
            logger.error(f"❌ Error en búsqueda científica: {e}")
            return f"🔧 Error procesando búsqueda científica: {str(e)}\n\n💡 *Puedes intentar con `/papers [tu consulta]`*"
    
    def _extract_search_terms(self, message: str) -> str:
        """Extrae términos de búsqueda del mensaje del usuario"""
        # Remover palabras comunes y obtener términos clave
        stop_words = {
            'busca', 'buscar', 'encuentra', 'encontrar', 'necesito', 'quiero',
            'papers', 'paper', 'artículos', 'artículo', 'sobre', 'acerca', 'de',
            'investigación', 'estudios', 'estudio', 'hay', 'qué', 'cuáles',
            'en', 'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'pero'
        }
        
        # Extraer palabras importantes
        words = re.findall(r'\b\w+\b', message.lower())
        important_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Si no hay palabras importantes, devolver el mensaje limpio
        if not important_words:
            return re.sub(r'[^\w\s]', '', message).strip()
        
        # Unir las palabras más importantes
        search_terms = ' '.join(important_words[:4])  # Máximo 4 términos
        return search_terms

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