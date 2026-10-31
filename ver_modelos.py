# ver_modelos.py - lista los modelos disponibles para tu key
import config
from google import genai

cliente = genai.Client(api_key=config.GEMINI_API_KEY)
print("Modelos disponibles:")
for m in cliente.models.list():
    print(" -", m.name)