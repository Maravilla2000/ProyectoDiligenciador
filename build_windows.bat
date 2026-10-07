@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller --noconfirm --clean --distpath "%~dp0dist" --workpath "%~dp0build\pyinstaller" "%~dp0app.spec"
if errorlevel 1 (
    echo.
    echo No se pudo crear el ejecutable. Revise los mensajes anteriores.
    pause
    exit /b 1
)

echo.
echo Ejecutable creado en: "%~dp0dist\GeneradorDiligencias.exe"
