@echo off
title NOVA - Co-host de IA
color 0B
cd /d %~dp0

echo ============================================
echo    NOVA - Co-host de IA para TikTok Live
echo ============================================
echo.

REM -- 1. Si es la primera vez, crea el entorno virtual (solo pasa una vez)
if not exist "venv\Scripts\python.exe" (
    echo Primera vez: preparando el entorno de Python...
    echo Esto solo pasa UNA vez. Espera un momento.
    echo.
    python -m venv venv
)

REM -- 2. Verifica que las librerias esten instaladas
echo Verificando librerias... (la primera vez tarda varios minutos)
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
echo.

REM -- 3. Arranca a Nova
echo Conectando al live de TikTok...
echo ============================================
echo.
venv\Scripts\python.exe main.py

echo.
echo ============================================
echo Nova se detuvo. Si hay un error arriba, copialo completo.
pause