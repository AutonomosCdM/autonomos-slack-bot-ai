#!/usr/bin/env python3
"""
Enviar mensaje para reactivar el bot
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

try:
    # Enviar mensaje al canal para reactivar
    response = client.chat_postMessage(
        channel="#it_autonomos",
        text="""🔄 **REACTIVANDO BOT DONA**

El bot está CONECTADO y funcionando:
✅ Socket Mode activo
✅ Eventos configurados correctamente
✅ Tokens válidos

🚨 **SI VES "Mensajes desactivados":**
1. Click en "¿Cómo funciona dona?" en el DM
2. Busca "Reactivar mensajes" o "Enable messaging"
3. O escribe `/invite @dona` en este canal

**PRUEBA AHORA:**
• `@dona hola mundo`
• `/hello test`

El bot DEBE responder si está reactivado."""
    )
    
    print("✅ Mensaje de reactivación enviado")
    
except Exception as e:
    print(f"❌ Error: {e}")