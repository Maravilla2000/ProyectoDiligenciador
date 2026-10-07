import os
import re
from docxtpl import DocxTemplate

# Map de dígitos para conversión de Identidades y DUIs a letras
DIGIT_MAP = {
    '0': 'cero', '1': 'uno', '2': 'dos', '3': 'tres', '4': 'cuatro',
    '5': 'cinco', '6': 'seis', '7': 'siete', '8': 'ocho', '9': 'nueve',
    '-': 'guion'
}

# =========================================================
# UTILIDADES DE TEXTO, NÚMEROS Y FORMATO PROCESAL
# =========================================================
def numero_a_letras(n: int) -> str:
    """Convierte un entero (0-999) a letras en mayúsculas, estilo acta policial."""
    if not (0 <= n <= 999):
        return str(n)
        
    unidades = ["CERO", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
    especiales = {
        10: "DIEZ", 11: "ONCE", 12: "DOCE", 13: "TRECE", 14: "CATORCE", 15: "QUINCE",
        16: "DIECISEIS", 17: "DIECISIETE", 18: "DIECIOCHO", 19: "DIECINUEVE",
        20: "VEINTE", 21: "VEINTIUNO", 22: "VEINTIDÓS", 23: "VEINTITRÉS", 24: "VEINTICUATRO",
        25: "VEINTICINCO", 26: "VEINTISÉIS", 27: "VEINTISIETE", 28: "VEINTIOCHO", 29: "VEINTINUEVE"
    }
    decenas = {
        30: "TREINTA", 40: "CUARENTA", 50: "CINCUENTA",
        60: "SESENTA", 70: "SETENTA", 80: "OCHENTA", 90: "NOVENTA"
    }
    centenas = {
        100: "CIEN", 200: "DOSCIENTOS", 300: "TRESCIENTOS", 400: "CUATROCIENTOS",
        500: "QUINIENTOS", 600: "SEISCIENTOS", 700: "SETECIENTOS",
        800: "OCHOCIENTOS", 900: "NOVECIENTOS"
    }
    
    if n < 10:
        return unidades[n]
    if n in especiales:
        return especiales[n]
    if n < 100:
        dec, uni = (n // 10) * 10, n % 10
        return decenas[dec] if uni == 0 else f"{decenas[dec]} Y {unidades[uni]}"
    if n == 100:
        return "CIEN"
    if n in centenas:
        return centenas[n]
        
    cent, resto = (n // 100) * 100, n % 100
    prefix = "CIENTO" if cent == 100 else centenas[cent]
    return f"{prefix} {numero_a_letras(resto)}"

def formatear_edad(edad_input, para_acta=True) -> str:
    """Convierte la edad a letras en minúsculas para Actas y número para Oficios."""
    val_str = str(edad_input).strip()
    try:
        n = float(val_str)
        if n.is_integer():
            n = int(n)
            letras = numero_a_letras(n)
            return letras.lower() if para_acta else str(n)
    except ValueError:
        pass
    return val_str.lower() if para_acta else val_str

def convertir_identidad_a_letras(texto, para_acta=True) -> str:
    """Convierte secuencias numéricas (DUI, Pasaportes) a palabras. Ej: 'DUI 029...-0' -> 'dui cero dos nueve... guion cero'"""
    val_str = str(texto).strip()
    if not val_str:
        return ""
    if not para_acta:
        return val_str

    def replace_match(match):
        chars = match.group(0)
        if not any(c.isdigit() for c in chars):
            return chars
        return " ".join(DIGIT_MAP[c] for c in chars if c in DIGIT_MAP)
        
    resultado = re.sub(r'[\d\-]+', replace_match, val_str)
    return resultado.lower()

def unir_con_y(items: list) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} y {items[1]}"
    return ", ".join(items[:-1]) + " y " + items[-1]

unir_nombres = unir_con_y

def _buscar_plantilla(nombre_plantilla: str):
    rutas = [
        os.path.join("plantillas", nombre_plantilla),
        os.path.join(os.path.dirname(__file__), "plantillas", nombre_plantilla),
        os.path.join(os.path.dirname(__file__), nombre_plantilla),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return ruta
    return None

def limpiar_datos(lista: list) -> list:
    return [
        {k: "" if v is None or str(v).strip().lower() in ['nan', 'none'] else str(v).strip() for k, v in item.items()}
        for item in lista
    ]

# =========================================================
# CONSTRUCCIÓN DE TEXTOS DE DELITOS
# =========================================================
def _clave_delito(imp: dict) -> tuple:
    return (imp.get('Delito', '').strip().upper(), imp.get('Articulo_CP', '').strip().lower())

def _recolectar_delitos_unicos(imputados: list) -> tuple:
    delitos, articulos = [], []
    for imp in imputados:
        d = imp.get('Delito', '').strip().upper()  # FORZAR MAYÚSCULA
        a = imp.get('Articulo_CP', '').strip().lower()  # FORZAR MINÚSCULA
        if d and d not in delitos:
            delitos.append(d)
        if a and a not in articulos:
            articulos.append(a)
    return delitos, articulos

def construir_textos_delitos(imputados: list) -> dict:
    vacio = {
        "texto_delitos_remision": "", "texto_delitos_resumen": "",
        "texto_delitos_plural": "", "texto_delitos_identificacion": "",
    }
    if not imputados: return vacio

    plural = len(imputados) > 1
    claves = [_clave_delito(imp) for imp in imputados]
    mismos = len(set(claves)) == 1
    delitos_unicos, articulos_unicos = _recolectar_delitos_unicos(imputados)

    if mismos:
        delito, art = claves[0]
        art_str = f" tipificado en el artículo {art}" if art else ""
        pronombre = "por atribuírseles" if plural else "por atribuírsele"
        art_id = f" previsto en el artículo {art} Pn." if art else ""

        return {
            "texto_delitos_remision": f"{pronombre} la comisión del delito de {delito}{art_str} del Código Penal vigente",
            "texto_delitos_resumen": f"por el delito de {delito}{art_str} del Código Penal vigente",
            "texto_delitos_plural": f"por el delito de {delito}",
            "texto_delitos_identificacion": f"{pronombre} el delito de {delito}{art_id}",
        }

    partes_remision = []
    for imp in imputados:
        f = imp.get('Género', '').lower() == 'femenino'
        trato = "a la señora" if f else "al señor"
        d = imp.get('Delito', '').strip().upper()
        a = imp.get('Articulo_CP', '').strip().lower()
        art_txt = f" tipificado en el artículo {a}" if a else ""
        partes_remision.append(f"{trato} {imp['Nombre']} la comisión del delito de {d}{art_txt}")

    art_id = f" previstos en los artículos {unir_con_y(articulos_unicos)} Pn." if articulos_unicos else ""

    return {
        "texto_delitos_remision": "por atribuírsele " + unir_con_y(partes_remision) + " del Código Penal vigente",
        "texto_delitos_resumen": "por los delitos antes relacionados",
        "texto_delitos_plural": f"por los delitos de {unir_con_y(delitos_unicos)}",
        "texto_delitos_identificacion": f"por atribuírseles los delitos de {unir_con_y(delitos_unicos)}{art_id}",
    }

# =========================================================
# PREPARACIÓN DE GRAMÁTICA Y EDADES/DUI
# =========================================================
def preparar_gramatica(datos_caso: dict) -> dict:
    # 🔹 Valores por defecto para campos opcionales (investigador y SATI)
    datos_caso.setdefault("nombre_investigador", "")
    datos_caso.setdefault("codigo_sati", "")

    imputados = limpiar_datos(datos_caso.get("lista_imputados", []))
    victimas = limpiar_datos(datos_caso.get("lista_victimas", []))

    datos_caso.update(construir_textos_delitos(imputados))
    plural = len(imputados) > 1

    delitos_unicos, articulos_unicos = _recolectar_delitos_unicos(imputados)
    datos_caso["delito"] = unir_con_y(delitos_unicos) if delitos_unicos else "DELITO NO ESPECIFICADO"
    datos_caso["articulo_cp"] = unir_con_y(articulos_unicos) if articulos_unicos else "N/A"

    # === VÍCTIMAS ===
    v_nombres_acta, v_nombres_oficio = [], []
    for i, v in enumerate(victimas):
        fem = v.get("Género", "").lower() == "femenino"
        trato = "la señora" if fem else "el señor"
        ident = "identificada" if fem else "identificado"

        # Conversión de Edad
        edad_acta = formatear_edad(v.get('Edad', ''), para_acta=True)
        edad_oficio = formatear_edad(v.get('Edad', ''), para_acta=False)
        v['Edad_Acta'] = edad_acta
        v['Edad_Oficio'] = edad_oficio

        # Conversión de DUI de la Víctima
        dui_raw = v.get('DUI', '')
        dui_acta = convertir_identidad_a_letras(dui_raw, para_acta=True)
        dui_oficio = convertir_identidad_a_letras(dui_raw, para_acta=False)
        v['DUI_Acta'] = dui_acta
        v['DUI_Oficio'] = dui_oficio

        v_nombres_acta.append(
            f"{trato} {v['Nombre']} de {edad_acta} años de edad, residente en {v['Residencia']}, "
            f"{ident} con documento único de identidad número {dui_acta}"
        )

        # 🔹 Oficios: incluir DUI en NÚMERO justo después de la edad
        dui_txt_oficio = (
            f", con documento único de identidad número {dui_oficio}"
            if dui_oficio else ""
        )
        t_oficio = (
            f"{v['Nombre']} de {edad_oficio} años de edad"
            f"{dui_txt_oficio}, "
            f"residente en {v['Residencia']}"
        )
        v_nombres_oficio.append(f"{i+1}) {t_oficio}" if len(victimas) > 1 else t_oficio)

    datos_caso["bloque_victimas_remision"] = unir_con_y(v_nombres_acta)
    datos_caso["bloque_victimas_oficios"] = (
        "\n".join(v_nombres_oficio) if len(victimas) > 1
        else (v_nombres_oficio[0] if v_nombres_oficio else "")
    )
    datos_caso["a_las_victimas_oficio"] = (
        "las víctimas" if len(victimas) > 1 
        else ("la señora" if victimas and victimas[0].get("Género", "").lower() == "femenino" else "el señor")
    ) if victimas else "la víctima"

    # 🔹 Variables adicionales de identificación de víctimas para oficios (en NÚMERO)
    datos_caso["identificaciones_victimas_oficio"] = unir_con_y(
        [f"{v['Nombre']}: {v.get('DUI_Oficio', '')}" for v in victimas if v.get('DUI_Oficio')]
    )
    datos_caso["dui_victima_oficio"] = victimas[0].get('DUI_Oficio', '') if victimas else ""

    # === IMPUTADOS ===
    solo_mujeres = all(imp.get("Género", "").lower() == "femenino" for imp in imputados) if imputados else False
    bloques_acta, bloques_oficios, nombres_cortos = [], [], []
    avisos_remision, datos_identificacion, avisos_identificacion = [], [], []

    for i, imp in enumerate(imputados):
        f = (imp.get("Género", "").lower() == "femenino")
        trato = "la señora" if f else "el señor"
        hijo = "hija" if f else "hijo"
        conocido = "conocida" if f else "conocido"
        originario = "originaria" if f else "originario"
        imp["letra_o_a"] = "A" if f else "O"

        # Conversión de Edad
        edad_acta = formatear_edad(imp.get('Edad', ''), para_acta=True)
        edad_oficio = formatear_edad(imp.get('Edad', ''), para_acta=False)
        imp['Edad_Acta'] = edad_acta
        imp['Edad_Oficio'] = edad_oficio

        # REGLA IDENTIFICACIÓN IMPUTADO: Valor por defecto o Conversión de números
        identidad_val = imp.get("Identidad", "").strip()
        # 🔹 Guardamos el valor ORIGINAL en número para usarlo en los oficios
        imp["Identidad_Original"] = identidad_val
        imp["Identidad_Oficio"] = identidad_val  # 🔹 versión en NÚMERO para oficios

        if not identidad_val:
            identidad_acta = "el cual manifestó no tener y llamarse como menciono previamente"
        else:
            identidad_acta = convertir_identidad_a_letras(identidad_val, para_acta=True)

        imp["Identidad"] = identidad_acta  # 🔹 versión en LETRAS para actas

        nombres_cortos.append(f"{trato} {imp['Nombre']}")
        padres = [f"de {imp[k]}" for k in ("Padre", "Madre") if imp.get(k)]
        padre_madre = f"{hijo} {' y '.join(padres)}" if padres else f"{hijo} de padres ignorados"

        alias_v = imp.get("Alias", "").strip()
        alias_txt = f" y quien es {conocido} por {alias_v}" if alias_v and alias_v.lower() not in ("ninguno", "ninguna", "n/a") else ""

        pandilla_v = imp.get("Pandilla", "").strip()
        pandilla_txt = f", miembro activo de {pandilla_v}" if pandilla_v and pandilla_v.lower() not in ("ninguna", "ninguno", "n/a") else ""

        est_civil = imp.get("Estado_Civil", "").strip()
        est_civil_txt = f", de estado familiar {est_civil}" if est_civil else ""

        prof = imp.get("Profesion", "").strip()
        prof_txt = f", de profesión u oficio {prof}" if prof else ""

        b_acta = (
            f"{trato} {imp['Nombre']}{alias_txt} de {edad_acta} años de edad"
            f"{est_civil_txt}{prof_txt}, de nacionalidad {imp['Nacionalidad']}, "
            f"residente en {imp['Residencia']}, con documento {identidad_acta}{pandilla_txt}, {padre_madre}"
        )
        bloques_acta.append(b_acta)

        # 🔹 Oficios: incluir IDENTIDAD en NÚMERO justo después de la edad
        identidad_txt_oficio = (
            f", con documento de identidad número {imp['Identidad_Oficio']}"
            if imp.get('Identidad_Oficio') else ""
        )
        b_oficio = (
            f"{imp['Nombre']} de {edad_oficio} años de edad"
            f"{identidad_txt_oficio}, "
            f"de nacionalidad {imp['Nacionalidad']}, residente en {imp['Residencia']}"
        )
        bloques_oficios.append(f"{i+1}) {b_oficio}" if plural else b_oficio)

        avisos_remision.append(
            f"{trato} {imp['Nombre']} designó que se le avise de su detención a su "
            f"{imp['Parentesco_Aviso']} de nombre {imp['Nombre_Aviso']}."
        )

        alias_id_txt = f" y quien es {conocido} por {imp['Alias']}," if imp.get('Alias') and imp['Alias'].lower() != "ninguno" else ","
        identidad_txt = f" {identidad_acta}," if identidad_acta else ""
        pandilla_id_txt = f" quien es miembro activo de {imp['Pandilla']}" if imp.get('Pandilla') and imp['Pandilla'].lower() != "ninguna" else " quien no pertenece a pandillas y es"
        
        # Extracción Asegurada de Delitos Mayúsculas y Artículos Minúsculas
        delito_imp = imp.get('Delito', '').strip().upper()
        art_imp = imp.get('Articulo_CP', '').strip().lower()
        delito_detalle = f" por el (los) delito(s) de {delito_imp}" + (f" (Art. {art_imp} C.P.)" if art_imp else "")

        b_ident = (
            f"{i+1}) {trato} {imp['Nombre']}{alias_id_txt}{identidad_txt}{pandilla_id_txt} "
            f"de {edad_acta} años de edad, estado familiar {imp['Estado_Civil']}, "
            f"de profesión u oficio {imp['Profesion']}, {originario} de {imp['Origen']}, "
            f"lugar y fecha de nacimiento {imp['Fecha_Nac']}, residente en {imp['Residencia']}. "
            f"Siendo {padre_madre} de nacionalidad {imp['Nacionalidad']}{delito_detalle}."
        )
        datos_identificacion.append(b_ident[3:] if not plural else b_ident)
        avisos_identificacion.append(f"{i+1}) {trato} {imp['Nombre']} manifestó que se le diera aviso a su {imp['Parentesco_Aviso']} {imp['Nombre_Aviso']}."[3:] if not plural else f"{i+1}) {trato} {imp['Nombre']} manifestó que se le diera aviso a su {imp['Parentesco_Aviso']} {imp['Nombre_Aviso']}.")

    datos_caso["bloque_imputados_remision"] = unir_con_y(bloques_acta)
    datos_caso["nombres_imputados"] = unir_con_y(nombres_cortos)
    datos_caso["bloque_avisos_remision"] = " ".join(avisos_remision)
    datos_caso["bloque_datos_identificacion"] = "\n".join(datos_identificacion)
    datos_caso["bloque_avisos_identificacion"] = "\n".join(avisos_identificacion)
    datos_caso["plural_s"] = "s" if plural else ""

    # 🔹 Variables adicionales de identificación de imputados para oficios (en NÚMERO)
    datos_caso["identificaciones_imputados_oficio"] = unir_con_y(
        [f"{imp['Nombre']}: {imp.get('Identidad_Oficio', '')}" for imp in imputados if imp.get('Identidad_Oficio')]
    )
    datos_caso["identidad_imputado_oficio"] = imputados[0].get('Identidad_Oficio', '') if imputados else ""

    if plural:
        datos_caso["a_los_imputados_oficio"] = "a las imputadas" if solo_mujeres else "a los imputados"
        datos_caso["bloque_imputados_oficios"] = "\n".join(bloques_oficios)
        datos_caso["quienes_fueron"] = "Quienes fueron aprehendidas" if solo_mujeres else "Quienes fueron aprehendidos"
        datos_caso["dicho_imputado"] = "Dichas imputadas serán puestas" if solo_mujeres else "Dichos imputados serán puestos"
        datos_caso["plural_les"] = "les"
        datos_caso["plural_quedarian"] = "quedarían"
        datos_caso["plural_detenidos"] = "detenidas" if solo_mujeres else "detenidos"
        datos_caso["plural_nombrarian"] = "nombrarían"
        datos_caso["plural_este"] = "estas" if solo_mujeres else "estos"
        datos_caso["plural_manifesto"] = "manifestaron"
        datos_caso["el_los_represente"] = "las represente" if solo_mujeres else "los represente"
        datos_caso["el_los_detenidos"] = "las detenidas" if solo_mujeres else "los detenidos"
        datos_caso["a_los_imputados_identificacion"] = "a las imputadas" if solo_mujeres else "a los imputados"
        datos_caso["quienes_identificacion"] = "quienes"
        datos_caso["plural_quedan"] = "quedan"
        datos_caso["plural_os_as"] = "as" if solo_mujeres else "os"
        datos_caso["n_plural"] = "n"
        datos_caso["es_plural"] = "es"
        datos_caso["los_imputados_texto"] = "las imputadas" if solo_mujeres else "los imputados"
    else:
        f = (imputados[0].get("Género", "").lower() == "femenino") if imputados else False
        datos_caso["a_los_imputados_oficio"] = "a la imputada" if f else "al imputado"
        datos_caso["bloque_imputados_oficios"] = bloques_oficios[0] if bloques_oficios else ""
        datos_caso["quienes_fueron"] = "Quien fue aprehendida" if f else "Quien fue aprehendido"
        datos_caso["dicho_imputado"] = "Dicha imputada será puesta" if f else "Dicho imputado será puesto"
        datos_caso["plural_les"] = "le"
        datos_caso["plural_quedarian"] = "quedaría"
        datos_caso["plural_detenidos"] = "detenida" if f else "detenido"
        datos_caso["plural_nombrarian"] = "nombraría"
        datos_caso["plural_este"] = "esta" if f else "este"
        datos_caso["plural_manifesto"] = "manifestó"
        datos_caso["el_los_represente"] = "la represente" if f else "lo represente"
        datos_caso["el_los_detenidos"] = "la detenida" if f else "el detenido"
        datos_caso["a_los_imputados_identificacion"] = "a la imputada" if f else "al imputado"
        datos_caso["quienes_identificacion"] = "quien"
        datos_caso["plural_quedan"] = "queda"
        datos_caso["plural_os_as"] = "a" if f else "o"
        datos_caso["n_plural"] = ""
        datos_caso["es_plural"] = ""
        datos_caso["los_imputados_texto"] = "la imputada" if f else "el imputado"

    datos_caso["lista_imputados"] = imputados
    return datos_caso

# =========================================================
# GENERACIÓN DEL PAQUETE
# =========================================================
def generar_paquete_diligencias(datos_caso: dict, carpeta_salida="expediente_generado") -> list:
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    datos_caso = preparar_gramatica(datos_caso)
    plantillas = {
        "01_ACTA_DE_REMISION_PLANTILLA.docx": "01-Acta_Remision_Generada.docx",
        "02_OFICIO_FGR_PLANTILLA.docx": "02-Oficio_FGR_Generado.docx",
        "03_OFICIO_PGR_PLANTILLA.docx": "03-Oficio_PGR_Generado.docx",
        "04_OFICIO_PDH_PLANTILLA.docx": "04-Oficio_PDH_Generado.docx",
        "05_OFICIO_CUSTODIA_911_PLANTILLA.docx": "05-Oficio_911_Generado.docx",
        "06_ACTA_DE_IDENTIFICACION_PLANTILLA.docx": "06-Acta_Identificacion_Generada.docx"
    }

    archivos_generados = []
    for p_name, out_name in plantillas.items():
        ruta = _buscar_plantilla(p_name)
        if ruta:
            doc = DocxTemplate(ruta)
            doc.render(datos_caso)
            out_ruta = os.path.join(carpeta_salida, out_name)
            doc.save(out_ruta)
            archivos_generados.append(out_ruta)

    if not archivos_generados:
        raise FileNotFoundError("Plantillas .docx no encontradas.")

    return archivos_generados