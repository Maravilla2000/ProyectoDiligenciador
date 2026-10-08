"""
Configuración de pytest para el proyecto.

Agrega la raíz del proyecto al sys.path para que los tests puedan
importar módulos como `generador`, `catalogo`, etc.
"""
import sys
from pathlib import Path

# Raíz del proyecto (donde vive este conftest.py)
RAIZ_PROYECTO = Path(__file__).parent.resolve()

if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))