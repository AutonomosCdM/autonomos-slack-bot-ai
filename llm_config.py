"""
Configuración de LLMs para el bot de Slack
Soporta múltiples proveedores: Anthropic, OpenRouter, OpenAI
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    OPENAI = "openai"

class LLMConfig:
    """Configuración centralizada para múltiples LLMs"""
    
    def __init__(self):
        # Proveedor activo (puede cambiarse dinámicamente)
        self.active_provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        # Configuraciones por proveedor
        self.configs = {
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000")),
                "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
            },
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku"),
                "max_tokens": int(os.getenv("OPENROUTER_MAX_TOKENS", "1000")),
                "temperature": float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
                "site_url": os.getenv("OPENROUTER_SITE_URL", "https://slack.com"),
                "app_name": os.getenv("OPENROUTER_APP_NAME", "Dona Bot")
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            }
        }
        
        # Prompt del sistema compartido
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
    
    def get_active_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del proveedor activo"""
        return self.configs.get(self.active_provider, {})
    
    def switch_provider(self, provider: str) -> bool:
        """Cambia el proveedor activo"""
        if provider.lower() in self.configs:
            self.active_provider = provider.lower()
            return True
        return False
    
    def is_configured(self, provider: Optional[str] = None) -> bool:
        """Verifica si un proveedor está configurado correctamente"""
        target = provider.lower() if provider else self.active_provider
        config = self.configs.get(target, {})
        return bool(config.get("api_key"))

# Instancia global de configuración
llm_config = LLMConfig()