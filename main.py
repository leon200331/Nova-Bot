# ════════════════════════════════════════════════════════════
#  NOVA — Co-host IA para TikTok Live
#  EL MOTOR PRINCIPAL
#  ─────────────────────────────────────────────────────────
#  Este archivo NO se toca. Su trabajo:
#
#   TikTok Live ──► prioridades ──► Gemini (cerebro)
#                                      │
#                                      ▼
#                          extraer [EMO:] y [POSE:]
#                                      │
#                                      ▼
#                    edge-tts (voz) ──► pygame (audio)
#                                      │
#                                      ▼
#                        VB-CABLE ──► OBS / LIVE Studio
#
#  Personalización: SOLO en config.py
#  Personalidad:    SOLO en persona_nova.txt
# ════════════════════════════════════════════════════════════

import asyncio
import os
import queue
import re
import tempfile
import threading
import time
from collections import deque

import edge_tts
import pygame
from google import genai
from google.genai import types
from TikTokLive import TikTokLiveClient

import config
from prompt import build_system_prompt


# ════════════════════════════════════════════════════════════
# 1. ESTADO DE LA SESIÓN (lo que Nova "recuerda" en el live)
# ════════════════════════════════════════════════════════════

PAUSED = False               # /pause y /resume la controlan
saludados = set()            # usuarios ya saludados en este live
memoria = deque(maxlen=15)   # eventos recientes para dar contexto

# Prioridades (menor número = más importante)
P_GIFT, P_STREAMER, P_QUESTION, P_CHAT, P_FOLLOW, P_JOIN = 0, 1, 2, 3, 4, 5

cola = queue.PriorityQueue()
_seq = 0
_lock = threading.Lock()


def push(prioridad, tag, texto):
    """Agrega algo a la cola de atención de Nova (thread-safe)."""
    global _seq
    with _lock:
        _seq += 1
        cola.put((prioridad, _seq, tag, texto))


# ════════════════════════════════════════════════════════════
# 2. ETIQUETAS [EMO:] Y [POSE:] (el puente hacia su cuerpo)
# ════════════════════════════════════════════════════════════

def extraer_emo(texto):
    """Separa la etiqueta [EMO: ...] del texto hablado.

    Ej: "[EMO: feliz] Hola, Leo" → ("feliz", "Hola, Leo")
    Si no trae etiqueta, devuelve "neutral".
    También limpia cualquier [POSE: ...] para que no se lea en voz alta.
    """
    m = re.match(r"\[EMO:\s*([a-záéíóúñ]+)\]\s*(.*)",
                 texto.strip(), re.IGNORECASE)
    if m:
        emo = m.group(1).lower()
        frase = m.group(2).strip()
    else:
        emo = "neutral"
        frase = texto.strip()

    # Quita la pose del texto hablado (se usará para el avatar, no la voz)
    frase = re.sub(r"\[POSE:\s*[a-záéíóúñ]+\]", "", frase).strip()

    # AQUÍ IRÁ, EN LA FASE DEL AVATAR:
    # cambiar la carita de Nova según 'emo' (PNGtuber / Live2D)
    return emo, frase


# ════════════════════════════════════════════════════════════
# 3. LA VOZ (edge-tts, gratis)
# ════════════════════════════════════════════════════════════

async def hablar(frase):
    """Convierte el texto en voz y lo reproduce por el audio del stream."""
    frase = " ".join(frase.split())  # limpia saltos de línea raros
    try:
        path = os.path.join(tempfile.gettempdir(), "nova_reply.mp3")
        await edge_tts.Communicate(
            frase, config.VOICE, rate=config.TTS_RATE
        ).save(path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print(f"  🗣️ {config.ASSISTANT_NAME.upper()}: {frase}")
    except Exception as e:
        print(f"  [error de voz] {e}")


# ════════════════════════════════════════════════════════════
# 4. EL CEREBRO (Gemini, free tier)
# ════════════════════════════════════════════════════════════

def crear_chat():
    """Crea la conversación con Gemini usando la personalidad del txt."""
    cliente = genai.Client(api_key=config.GEMINI_API_KEY)
    return cliente.chats.create(
        model=config.GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            temperature=1.0,
            max_output_tokens=250,   # fuerza respuestas cortas
        ),
    )


# ════════════════════════════════════════════════════════════
# 5. EL WORKER: decide CUÁNDO y a QUÉ responde Nova
# ════════════════════════════════════════════════════════════

async def worker(chat):
    """Ciclo eterno: saca de la cola, aplica reglas y responde."""
    ultimo = 0.0
    while True:
        # -- Sacar lo siguiente de la cola --
        try:
            prio, _, tag, texto = cola.get_nowait()
        except queue.Empty:
            await asyncio.sleep(0.3)
            continue

        # En pausa solo atiende regalos y al streamer
        if PAUSED and prio > P_STREAMER:
            continue

        # -- Anti-flood: silencio mínimo entre respuestas --
        espera = config.MIN_SECONDS_BETWEEN_REPLIES - (time.time() - ultimo)
        if espera > 0:
            await asyncio.sleep(espera)

        # Esperar a que Nova termine de hablar la respuesta anterior
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.2)

        # -- Agrupar comentarios de chat acumulados --
        if prio >= P_QUESTION:
            extras = []
            while len(extras) < config.MAX_BATCH and not cola.empty():
                try:
                    p2, _, t2, x2 = cola.get_nowait()
                except queue.Empty:
                    break
                if p2 >= P_QUESTION:
                    extras.append(f"{t2} {x2}")
                else:
                    push(p2, t2, x2)   # reinserta lo importante
            if extras:
                texto = texto + "\n" + "\n".join(extras)

        # -- Construir el bloque [CONTEXTO] (memoria del live) --
        contexto = ""
        if saludados:
            contexto += f"Ya saludaste a: {', '.join(list(saludados)[-10:])}. "
        if memoria:
            contexto += ("Eventos recientes: "
                         + "; ".join(list(memoria)[-6:]) + ".")
        if contexto:
            contexto = f"[CONTEXTO] {contexto}\n"

        # -- Preguntarle al cerebro --
        mensaje = f"{contexto}{tag} {texto}"
        try:
            # to_thread para no congelar los eventos de TikTok
            resp = await asyncio.to_thread(chat.send_message, mensaje)
            respuesta = (resp.text or "").strip()
        except Exception as e:
            print(f"  [error Gemini] {e} — recreando chat…")
            chat = crear_chat()
            respuesta = ""

        # -- Responder --
        if respuesta:
            emo, frase = extraer_emo(respuesta)
            print(f"  😊 Expresión: {emo}")
            await hablar(frase)          # solo el texto, sin etiquetas
            memoria.append(f"tú dijiste: {respuesta[:60]}")
            ultimo = time.time()
        else:
            # si no dijo nada, no cuenta como pausa completa
            ultimo = time.time() - config.MIN_SECONDS_BETWEEN_REPLIES / 2


# ════════════════════════════════════════════════════════════
# 6. CONSOLA: aquí le HABLAS a Nova mientras transmites
# ════════════════════════════════════════════════════════════

def consola():
    global PAUSED
    print("""
--- COMANDOS DEL STREAMER (escribe mientras transmites) ---
  /pause         silencia a Nova
  /resume        la reactiva
  /say <texto>   la obliga a decir algo AHORA (ignora la pausa)
  /ignore <user> ignora a un usuario del chat
  Cualquier otro texto se lo mandas como [STREAMER]
""")
    while True:
        try:
            linea = input().strip()
        except EOFError:
            time.sleep(5)
            continue
        if not linea:
            continue
        if linea == "/pause":
            PAUSED = True
            print("⏸ Nova en pausa")
        elif linea == "/resume":
            PAUSED = False
            print("▶ Nova activa")
        elif linea.startswith("/say "):
            push(P_GIFT, "[STREAMER]",
                 "OBLIGATORIO, di esto ahora con tu estilo: " + linea[5:])
        elif linea.startswith("/ignore "):
            usuario = linea.split()[1]
            config.IGNORED_USERS.append(usuario)
            print(f"🚫 ignorando a {usuario}")
        else:
            push(P_STREAMER, "[STREAMER]", linea)


# ════════════════════════════════════════════════════════════
# 7. EVENTOS DE TIKTOK (ojos y oídos de Nova)
# ════════════════════════════════════════════════════════════

client = TikTokLiveClient(unique_id=config.TIKTOK_USERNAME)


@client.on("connect")
async def conectado(event):
    print(f"✅ Conectado al live de @{config.TIKTOK_USERNAME}. "
          f"Escuchando chat…")


@client.on("disconnect")
async def desconectado(event):
    print("❌ Se perdió la conexión con TikTok.")


@client.on("comment")
async def comentario(event):
    usuario = getattr(event.user, "unique_id", "alguien")
    texto = (getattr(event, "comment", "") or "").strip()
    if not texto:
        return
    if usuario.lower() in (u.lower() for u in config.IGNORED_USERS):
        return

    # Si el comentario es TUYO (streamer), te trata distinto
    if (config.STREAMER_USERNAME
            and usuario.lower() == config.STREAMER_USERNAME.lower()):
        push(P_STREAMER, "[STREAMER]", texto)
    # Pregunta directa o te menciona → prioridad media
    elif "?" in texto or config.ASSISTANT_NAME.lower() in texto.lower():
        push(P_QUESTION, "[CHAT]", f"{usuario}: {texto}")
    else:
        push(P_CHAT, "[CHAT]", f"{usuario}: {texto}")


@client.on("gift")
async def regalo(event):
    g = getattr(event, "gift", None)
    # Si el regalo se acumula (combo), espera a que termine
    if getattr(g, "streakable", False) and getattr(g, "streaking", False):
        return
    nombre = None
    for attr in ("gift_name", "name"):
        if g is not None and hasattr(g, attr):
            nombre = getattr(g, attr)
            break
    if nombre is None:
        nombre = getattr(getattr(g, "info", None), "name", "un regalo")
    usuario = getattr(event.user, "unique_id", "alguien")
    push(P_GIFT, "[EVENTO]", f"{usuario} envió el regalo: {nombre}")
    memoria.append(f"regalo de {usuario} ({nombre})")


@client.on("follow")
async def sigue(event):
    usuario = getattr(event.user, "unique_id", "alguien")
    if cola.qsize() < 30:   # anti-saturación
        push(P_FOLLOW, "[EVENTO]", f"{usuario} te siguió")


@client.on("join")
async def entra(event):
    usuario = getattr(event.user, "unique_id", "alguien")
    if usuario in saludados or cola.qsize() >= 30:
        return
    saludados.add(usuario)
    push(P_JOIN, "[EVENTO]", f"{usuario} entró al live")


# ════════════════════════════════════════════════════════════
# 8. ARRANQUE
# ════════════════════════════════════════════════════════════

async def main():
    # Revisión básica antes de arrancar
    if "PEGA" in config.GEMINI_API_KEY:
        print("⚠️  Primero pon tu API key de Google AI Studio en config.py")
        print("    Gratis aquí: https://aistudio.google.com/apikey")
        return
    if not config.TIKTOK_USERNAME or config.TIKTOK_USERNAME == "tu_usuario":
        print("⚠️  Pon tu usuario de TikTok (sin @) en config.py")
        return

    pygame.mixer.init()
    chat = crear_chat()
    print(f"🧠 {config.ASSISTANT_NAME} despierta con su personalidad cargada…")
    threading.Thread(target=consola, daemon=True).start()
    asyncio.create_task(worker(chat))
    print(f"🚀 Conectando al live de @{config.TIKTOK_USERNAME}…")
    await client.start(run_forever=True)
    # Si tu versión de TikTokLive pide otro método, cámbialo por: client.run()


if __name__ == "__main__":
    asyncio.run(main())