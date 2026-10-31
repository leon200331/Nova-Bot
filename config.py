# ════════════════════════════════════════════════════════════
#  NOVA — Co-host IA para TikTok Live
#  CONFIGURACIÓN GENERAL
#  ─────────────────────────────────────────────────────────
#  Este es el ÚNICO archivo que editas para personalizar
#  a Nova. Los demás archivos del proyecto NO se tocan:
#
#  nova-bot/
#  ├── config.py        ← ESTE ARCHIVO (tu configuración)
#  ├── prompt.py        ← el que llena los nombres en el prompt (no tocar)
#  ├── persona_nova.txt ← la personalidad (solo si cambias su carácter)
#  ├── main.py          ← el motor (no tocar)
#  ├── requirements.txt ← las librerías (no tocar)
#  └── NOVA.bat         ← doble clic para arrancar (no tocar)
# ════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# 1. CONEXIÓN A TIKTOK (tu live)
# ─────────────────────────────────────────────

# Tu usuario de TikTok, SIN la arroba (@)
# Si tu live es tiktok.com/@leochan_22 → escribe: "leochan_22"
TIKTOK_USERNAME = "leochan_22"

# Tu misma cuenta de TikTok (sin @), para que Nova reconozca
# que TUS comentarios en el chat son del STREAMER y no del público
STREAMER_USERNAME = "leochan_22"


# ─────────────────────────────────────────────
# 2. EL CEREBRO (Gemini de Google — gratis)
# ─────────────────────────────────────────────

# API key GRATIS: entra a https://aistudio.google.com/apikey
# → botón "Create API key" → cópiala → pégala entre las comillas
GEMINI_API_KEY = "GEMINI_API_KEY", "TU_API_KEY_AQUI"

# Modelo a usar (flash = rápido y entra en el plan gratuito)
GEMINI_MODEL = "gemini-3.8-flash"


# ─────────────────────────────────────────────
# 3. IDENTIDAD (quién es Nova y quién eres tú)
# ─────────────────────────────────────────────

# Nombre de tu IA (es el que se inyecta en el prompt automáticamente)
ASSISTANT_NAME = "Nova"

# Cómo Nova te llama a TI cuando te habla en el live
# (puede ser tu nombre, tu apodo o lo que quieras que te diga)
STREAMER_NAME = "Leo"


# ─────────────────────────────────────────────
# 4. LA VOZ (edge-tts — gratis)
# ─────────────────────────────────────────────

# Voces femeninas de México disponibles:
#   es-MX-DaliaNeural  → mujer, la recomendada
#   es-MX-JorgeNeural  → hombre (por si algún día la cambias)
# Lista completa: en la terminal escribe  edge-tts --list-voices
VOICE = "es-MX-DaliaNeural"

# Velocidad del habla: "+8%" = un poco más rápida que lo normal
# Rango típico: "-10%" (más lenta) a "+20%" (más rápida)
TTS_RATE = "+8%"


# ─────────────────────────────────────────────
# 5. COMPORTAMIENTO EN EL LIVE
# ─────────────────────────────────────────────

# Segundos MÍNIMOS de silencio entre cada respuesta de Nova.
# Evita que hable sin parar y se empalme contigo.
# 8 = recomendado | más alto = más tranquila | más bajo = más habladora
MIN_SECONDS_BETWEEN_REPLIES = 8

# Cuántos comentarios del chat junta Nova antes de responderlos
# con una sola frase (evita responder uno por uno)
MAX_BATCH = 6

# Usuarios que Nova ignorará por completo (escribe el usuario sin @)
# Ejemplo: ["trol123", "spam_gamer"]
IGNORED_USERS = []