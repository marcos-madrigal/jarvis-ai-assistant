# 🤖 J.A.R.V.I.S. — Local-First AI Voice & Productivity Assistant

A modular, local-first personal AI assistant powered by **Ollama** (local LLMs), featuring real-time voice synthesis, persistent SQLite conversational memory, a web dashboard, and direct integrations with **Gmail** and **Apple iCloud Calendar**.

---

### ✨ Key Features
- **Local LLM Reasoning (`Ollama`):** Runs inference locally without external LLM API latency or token costs, maintaining structured system prompts and conversational context.
- **Persistent Memory (`SQLite`):** Custom memory manager (`memoria.py`) storing conversation history and user context in a local relational database (`jarvis_memoria.db`).
- **Voice Synthesis (`Edge-TTS`):** Natural text-to-speech audio generation (`voz.py`) for hands-free responses.
- **Action Execution & Integrations:**
  - **Gmail Integration (`gmail.py`):** OAuth2-authenticated email reading and sending via Google APIs.
  - **Apple iCloud Calendar (`calendario.py`):** CalDAV integration using app-specific credentials to query and schedule events.
  - **Command Dispatcher (`ejecutor.py`):** Modular intent router translating LLM outputs into system actions.
- **Web Interface (`Flask`):** Lightweight browser UI (`app.py` + `templates/index.html`) for interacting with the assistant.

---

### 🛠️ Tech Stack
- **Core & AI:** Python 3.13, Ollama
- **Backend & UI:** Flask, HTML5, CSS3, JavaScript
- **Voice & Audio:** `edge-tts`
- **APIs & Protocols:** Google Gmail API (OAuth2), Apple iCloud Calendar (CalDAV / `icalendar`)
- **Database:** SQLite3

---

### 📂 Project Structure
```text
JARVIS/
├── templates/
│   └── index.html          # Web frontend interface
├── app.py                  # Flask web server & API endpoints
├── jarvis.py               # Core assistant orchestrator (JarvisCore)
├── ejecutor.py             # Action dispatcher & tool execution logic
├── memoria.py              # SQLite persistent conversation memory
├── voz.py                  # Text-to-speech synthesis module
├── gmail.py                # Gmail API integration
├── calendario.py           # iCloud Calendar (CalDAV) integration
├── conectar_google.py      # Google OAuth2 setup helper
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── .gitignore
```

---

### 🚀 Running Locally

1. **Clone the repository:**
```bash
git clone [https://github.com/marcos-madrigal/jarvis-ai-assistant.git](https://github.com/marcos-madrigal/jarvis-ai-assistant.git)
cd jarvis-ai-assistant
```

2. **Create and activate a virtual environment:**
```bash
python -m venv jarvis_env
# On Windows:
.\jarvis_env\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
   * Copy `.env.example` to `.env` and fill in your credentials (`CORREO_ICLOUD`, `PASSWORD_APP_ICLOUD`, etc.).
   * Place your Google Cloud OAuth `credentials.json` in the root folder and run `python conectar_google.py` once to generate `token.json`.

5. **Ensure Ollama is running locally and launch the app:**
```bash
python app.py
```