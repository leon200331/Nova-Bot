# ════════════════════════════════════════════════════════════
#  NOVA — Co-host IA para TikTok Live
#  LECTOR DE PERSONALIDAD
#  ─────────────────────────────────────────────────────────
#  Este archivo NO se toca nunca.
#
#  Su único trabajo es:
#   1. Leer la personalidad de Nova desde persona_nova.txt
#   2. Rellenar los huecos {ASSISTANT_NAME} y {STREAMER_NAME}
#      con los valores que pusiste en config.py
#   3. Entregar el prompt final listo para Gemini
# ════════════════════════════════════════════════════════════

import os

import config

# Busca persona_nova.txt en la MISMA carpeta donde está este archivo,
# sin importar desde dónde ejecutes el programa
_ARCHIVO_PERSONALIDAD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "persona_nova.txt"
)


def build_system_prompt():
    """Lee persona_nova.txt y devuelve el prompt final de Nova.

    - Si falta el archivo, se detiene con un mensaje claro (en español)
      para que sepas exactamente qué hacer, en vez de un error críptico.
    - Los nombres se rellenan solos desde config.py.
    """
    # 1. Verificar que exista el archivo de personalidad
    if not os.path.exists(_ARCHIVO_PERSONALIDAD):
        raise FileNotFoundError(
            f"\n{'=' * 60}\n"
            "ERROR: No encuentro el archivo persona_nova.txt\n"
            f"Busqué en: {_ARCHIVO_PERSONALIDAD}\n\n"
            "Solución: crea el archivo persona_nova.txt en esa misma\n"
            "carpeta y pega ahí el prompt completo (PARTE 1 a PARTE 6).\n"
            f"{'=' * 60}\n"
        )

    # 2. Leer la personalidad (utf-8 para que no se dañen los acentos)
    with open(_ARCHIVO_PERSONALIDAD, encoding="utf-8") as f:
        texto = f.read()

    # 3. Rellenar los huecos con los nombres de config.py
    #    (si cambias el nombre en config.py, aquí se actualiza solo)
    texto = texto.replace("{ASSISTANT_NAME}", config.ASSISTANT_NAME)
    texto = texto.replace("{STREAMER_NAME}", config.STREAMER_NAME)

    # 4. Aviso si el txt está vacío (protección extra)
    if not texto.strip():
        raise ValueError(
            "\npersona_nova.txt está VACÍO. Pega el prompt completo "
            "(PARTE 1 a PARTE 6) dentro del archivo y vuelve a arrancar.\n"
        )

    return texto


# ─────────────────────────────────────────────
# PRUEBA RÁPIDA (opcional)
# Ejecuta solo este archivo con:  python prompt.py
# y verás el prompt final de Nova con los nombres ya rellenos.
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(build_system_prompt())