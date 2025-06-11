#!/usr/bin/env python3
"""
Script para configurar y probar el bot en el canal #it_autonomos
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear cliente
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

def get_bot_info():
    """Obtener información del bot"""
    try:
        response = client.auth_test()
        return response['user_id'], response['user']
    except Exception as e:
        print(f"❌ Error obteniendo info del bot: {e}")
        return None, None

def invite_bot_to_channel(channel_name):
    """Invitar bot al canal"""
    try:
        bot_id, bot_name = get_bot_info()
        if not bot_id:
            return False
            
        # Buscar el canal
        channels = client.conversations_list(types="public_channel,private_channel")
        channel_id = None
        
        for channel in channels['channels']:
            if channel['name'] == channel_name.replace('#', ''):
                channel_id = channel['id']
                break
        
        if not channel_id:
            print(f"❌ Canal {channel_name} no encontrado")
            return False
        
        # Invitar bot al canal
        try:
            client.conversations_invite(channel=channel_id, users=bot_id)
            print(f"✅ Bot invitado al canal {channel_name}")
            return True
        except Exception as e:
            if "already_in_channel" in str(e):
                print(f"ℹ️ Bot ya está en el canal {channel_name}")
                return True
            else:
                print(f"❌ Error invitando bot: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error en invite_bot_to_channel: {e}")
        return False

def send_test_message(channel_name):
    """Enviar mensaje de prueba"""
    try:
        response = client.chat_postMessage(
            channel=channel_name,
            text="""🤖 **Bot Dona - Prueba de Funcionamiento**

✅ **Conexión exitosa**
📡 Socket Mode activo
🔧 Listo para recibir comandos

**Prueba estas funciones:**
• Mencióneme: `@dona hola`
• Comando slash: `/hello mensaje`
• Envíame un DM

🚀 **Estado: OPERATIVO**"""
        )
        
        print(f"✅ Mensaje de prueba enviado a {channel_name}")
        return response['ts']
        
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return None

def main():
    """Función principal"""
    print("🔧 Configurando bot Dona...")
    
    # 1. Obtener info del bot
    bot_id, bot_name = get_bot_info()
    if bot_id:
        print(f"🤖 Bot detectado: {bot_name} (ID: {bot_id})")
    else:
        print("❌ No se pudo obtener información del bot")
        return
    
    # 2. Invitar bot al canal
    channel = "it_autonomos"
    print(f"📥 Invitando bot al canal #{channel}...")
    invite_success = invite_bot_to_channel(channel)
    
    # 3. Enviar mensaje de prueba
    if invite_success:
        print("📤 Enviando mensaje de prueba...")
        msg_ts = send_test_message(f"#{channel}")
        
        if msg_ts:
            print("\n🎉 **CONFIGURACIÓN COMPLETA**")
            print(f"✅ Bot está en #{channel}")
            print("✅ Mensaje de prueba enviado")
            print(f"\n💡 **Próximos pasos:**")
            print(f"1. Ve al canal #{channel} en Slack")
            print(f"2. Menciona el bot: @{bot_name} hola")
            print(f"3. Prueba el comando: /hello mundo")
    
    print("\n🔍 **Debug Info:**")
    print(f"Bot ID: {bot_id}")
    print(f"Bot Name: {bot_name}")

if __name__ == "__main__":
    main()