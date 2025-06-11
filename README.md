# 🤖 Slack Bot con Bolt para Python

Un bot de Slack funcional y listo para usar que utiliza Socket Mode (no requiere URL pública).

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar o descargar este proyecto
cd autonomos_dona

# Crear entorno virtual (ALTAMENTE RECOMENDADO)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar la App de Slack

#### Paso 1: Crear la App en Slack
1. Ve a [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Nombre: `Mi Bot` (o como quieras)
4. Workspace: Selecciona tu workspace

#### Paso 2: Configurar Socket Mode
1. En **"Socket Mode"** → **Enable Socket Mode**
2. En **"App-Level Tokens"** → **Generate Token and Scopes**
   - Token Name: `socket-token`
   - Scope: `connections:write`
   - **Copia el token** (comienza con `xapp-`)

#### Paso 3: Configurar Permisos del Bot
1. En **"OAuth & Permissions"** → **Bot Token Scopes**
2. Añade estos scopes:
   ```
   app_mentions:read    - Para responder a menciones
   channels:history     - Para leer mensajes en canales
   chat:write          - Para enviar mensajes
   im:history          - Para leer DMs
   im:read             - Para recibir DMs
   im:write            - Para responder DMs
   commands            - Para comandos slash
   ```

#### Paso 4: Instalar el Bot
1. En **"OAuth & Permissions"** → **Install to Workspace**
2. **Copia el Bot User OAuth Token** (comienza con `xoxb-`)

#### Paso 5: Registrar Comando Slash
1. En **"Slash Commands"** → **Create New Command**
2. Command: `/hello`
3. Request URL: `https://cualquier-cosa.com` (no importa con Socket Mode)
4. Description: `Saluda al bot`

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tus tokens
nano .env  # o usa tu editor favorito
```

Tu archivo `.env` debe verse así:
```
SLACK_BOT_TOKEN=xoxb-tu-token-del-bot-aqui
SLACK_APP_TOKEN=xapp-tu-token-de-app-aqui
```

### 4. Ejecutar el Bot

```bash
# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Cargar variables de entorno y ejecutar
python app.py
```

Deberías ver:
```
🚀 Iniciando Slack Bot...
📡 Usando Socket Mode (no necesita URL pública)
🔗 Conectando a Slack...
✅ Bot conectado exitosamente!
💬 El bot está listo para recibir mensajes
```

## 🎯 Características del Bot

### ✅ Responde a Menciones
```
@tu-bot ¡hola!
```
El bot responderá en el mismo canal.

### ✅ Comando Slash
```
/hello mundo
```
Responde con un mensaje personalizado.

### ✅ Mensajes Directos
Envía un DM al bot y responderá automáticamente.

### ✅ Manejo de Errores
El bot no se rompe por errores inesperados.

## 🔧 Troubleshooting

### ❌ "Error: Las siguientes variables de entorno no están configuradas"

**Problema:** El archivo `.env` no existe o no se está cargando.

**Solución:**
```bash
# Verificar que el archivo existe
ls -la .env

# Si no existe, crearlo desde el ejemplo
cp .env.example .env

# Editar con tus tokens reales
nano .env
```

### ❌ "slack_bolt.error.BoltError: A valid app-level token is required"

**Problema:** El `SLACK_APP_TOKEN` es incorrecto o falta.

**Solución:**
1. Ve a [api.slack.com/apps](https://api.slack.com/apps) → Tu App
2. **App-Level Tokens** → Crear nuevo si no existe
3. Scope: `connections:write`
4. Copia el token completo (comienza con `xapp-`)

### ❌ "slack_sdk.errors.SlackApiError: invalid_auth"

**Problema:** El `SLACK_BOT_TOKEN` es incorrecto.

**Solución:**
1. Ve a **OAuth & Permissions**
2. Copia el **Bot User OAuth Token** (comienza con `xoxb-`)
3. Asegúrate de que el bot esté instalado en el workspace

### ❌ El comando `/hello` no funciona

**Problema:** No está registrado o mal configurado.

**Solución:**
1. Ve a **Slash Commands** en tu app
2. Crear **New Command**: `/hello`
3. Request URL: `https://example.com` (no importa)
4. **Reinstalar la app** si es necesario

### ❌ El bot no responde a menciones

**Problema:** Faltan permisos o no está en el canal.

**Solución:**
1. Verificar scopes en **OAuth & Permissions**:
   - `app_mentions:read`
   - `chat:write`
2. **Invitar el bot al canal**: `/invite @tu-bot`

### ❌ "ModuleNotFoundError: No module named 'slack_bolt'"

**Problema:** Dependencias no instaladas o entorno virtual no activo.

**Solución:**
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep slack
```

## 🚨 Por Qué Esta "Maldita Cosa" Es Difícil de Hacer Funcionar

### 1. **Tokens Confusos**
Slack tiene **2 tipos de tokens** diferentes:
- **Bot Token** (`xoxb-`): Para que el bot haga cosas
- **App Token** (`xapp-`): Para Socket Mode

**La gente se confunde** porque antes solo había Bot Tokens.

### 2. **Socket Mode vs HTTP**
- **HTTP Mode**: Necesita URL pública (ngrok, etc.) - MÁS COMPLEJO
- **Socket Mode**: Conexión directa - MÁS SIMPLE

**Este proyecto usa Socket Mode** para evitar complicaciones.

### 3. **Permisos (Scopes) Exactos**
Si falta **un solo scope**, el bot falla silenciosamente.

**Lista exacta necesaria:**
```
app_mentions:read
channels:history  
chat:write
im:history
im:read
im:write
commands
```

### 4. **Variables de Entorno**
Python no carga `.env` automáticamente. Este proyecto usa `python-dotenv` para solucionarlo.

### 5. **Comando Slash Phantom**
Debes **registrar** `/hello` en la interfaz web, aunque uses Socket Mode.

### 6. **Reinstalación Necesaria**
Cambiar permisos requiere **reinstalar** la app en el workspace.

## 📁 Estructura del Proyecto

```
autonomos_dona/
├── app.py              # Bot principal
├── requirements.txt    # Dependencias
├── .env.example       # Plantilla de configuración
├── .env               # Tu configuración (NO comitear)
├── .gitignore         # Archivos a ignorar
└── README.md          # Esta documentación
```

## 🛡️ Seguridad

- **NUNCA** comitas el archivo `.env`
- Los tokens son como **contraseñas** - protégelos
- Usa entornos virtuales para aislar dependencias

## 📚 Recursos Adicionales

- [Bolt Python Docs](https://slack.dev/bolt-python/)
- [Slack API Docs](https://api.slack.com/)
- [Socket Mode Guide](https://api.slack.com/apis/connections/socket)

## 🐛 Reportar Problemas

Si encuentras problemas:
1. Revisa la sección **Troubleshooting**
2. Verifica que seguiste **todos** los pasos
3. Revisa los logs con `LOG_LEVEL=DEBUG`

---

**¡Este bot debería funcionar siguiendo exactamente estos pasos!** 🎉