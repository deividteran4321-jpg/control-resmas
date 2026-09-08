@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Primera vez: creando entorno e instalando dependencias...
    echo Esto puede tardar 1-2 minutos, por favor espera.
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: no se encontro Python. Instalalo desde https://www.python.org/downloads/
        echo Durante la instalacion, marca la casilla "Add Python to PATH".
        pause
        exit /b 1
    )
    ".venv\Scripts\pip.exe" install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR instalando dependencias. Revisa el mensaje de arriba.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando Control de Resmas...
echo Se abrira en tu navegador. NO cierres esta ventana mientras uses la app.
echo Para apagarla: cierra esta ventana o presiona Ctrl+C.
echo.

".venv\Scripts\streamlit.exe" run app.py

pause
