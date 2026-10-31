# NOVA - PRUEBA RAPIDA (sin live, sin TikTok)
# Verifica: 1. tu API key, 2. el prompt, 3. la voz
# Se ejecuta con:  python test_rapido.py
import asyncio
import os
import re
import tempfile

import edge_tts
import pygame
from google import genai
from google.genai import types

import config
from prompt import build_system_prompt


async def main():
    # 1. Prueba del cerebro (tu API key)
    print("1. Probando el cerebro (Gemini + tu API key)...")
    cliente = genai.Client(api_key=config.GEMINI_API_KEY)
    chat = cliente.chats.create(
        model=config.GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            temperature=1.0,
            max_output_tokens=250,
        ),
    )
    resp = chat.send_message(
        "[STREAMER] Hola Nova, presentate en una frase para "
        "saber que estas viva"
    )
    frase = (resp.text or "").strip()
    print(f"   Cerebro respondio: {frase}")
    print("   [OK] Cerebro funciona - tu API key sirve\n")

    # 2. Quitar la etiqueta [EMO:] antes de hablar
    m = re.match(r"\[EMO:\s*([a-záéíóúñ]+)\]\s*(.*)", frase,
                 re.IGNORECASE)
    if m:
        print(f"   Expresion: {m.group(1)}")
        frase = m.group(2).strip()

    # 3. Prueba de voz
    print("3. Probando la voz...")
    path = os.path.join(tempfile.gettempdir(), "nova_test.mp3")
    await edge_tts.Communicate(
        frase, config.VOICE, rate=config.TTS_RATE
    ).save(path)
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    print(f"   Nova dice: {frase}")
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.2)
    print("\nTODO FUNCIONA: cerebro + personalidad + voz.")
    print("Nova esta viva. Solo falta probarla en un live real.")


if __name__ == "__main__":
    asyncio.run(main())