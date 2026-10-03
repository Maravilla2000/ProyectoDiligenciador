import os
from docxtpl import DocxTemplate


# =========================================================
# UTILIDADES NUMÉRICAS (por si se usan desde el generador)
# =========================================================

def numero_a_letras(n: int) -> str:
    """Convierte un entero (0-999) a letras en mayúsculas, estilo acta policial."""
    if n < 0 or n > 999:
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
        dec = (n // 10) * 10
        uni = n % 10
        return decenas[dec] if uni == 0 else f"{decenas[dec]} Y {unidades[uni]}"
    if n == 100:
        return "CIEN"
    if n in centenas:
        return centenas[n]
    cent = (n // 100) * 100
    resto = n % 100
    return f"CIENTO {numero_a_letras(resto)}" if cent == 100 else f"{centenas[cent]} {numero_a_letras(resto)}"


# =========================================================
# UTILIDADES DE PLANTILLAS Y TEXTO
# =========================================================

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


def unir_nombres(lista_textos):
    if not lista_textos:
        return ""
    if len(lista_textos) == 1:
        return lista_textos[0]
    return ", ".join(lista_textos[:-1]) + " y " + lista_textos[-1]


def limpiar_datos(lista):
    """Convierte nulos a cadenas vacías."""
    limpia = []
    for item in lista:
        nuevo = {}
        for k, v in item.items():
            if v is None or str(v).strip().lower() in ['nan', 'none']:
                nuevo[k] = ""
            else:
                nuevo[k] = str(v).strip()
        limpia.append(nuevo)
    return limpia


def _unir_con_y(items):
    """Une elementos con comas y 'y' final: [a, b, c] -> 'a, b y c'."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} y {items[1]}"
    return ", ".join(items[:-1]) + " y " + items[-1]


# =========================================================
# CONSTRUCCIÓN DE TEXTOS DE DELITOS (4 VARIANTES)
# =========================================================

def _clave_delito(imp):
    """Devuelve tupla normalizada (delito, artículo) para comparar."""
    return (
        imp.get('Delito', '').strip().upper(),
        imp.get('Articulo_CP', '').strip()
    )


def _recolectar_delitos_unicos(imputados):
    """Devuelve (lista_delitos_únicos, lista_articulos_únicos) preservando orden."""
    delitos, articulos = [], []
    for imp in imputados:
        d = imp.get('Delito', '').strip().upper()
        a = imp.get('Articulo_CP', '').strip()
        if d and d not in delitos:
            delitos.append(d)
        if a and a not in articulos:
            articulos.append(a)
    return delitos, articulos


def construir_textos_delitos(imputados):
    """
    Devuelve un diccionario con las 4 variantes de texto que las plantillas necesitan:
      - texto_delitos_remision:        bloque completo para el Acta de Remisión
      - texto_delitos_resumen:         resumen para la 2da mención en Acta de Remisión
      - texto_delitos_plural:          bloque para los oficios ("por el/los delito(s) de X")
      - texto_delitos_identificacion:  bloque para el Acta de Identificación
    """
    vacio = {
        "texto_delitos_remision": "",
        "texto_delitos_resumen": "",
        "texto_delitos_plural": "",
        "texto_delitos_identificacion": "",
    }
    if not imputados:
        return vacio

    plural = len(imputados) > 1
    claves = [_clave_delito(imp) for imp in imputados]
    mismos = len(set(claves)) == 1

    delitos_unicos, articulos_unicos = _recolectar_delitos_unicos(imputados)
    delito_resumen = _unir_con_y(delitos_unicos) if delitos_unicos else "DELITO NO ESPECIFICADO"
    articulo_resumen = _unir_con_y(articulos_unicos) if articulos_unicos else ""

    # ---------- CASO A: TODOS EL MISMO DELITO ----------
    if mismos:
        delito, art = claves[0]
        art_str = f" tipificado en el artículo {art}" if art else ""

        # 1) Remisión
        pronombre = "por atribuírseles" if plural else "por atribuírsele"
        texto_remision = f"{pronombre} la comisión del delito de {delito}{art_str} del Código Penal vigente"

        # 2) Resumen
        texto_resumen = f"por el delito de {delito}{art_str} del Código Penal vigente"

        # 3) Plural (oficios)
        texto_plural = f"por el delito de {delito}"

        # 4) Identificación
        art_id = f" previsto en el artículo {art} Pn." if art else ""
        pron_id = "por atribuírseles" if plural else "por atribuírsele"
        texto_ident = f"{pron_id} el delito de {delito}{art_id}"

        return {
            "texto_delitos_remision": texto_remision,
            "texto_delitos_resumen": texto_resumen,
            "texto_delitos_plural": texto_plural,
            "texto_delitos_identificacion": texto_ident,
        }

    # ---------- CASO B: DELITOS DIFERENTES ----------
    # 1) Remisión: "por atribuírsele al señor X la comisión del delito de A, y a la señora Y la comisión del delito de B"
    partes_remision = []
    for imp in imputados:
        f = imp.get('Género', '').lower() == 'femenino'
        trato = "a la señora" if f else "al señor"
        d = imp.get('Delito', '').strip().upper()
        a = imp.get('Articulo_CP', '').strip()
        art_txt = f" tipificado en el artículo {a}" if a else ""
        partes_remision.append(f"{trato} {imp['Nombre']} la comisión del delito de {d}{art_txt}")

    texto_remision = "por atribuírsele " + _unir_con_y(partes_remision) + " del Código Penal vigente"

    # 2) Resumen: "por los delitos antes relacionados"
    texto_resumen = "por los delitos antes relacionados"

    # 3) Plural (oficios): "por los delitos de A y B"
    texto_plural = f"por los delitos de {_unir_con_y(delitos_unicos)}"

    # 4) Identificación: "por atribuírseles los delitos de A y B previstos en los artículos X y Y Pn."
    if articulos_unicos:
        art_id = f" previstos en los artículos {_unir_con_y(articulos_unicos)} Pn."
    else:
        art_id = ""
    texto_ident = f"por atribuírseles los delitos de {_unir_con_y(delitos_unicos)}{art_id}"

    return {
        "texto_delitos_remision": texto_remision,
        "texto_delitos_resumen": texto_resumen,
        "texto_delitos_plural": texto_plural,
        "texto_delitos_identificacion": texto_ident,
    }


# =========================================================
# PREPARACIÓN DE GRAMÁTICA
# =========================================================

def preparar_gramatica(datos_caso: dict):
    imputados = limpiar_datos(datos_caso.get("lista_imputados", []))
    victimas = limpiar_datos(datos_caso.get("lista_victimas", []))

    # === DELITOS ===
    textos = construir_textos_delitos(imputados)
    datos_caso.update(textos)

    plural = len(imputados) > 1
    claves = [_clave_delito(imp) for imp in imputados]
    mismos_delitos = len(set(claves)) == 1 if imputados else True

    # Compatibilidad con variables antiguas (por si alguna plantilla vieja las usa)
    delitos_unicos, articulos_unicos = _recolectar_delitos_unicos(imputados)
    datos_caso["delito"] = _unir_con_y(delitos_unicos) if delitos_unicos else "DELITO NO ESPECIFICADO"
    datos_caso["articulo_cp"] = _unir_con_y(articulos_unicos) if articulos_unicos else "N/A"

    # === VÍCTIMAS ===
    v_nombres_acta = []
    v_nombres_oficio = []

    for i, v in enumerate(victimas):
        fem = v.get("Género", "").lower() == "femenino"
        trato = "la señora" if fem else "el señor"
        ident = "identificada" if fem else "identificado"

        t_acta = f"{trato} {v['Nombre']} de {v['Edad']} años de edad, residente en {v['Residencia']}, {ident} con documento único de identidad número {v['DUI']}"
        v_nombres_acta.append(t_acta)

        t_oficio = f"{v['Nombre']} de {v['Edad']} años de edad, residente en {v['Residencia']}"
        if len(victimas) > 1:
            v_nombres_oficio.append(f"{i+1}) {t_oficio}")
        else:
            v_nombres_oficio.append(t_oficio)

    datos_caso["bloque_victimas_remision"] = unir_nombres(v_nombres_acta)
    datos_caso["bloque_victimas_oficios"] = "\n".join(v_nombres_oficio) if len(victimas) > 1 else (v_nombres_oficio[0] if v_nombres_oficio else "")
    if victimas:
        datos_caso["a_las_victimas_oficio"] = "las víctimas" if len(victimas) > 1 else ("la señora" if victimas[0].get("Género", "").lower() == "femenino" else "el señor")
    else:
        datos_caso["a_las_victimas_oficio"] = "la víctima"

    # === IMPUTADOS ===
    solo_mujeres = all(imp.get("Género", "").lower() == "femenino" for imp in imputados) if imputados else False

    bloques_acta = []
    bloques_oficios = []
    nombres_cortos = []
    avisos_remision = []
    datos_identificacion = []
    avisos_identificacion = []

    for i, imp in enumerate(imputados):
        f = (imp.get("Género", "").lower() == "femenino")
        trato = "la señora" if f else "el señor"
        hijo = "hija" if f else "hijo"
        conocido = "conocida" if f else "conocido"
        originario = "originaria" if f else "originario"
        imp["letra_o_a"] = "A" if f else "O"

        nombres_cortos.append(f"{trato} {imp['Nombre']}")

        padres = []
        if imp["Padre"]:
            padres.append(f"de {imp['Padre']}")
        if imp["Madre"]:
            padres.append(f"de {imp['Madre']}")
        padre_madre = f"{hijo} {' y '.join(padres)}" if padres else f"{hijo} de padres ignorados"

        # --- Bloques OPCIONALES: solo se agregan si el usuario los llenó ---
        alias_valor = imp.get("Alias", "").strip()
        if alias_valor and alias_valor.lower() not in ("ninguno", "ninguna", "n/a"):
            alias_txt = f" y quien es {conocido} por {alias_valor}"
        else:
            alias_txt = ""

        pandilla_valor = imp.get("Pandilla", "").strip()
        if pandilla_valor and pandilla_valor.lower() not in ("ninguna", "ninguno", "n/a"):
            pandilla_txt = f", miembro activo de {pandilla_valor}"
        else:
            pandilla_txt = ""

        estado_civil_valor = imp.get("Estado_Civil", "").strip()
        estado_civil_txt = f", de estado familiar {estado_civil_valor}" if estado_civil_valor else ""

        profesion_valor = imp.get("Profesion", "").strip()
        profesion_txt = f", de profesión u oficio {profesion_valor}" if profesion_valor else ""

        b_acta = (
            f"{trato} {imp['Nombre']}{alias_txt} de {imp['Edad']} años de edad"
            f"{estado_civil_txt}"
            f"{profesion_txt}"
            f", de nacionalidad {imp['Nacionalidad']}, residente en {imp['Residencia']}, "
            f"quien {imp['Identidad']}{pandilla_txt}, {padre_madre}"
        )
        bloques_acta.append(b_acta)

        b_oficio = f"{imp['Nombre']} de {imp['Edad']} años de edad, de nacionalidad {imp['Nacionalidad']}, residente en {imp['Residencia']}"
        bloques_oficios.append(f"{i+1}) {b_oficio}" if plural else b_oficio)

        avisos_remision.append(f"{trato} {imp['Nombre']} designó que se le avise de su detención a su {imp['Parentesco_Aviso']} de nombre {imp['Nombre_Aviso']}.")

        alias_texto = f" y quien es {conocido} por {imp['Alias']}," if imp['Alias'] and imp['Alias'].lower() != "ninguno" else ","
        identidad_valor = imp.get("Identidad", "").strip()
        identidad_texto = f" {identidad_valor}," if identidad_valor else ""
        pandilla_texto = f" quien es miembro activo de {imp['Pandilla']}" if imp['Pandilla'] and imp['Pandilla'].lower() != "ninguna" else " quien no pertenece a pandillas y es"

        delito_imp = imp.get('Delito', '').strip().upper()
        art_imp = imp.get('Articulo_CP', '').strip()
        delito_detalle = f" por el (los) delito(s) de {delito_imp}" + (f" (Art. {art_imp} C.P.)" if art_imp else "")

        b_ident = f"{i+1}) {trato} {imp['Nombre']}{alias_texto}{identidad_texto}{pandilla_texto} de {imp['Edad']} años de edad, estado familiar {imp['Estado_Civil']}, de profesión u oficio {imp['Profesion']}, {originario} de {imp['Origen']}, lugar y fecha de nacimiento {imp['Fecha_Nac']}, residente en {imp['Residencia']}. Siendo {padre_madre} de nacionalidad {imp['Nacionalidad']}{delito_detalle}."
        if not plural:
            b_ident = b_ident[3:]
        datos_identificacion.append(b_ident)

        b_aviso_ident = f"{i+1}) {trato} {imp['Nombre']} manifestó que se le diera aviso a su {imp['Parentesco_Aviso']} {imp['Nombre_Aviso']}."
        if not plural:
            b_aviso_ident = b_aviso_ident[3:]
        avisos_identificacion.append(b_aviso_ident)

    # === INYECCIÓN DE BLOQUES ===
    datos_caso["bloque_imputados_remision"] = unir_nombres(bloques_acta)
    datos_caso["nombres_imputados"] = unir_nombres(nombres_cortos)
    datos_caso["bloque_avisos_remision"] = " ".join(avisos_remision)
    datos_caso["bloque_datos_identificacion"] = "\n".join(datos_identificacion)
    datos_caso["bloque_avisos_identificacion"] = "\n".join(avisos_identificacion)

    # === PLURAL_S ===
    # Se sigue usando en plantillas para: "atribuírsele{{ plural_s }}", "preguntarle{{ plural_s }}", etc.
    datos_caso["plural_s"] = "s" if plural else ""

    # === PLURALIDAD ===
    if plural:
        datos_caso["a_los_imputados_oficio"] = "a los imputados" if not solo_mujeres else "a las imputadas"
        datos_caso["bloque_imputados_oficios"] = "\n".join(bloques_oficios)
        datos_caso["quienes_fueron"] = "Quienes fueron aprehendidos" if not solo_mujeres else "Quienes fueron aprehendidas"
        datos_caso["dicho_imputado"] = "Dichos imputados serán puestos" if not solo_mujeres else "Dichas imputadas serán puestas"
        datos_caso["plural_les"] = "les"
        datos_caso["plural_quedarian"] = "quedarían"
        datos_caso["plural_detenidos"] = "detenidos" if not solo_mujeres else "detenidas"
        datos_caso["plural_nombrarian"] = "nombrarían"
        datos_caso["plural_este"] = "estos" if not solo_mujeres else "estas"
        datos_caso["plural_manifesto"] = "manifestaron"
        datos_caso["el_los_represente"] = "los represente" if not solo_mujeres else "las represente"
        datos_caso["el_los_detenidos"] = "los detenidos" if not solo_mujeres else "las detenidas"
        datos_caso["a_los_imputados_identificacion"] = "a los imputados" if not solo_mujeres else "a las imputadas"
        datos_caso["quienes_identificacion"] = "quienes"
        datos_caso["plural_quedan"] = "quedan"
        datos_caso["plural_os_as"] = "os" if not solo_mujeres else "as"
        datos_caso["n_plural"] = "n"
        datos_caso["es_plural"] = "es"
        datos_caso["los_imputados_texto"] = "los imputados" if not solo_mujeres else "las imputadas"
    else:
        f = (imputados[0].get("Género", "").lower() == "femenino") if imputados else False
        datos_caso["a_los_imputados_oficio"] = "al imputado" if not f else "a la imputada"
        datos_caso["bloque_imputados_oficios"] = bloques_oficios[0] if bloques_oficios else ""
        datos_caso["quienes_fueron"] = "Quien fue aprehendido" if not f else "Quien fue aprehendida"
        datos_caso["dicho_imputado"] = "Dicho imputado será puesto" if not f else "Dicha imputada será puesta"
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

def generar_paquete_diligencias(datos_caso: dict, carpeta_salida="expediente_generado"):
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