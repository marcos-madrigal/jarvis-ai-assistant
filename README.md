### 🤖 J.A.R.V.I.S. — Asistente Personal de Voz y Productividad (Local-First)

Asistente personal modular impulsado por **Ollama** (modelos de lenguaje locales), con síntesis de voz en tiempo real, memoria conversacional persistente en SQLite, interfaz web e integración directa con **Gmail** y **Apple iCloud Calendar**.

---

### ✨ Características Principales
- **Razonamiento con LLMs Locales (`Ollama`):** Ejecuta inferencia en local con Llama 3.1 sin latencia de APIs externas ni coste por tokens, manteniendo prompts de sistema estructurados y contexto conversacional.
- **Memoria Persistente (`SQLite`):** Gestor de memoria propio (`memoria.py`) que almacena el historial de conversaciones y el contexto del usuario en una base de datos relacional local (`jarvis_memoria.db`).
- **Síntesis y Reconocimiento de Voz (`Edge-TTS`):** Generación de voz neuronal natural (`voz.py`) y escucha por micrófono para interacción manos libres.
- **Ejecución de Acciones e Integraciones:**
  - **Integración con Gmail (`gmail.py`):** Lectura, búsqueda, resumen y envío de correos autenticados mediante OAuth2 con las APIs de Google.
  - **Apple iCloud Calendar (`calendario.py`):** Integración mediante protocolo CalDAV con contraseñas de aplicación para consultar, crear y eliminar eventos.
  - **Despachador de Comandos (`ejecutor.py`):** Enrutador modular de intenciones que traduce órdenes en lenguaje natural a acciones del sistema (temporizadores, aplicaciones de Windows, búsquedas y gestión de agenda/correo).
- **Interfaz Web (`Flask`):** Panel ligero en navegador (`app.py` + `templates/index.html`) para interactuar con el asistente.

---

### 🛠️ Stack Tecnológico
- **Núcleo e IA:** Python 3.13, Ollama (Llama 3.1)
- **Backend e Interfaz:** Flask, HTML5, CSS3, JavaScript
- **Voz y Audio:** `edge-tts`, `SpeechRecognition`, `pygame`
- **APIs y Protocolos:** Google Gmail API (OAuth2), Apple iCloud Calendar (CalDAV / `icalendar`)
- **Base de Datos:** SQLite3

---

### 📂 Estructura del Proyecto
```text
JARVIS/
├── templates/
│   └── index.html          # Interfaz web frontend
├── app.py                  # Servidor web Flask y endpoints de la API
├── jarvis.py               # Orquestador principal del asistente (JarvisCore)
├── ejecutor.py             # Despachador de acciones y lógica de herramientas
├── memoria.py              # Memoria conversacional persistente en SQLite
├── voz.py                  # Módulo de síntesis y reconocimiento de voz
├── gmail.py                # Integración con la API de Gmail
├── calendario.py           # Integración con iCloud Calendar (CalDAV)
├── conectar_google.py      # Asistente de configuración OAuth2 de Google
├── requirements.txt        # Dependencias de Python
├── .env.example            # Plantilla de variables de entorno
└── .gitignore
```

---

### 🚀 Ejecución en Local

1. **Clona el repositorio:**
```bash
git clone https://github.com/marcos-madrigal/jarvis-ai-assistant.git
cd jarvis-ai-assistant
```

2. **Crea y activa un entorno virtual:**
```bash
python -m venv jarvis_env
# En Windows:
.\jarvis_env\Scripts\activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configura las variables de entorno y credenciales:**
   * Copia `.env.example` a `.env` y rellena tus credenciales (`CORREO_ICLOUD`, `PASSWORD_APP_ICLOUD`).
   * Coloca tu archivo OAuth `credentials.json` de Google Cloud en la carpeta raíz y ejecuta `python conectar_google.py` una vez para generar `token.json`.

5. **Asegúrate de tener Ollama ejecutándose en local y arranca la aplicación:**
```bash
python app.py
```
