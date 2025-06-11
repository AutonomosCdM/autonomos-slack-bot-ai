#!/usr/bin/env python3
"""
Script para enviar un mensaje de prueba al canal #it_autonomos
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear cliente
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

try:
    # Enviar mensaje al canal #it_autonomos
    response = client.chat_postMessage(
        channel="#it_autonomos",
        text="🤖 ¡Hola! Soy el bot Dona y estoy funcionando correctamente.\n\nPuedes probar:\n• Mencionarme: @dona hola\n• Comando slash: /hello mundo\n• Enviarme un DM\n\n✅ Bot operativo y listo para usar!"
    )
    
    print("✅ Mensaje enviado exitosamente!")
    print(f"📍 Canal: #{response['channel']}")
    print(f"🕐 Timestamp: {response['ts']}")
    
except Exception as e:
    print(f"❌ Error enviando mensaje: {e}")
    print("🔍 Verifica que el bot esté invitado al canal #it_autonomos")
    print("💡 Invita el bot con: /invite @dona")