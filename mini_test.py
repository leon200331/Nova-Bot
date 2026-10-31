# mini_test.py - diagnostico directo, sin prompt de Nova
import config
from google import genai

print("Creando cliente...")
cliente = genai.Client(api_key=config.GEMINI_API_KEY)
print("Enviando pregunta simple...")
resp = cliente.models.generate_content(
    model=config.GEMINI_MODEL,
    contents="Contesta solo una palabra: hola"
)
print("RESPUESTA:", resp.text)