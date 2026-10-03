import os
import sys
import multiprocessing
import subprocess
import time
import webbrowser

def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta para acceder a los recursos empaquetados """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

if __name__ == '__main__':
    # 1. EVITA EL BUCLE INFINITO EN EXECUTABLES COMPILADOS
    multiprocessing.freeze_support()

    app_path = resolver_ruta("app.py")

    # 2. Abrir el navegador tras un breve retraso para dar tiempo al servidor
    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://localhost:8501")

    import threading
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # 3. Iniciar Streamlit sin recarga automática (headless y sin watcher)
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--global.developmentMode=false"
    ]
    
    sys.exit(stcli.main())