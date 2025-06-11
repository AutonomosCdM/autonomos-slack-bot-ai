"""
Configuración de LLM optimizada para producción - Solo OpenRouter
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ProductionLLMConfig:
    """Configuración simplificada para producción - Solo OpenRouter"""
    
    def __init__(self):
        # Solo OpenRouter en producción
        self.active_provider = "openrouter"
        
        # Configuración de OpenRouter
        self.config = {
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct:free"),
            "max_tokens": int(os.getenv("OPENROUTER_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
            "site_url": os.getenv("OPENROUTER_SITE_URL", "https://slack.com"),
            "app_name": os.getenv("OPENROUTER_APP_NAME", "Dona Bot")
        }
        
        # Prompt del sistema
        self.system_prompt = os.getenv("BOT_SYSTEM_PROMPT", """
Eres Dona, un asistente útil y amigable en Slack para el equipo de Autonomos.
Tus características:
- Eres profesional pero amigable
- Respondes en el mismo idioma que te hablan
- Eres conciso pero completo en tus respuestas
- Puedes ayudar con tareas técnicas y generales
- Si no sabes algo, lo admites honestamente
- Usas emojis de forma moderada para ser más amigable 😊
""").strip()
    
    def get_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de OpenRouter"""
        return self.config
    
    def is_configured(self) -> bool:
        """Verifica si OpenRouter está configurado correctamente"""
        return bool(self.config.get("api_key"))

# Instancia global
llm_config = ProductionLLMConfig()