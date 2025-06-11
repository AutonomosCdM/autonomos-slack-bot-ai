#!/usr/bin/env python3
"""
Envío simple de mensaje al canal #it_autonomos
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear cliente
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

try:
    # Enviar mensaje al canal
    response = client.chat_postMessage(
        channel="#it_autonomos",
        text="""🤖 **Bot Dona está funcionando correctamente!**

**Para que pueda responder a menciones, necesitas:**

1️⃣ **Invitarme al canal**: 
   • Escribe en este canal: `/invite @dona`
   • O ve a "View channel details" → "Members" → "Add people" → busca "dona"

2️⃣ **Probar las funciones**:
   • Mención: `@dona hola mundo`
   • Comando slash: `/hello esto es una prueba`
   • Mensaje directo: Abre DM conmigo

3️⃣ **Si el comando `/hello` no existe**:
   • Ve a https://api.slack.com/apps
   • Busca tu app → "Slash Commands" → "Create New Command"
   • Command: `/hello`
   • URL: `https://example.com` (no importa con Socket Mode)

🚀 **Estado actual: Bot conectado y operativo via Socket Mode**
📡 **Logs del servidor muestran conexión exitosa**"""
    )
    
    print("✅ Instrucciones enviadas al canal #it_autonomos")
    print(f"📍 Mensaje ID: {response['ts']}")
    
except Exception as e:
    print(f"❌ Error: {e}")