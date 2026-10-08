"""
Tests de utilidades puras del generador.
Validan el comportamiento ACTUAL antes de refactorizar.
"""
import pytest
from generador import (
    numero_a_letras,
    unir_con_y,
    convertir_identidad_a_letras,
    formatear_edad,
)


# =========================================================
# numero_a_letras
# =========================================================
class TestNumeroALetras:

    def test_cero(self):
        assert numero_a_letras(0) == "CERO"

    def test_unidades(self):
        assert numero_a_letras(1) == "UN"
        assert numero_a_letras(5) == "CINCO"
        assert numero_a_letras(9) == "NUEVE"

    def test_especiales_diez_a_veintinueve(self):
        assert numero_a_letras(10) == "DIEZ"
        assert numero_a_letras(15) == "QUINCE"
        assert numero_a_letras(20) == "VEINTE"
        assert numero_a_letras(21) == "VEINTIUNO"
        assert numero_a_letras(29) == "VEINTINUEVE"

    def test_decenas_exactas(self):
        assert numero_a_letras(30) == "TREINTA"
        assert numero_a_letras(50) == "CINCUENTA"
        assert numero_a_letras(90) == "NOVENTA"

    def test_decenas_con_unidad(self):
        assert numero_a_letras(42) == "CUARENTA Y DOS"
        assert numero_a_letras(99) == "NOVENTA Y NUEVE"

    def test_cien_exacto(self):
        assert numero_a_letras(100) == "CIEN"

    def test_centenas_exactas(self):
        assert numero_a_letras(200) == "DOSCIENTOS"
        assert numero_a_letras(500) == "QUINIENTOS"
        assert numero_a_letras(900) == "NOVECIENTOS"

    def test_centenas_con_resto(self):
        assert numero_a_letras(101) == "CIENTO UN"
        assert numero_a_letras(142) == "CIENTO CUARENTA Y DOS"
        assert numero_a_letras(999) == "NOVECIENTOS NOVENTA Y NUEVE"

    def test_fuera_de_rango_devuelve_str(self):
        assert numero_a_letras(1000) == "1000"
        assert numero_a_letras(-5) == "-5"


# =========================================================
# unir_con_y
# =========================================================
class TestUnirConY:

    def test_lista_vacia(self):
        assert unir_con_y([]) == ""

    def test_un_elemento(self):
        assert unir_con_y(["A"]) == "A"

    def test_dos_elementos(self):
        assert unir_con_y(["A", "B"]) == "A y B"

    def test_tres_elementos(self):
        assert unir_con_y(["A", "B", "C"]) == "A, B y C"

    def test_cuatro_elementos(self):
        assert unir_con_y(["A", "B", "C", "D"]) == "A, B, C y D"


# =========================================================
# convertir_identidad_a_letras
# =========================================================
class TestConvertirIdentidadALetras:

    def test_vacio(self):
        assert convertir_identidad_a_letras("") == ""

    def test_para_oficio_devuelve_original(self):
        # para_acta=False debe devolver el original tal cual
        assert convertir_identidad_a_letras("06148510-8", para_acta=False) == "06148510-8"

    def test_dui_completo(self):
        resultado = convertir_identidad_a_letras("06148510-8", para_acta=True)
        # Cada dígito separado por espacio, guion como "guion"
        assert resultado == "cero seis uno cuatro ocho cinco uno cero guion ocho"

    def test_dui_corto(self):
        assert convertir_identidad_a_letras("12-3", para_acta=True) == "uno dos guion tres"


# =========================================================
# formatear_edad
# =========================================================
class TestFormatearEdad:

    def test_acta_entero(self):
        assert formatear_edad("44", para_acta=True) == "cuarenta y cuatro"

    def test_oficio_entero(self):
        assert formatear_edad("44", para_acta=False) == "44"

    def test_acta_con_decimal_entero(self):
        # "44.0" debe comportarse como 44
        assert formatear_edad("44.0", para_acta=True) == "cuarenta y cuatro"

    def test_texto_no_numerico_acta(self):
        # Si no es número, devuelve en minúsculas
        assert formatear_edad("desconocida", para_acta=True) == "desconocida"

    def test_texto_no_numerico_oficio(self):
        assert formatear_edad("desconocida", para_acta=False) == "desconocida"