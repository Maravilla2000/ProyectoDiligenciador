# Generador de diligencias

## Crear el ejecutable para Windows

En una computadora Windows con Python instalado:

1. Abra una terminal en esta carpeta.
2. Instale los requisitos de compilación:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Ejecute `build_windows.bat`.
4. Comparta `dist\GeneradorDiligencias.exe`.

La computadora de destino no necesita tener Python instalado. Al abrir el
ejecutable se inicia la aplicación y se abre en el navegador. Para generar
documentos, las plantillas Word ya están incluidas dentro del ejecutable.
Mantenga abierta la ventana de consola mientras use la aplicación; al cerrarla,
se detiene el servidor local.
