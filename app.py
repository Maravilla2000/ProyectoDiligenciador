import datetime
import io
import os
import zipfile
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from catalogo import CATALOGO_AGENTES, CATALOGO_DELITOS, OPCION_DELITO_MANUAL
from generador import generar_paquete_diligencias, numero_a_letras, unir_con_y


def hora_a_letras(h: int) -> str:
    horas_dict = {
        0: "CERO",
        1: "UNA",
        2: "DOS",
        3: "TRES",
        4: "CUATRO",
        5: "CINCO",
        6: "SEIS",
        7: "SIETE",
        8: "OCHO",
        9: "NUEVE",
        10: "DIEZ",
        11: "ONCE",
        12: "DOCE",
        13: "TRECE",
        14: "CATORCE",
        15: "QUINCE",
        16: "DIECISEIS",
        17: "DIECISIETE",
        18: "DIECIOCHO",
        19: "DIECINUEVE",
        20: "VEINTE",
        21: "VEINTIUNO",
        22: "VEINTIDÓS",
        23: "VEINTITRÉS",
    }
    return horas_dict.get(h, str(h))


def anio_a_letras(a: int) -> str:
    anios = {
        2024: "DOS MIL VEINTICUATRO",
        2025: "DOS MIL VEINTICINCO",
        2026: "DOS MIL VEINTISEIS",
    }
    return anios.get(a, f"DOS MIL {a % 100}")


def configurar_pagina() -> None:
    st.set_page_config(page_title="Generador Policial", layout="wide")
    st.title("Generador Automático de Diligencias C.P. Maravilla versión 1.5")


def obtener_nombres_agentes() -> list[str]:
    return [agente["nombre"] for agente in CATALOGO_AGENTES if agente["nombre"] != "OTRO / INGRESAR MANUALMENTE"]


def buscar_agente_por_nombre(nombre: str) -> dict:
    return next((agente for agente in CATALOGO_AGENTES if agente["nombre"] == nombre), CATALOGO_AGENTES[0])


def inicializar_fecha_hora() -> None:
    if "fecha_inicial" in st.session_state:
        return

    zona_sv = ZoneInfo("America/El_Salvador")
    ahora_sv = datetime.datetime.now(zona_sv)
    st.session_state.fecha_inicial = ahora_sv.date()
    st.session_state.hora_inicial = ahora_sv.time().replace(second=0, microsecond=0)


def render_tipo_procedimiento() -> str:
    st.subheader("Tipo de Procedimiento")
    modo = st.radio(
        "Seleccione cómo desea ingresar a los involucrados:",
        [
            "Procedimiento Individual (1 Imputado y 1 Víctima)",
            "Procedimiento Múltiple (Varias Víctimas o Imputados con Delitos Propios)",
        ],
        horizontal=True,
    )
    st.divider()
    return modo


def render_fechas_y_agentes() -> dict:
    st.subheader("1. Fecha, Hora y Agentes Captores")
    inicializar_fecha_hora()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_acta_input = st.date_input("Fecha del Procedimiento", value=st.session_state.fecha_inicial)
    with col_f2:
        hora_acta_input = st.time_input("Hora del Procedimiento", value=st.session_state.hora_inicial, step=60)

    nombres_agentes = obtener_nombres_agentes()
    col1, col2, col3 = st.columns(3)
    with col1:
        codigo_expediente = st.text_input("Código de Expediente / Ref.", "001-2026")
        lugar_acta = st.text_input("Lugar del Acta", "EN EL PUESTO DE LA POLICIA NACIONAL CIVIL DE POLITUR SALINITAS...")
        lugar_resguardo = st.text_input("Lugar Custodia / Resguardo", "bartolinas del nueve once de Sonsonate")
        unidad_policial = st.text_input("Unidad Policial", "POLITUR SALINITAS")

    with col2:
        captor_1_sel = st.selectbox(
            "Captor 1",
            nombres_agentes,
            index=nombres_agentes.index("TITO BENJAMÍN GARCÍA CACERES") if "TITO BENJAMÍN GARCÍA CACERES" in nombres_agentes else 0,
        )
        agente_1_info = buscar_agente_por_nombre(captor_1_sel)
        nombre_agente_1 = agente_1_info["nombre"]
        oni_agente_1 = agente_1_info["oni_letras"]
        cargo_nombre_agente_1 = f"{agente_1_info['grado']} {agente_1_info['nombre']}"
        st.text_input("ONI Captor 1 (En letras)", value=oni_agente_1, disabled=True)

        captor_2_sel = st.selectbox(
            "Captor 2",
            nombres_agentes,
            index=nombres_agentes.index("GERARDO ENRIQUE HERNANDEZ MARAVILLA") if "GERARDO ENRIQUE HERNANDEZ MARAVILLA" in nombres_agentes else (1 if len(nombres_agentes) > 1 else 0),
        )
        agente_2_info = buscar_agente_por_nombre(captor_2_sel)
        nombre_agente_2 = agente_2_info["nombre"]
        oni_agente_2 = agente_2_info["oni_letras"]
        cargo_nombre_agente_2 = f"{agente_2_info['grado']} {agente_2_info['nombre']}"
        st.text_input("ONI Captor 2 (En letras)", value=oni_agente_2, disabled=True)

    with col3:
        emisor_sel = st.selectbox(
            "Emisor Oficios (Quien firma)",
            nombres_agentes,
            index=nombres_agentes.index("SAUL HUMBERTO PARADA CASTRO") if "SAUL HUMBERTO PARADA CASTRO" in nombres_agentes else 0,
        )
        emisor_info = buscar_agente_por_nombre(emisor_sel)
        emisor_grado_nombre = f"{emisor_info['grado']}. {emisor_info['nombre']}"
        st.text_input("Grado y Nombre del Emisor", value=emisor_grado_nombre, disabled=True)

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        nombre_investigador = st.text_input("Nombre del Investigador", "Inv. Peliguey")
    with col_inv2:
        codigo_sati = st.text_input("Código SATI", "S/N")

    st.divider()
    return {
        "codigo_expediente": codigo_expediente,
        "lugar_acta": lugar_acta,
        "lugar_resguardo": lugar_resguardo,
        "unidad_policial": unidad_policial,
        "fecha_acta_input": fecha_acta_input,
        "hora_acta_input": hora_acta_input,
        "nombre_agente_1": nombre_agente_1,
        "oni_agente_1": oni_agente_1,
        "cargo_nombre_agente_1": cargo_nombre_agente_1,
        "nombre_agente_2": nombre_agente_2,
        "oni_agente_2": oni_agente_2,
        "cargo_nombre_agente_2": cargo_nombre_agente_2,
        "emisor_grado_nombre": emisor_grado_nombre,
        "nombre_investigador": nombre_investigador,
        "codigo_sati": codigo_sati,
    }


def render_individual() -> tuple[list[dict], list[dict]]:
    st.subheader("2. Datos del Imputado y Delito(s)")
    tipo_delito = st.radio("Cantidad de Delitos:", ["Un Delito", "Múltiples Delitos"], horizontal=True)

    if tipo_delito == "Un Delito":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            delito_seleccionado = st.selectbox("Seleccionar Delito del Catálogo", list(CATALOGO_DELITOS.keys()))
            delito_ind = st.text_input("Escriba el Delito", "") if delito_seleccionado == OPCION_DELITO_MANUAL else delito_seleccionado
        with col_d2:
            art_sugerido = CATALOGO_DELITOS.get(delito_seleccionado, "")
            articulo_cp_ind = st.text_input("Artículo C.P.", value=art_sugerido)
    else:
        opciones_delitos = [key for key in CATALOGO_DELITOS.keys() if key != OPCION_DELITO_MANUAL]
        delitos_mult = st.multiselect("Seleccionar Delitos Múltiples del Catálogo", opciones_delitos)
        delito_manual_extra = st.text_input("Delito adicional manual (opcional, si no está en catálogo)", "")

        lista_delitos = list(delitos_mult)
        if delito_manual_extra.strip():
            lista_delitos.append(delito_manual_extra.strip().upper())

        articulos_mult = [CATALOGO_DELITOS.get(delito, "") for delito in delitos_mult]
        art_manual_extra = st.text_input("Artículo C.P. para delito manual extra (si aplica)", "")
        if art_manual_extra.strip():
            articulos_mult.append(art_manual_extra.strip())

        delito_ind = unir_con_y(lista_delitos) if lista_delitos else ""
        articulo_cp_ind = unir_con_y([valor for valor in articulos_mult if valor]) if articulos_mult else ""

        st.info(f"📌 **Delito resultante:** {delito_ind if delito_ind else 'Ninguno seleccionado'}")
        st.info(f"📜 **Artículo(s) resultante:** {articulo_cp_ind if articulo_cp_ind else 'Ninguno seleccionado'}")

    col4_a, col4_b, col4_c = st.columns(3)
    with col4_a:
        imp_nombre = st.text_input("Nombre Completo (Imputado)", "JUAN ANTONIO RIVERA")
        imp_genero = st.selectbox("Género", ["Masculino", "Femenino"], key="g_imp")
        imp_edad = st.text_input("Edad", "44")
        imp_identidad = st.text_input("DUI (Dejar vacío para texto por defecto)", "06148510-8")
        imp_nacionalidad = st.text_input("Nacionalidad", "Salvadoreña")
    with col4_b:
        imp_alias = st.text_input("Alias", "")
        imp_pandilla = st.text_input("Pandilla", "")
        imp_estado_civil = st.text_input("Estado Civil", "Soltero")
        imp_profesion = st.text_input("Profesión/Oficio", "Jornalero")
        imp_fecha_nac = st.text_input("Fecha de Nacimiento", "10/05/1979")
    with col4_c:
        imp_origen = st.text_input("Originario de", "Acajutla")
        imp_padre = st.text_input("Padre", "")
        imp_madre = st.text_input("Madre", "")
        imp_parentesco = st.text_input("Familiar a avisar (Parentesco)", "hermana")
        imp_aviso = st.text_input("Nombre del Familiar", "Enma Rivera")

    imp_residencia = st.text_area(
        "Residencia del Imputado",
        "Comunidad los Almendros, Cantón Punta Remedios, municipio de Acajutla",
        height=68,
    )

    st.subheader("3. Datos de la Víctima")
    col5, col6 = st.columns(2)
    with col5:
        vic_nombre = st.text_input("Nombre Víctima", "YOLANDA SANTAMARIA MARROQUÍN")
        vic_genero = st.selectbox("Género", ["Femenino", "Masculino"], key="g_vic")
        vic_edad = st.text_input("Edad Víctima", "52")
    with col6:
        vic_dui = st.text_input("DUI Víctima (Puedes ingresar los números)", "02956955-0")
        vic_residencia = st.text_area(
            "Residencia Víctima",
            "Comunidad los Almendros, Cantón Punta Remedios, municipio de Acajutla",
            height=100,
        )

    imputados_lista = [{
        "Nombre": imp_nombre,
        "Género": imp_genero,
        "Edad": imp_edad,
        "Nacionalidad": imp_nacionalidad,
        "Delito": delito_ind,
        "Articulo_CP": articulo_cp_ind,
        "Identidad": imp_identidad,
        "Alias": imp_alias,
        "Estado_Civil": imp_estado_civil,
        "Profesion": imp_profesion,
        "Origen": imp_origen,
        "Fecha_Nac": imp_fecha_nac,
        "Pandilla": imp_pandilla,
        "Padre": imp_padre,
        "Madre": imp_madre,
        "Residencia": imp_residencia,
        "Parentesco_Aviso": imp_parentesco,
        "Nombre_Aviso": imp_aviso,
    }]
    victimas_lista = [{
        "Nombre": vic_nombre,
        "Género": vic_genero,
        "Edad": vic_edad,
        "DUI": vic_dui,
        "Residencia": vic_residencia,
    }]
    return imputados_lista, victimas_lista


def render_multiple() -> tuple[list[dict], list[dict]]:
    st.subheader("2. Imputados y sus Delitos")
    st.info("💡 Escribe el delito y el artículo directamente en cada celda. Abajo tienes el catálogo de referencia para copiar/pegar.")

    with st.expander("📖 Ver catálogo de delitos y artículos (referencia)"):
        for delito, articulo in CATALOGO_DELITOS.items():
            if delito != OPCION_DELITO_MANUAL:
                st.write(f"- **{delito}** → {articulo}")

    if "df_imp" not in st.session_state:
        st.session_state.df_imp = pd.DataFrame([{
            "Nombre": "JUAN ANTONIO RIVERA",
            "Género": "Masculino",
            "Edad": "44",
            "Delito": "LESIONES",
            "Delito_Manual": "",
            "Articulo_CP": "ciento cuarenta y dos",
            "Nacionalidad": "Salvadoreña",
            "Identidad": "",
            "Alias": "",
            "Estado_Civil": "Soltero",
            "Profesion": "Jornalero",
            "Origen": "Acajutla",
            "Fecha_Nac": "10/05/1979",
            "Pandilla": "",
            "Padre": "",
            "Madre": "",
            "Residencia": "Comunidad los Almendros",
            "Parentesco_Aviso": "hermana",
            "Nombre_Aviso": "Enma Rivera",
        }])

    df_imputados = st.data_editor(st.session_state.df_imp, num_rows="dynamic", use_container_width=True, key="tabla_imp_editor")

    st.subheader("3. Víctimas")
    if "df_vic" not in st.session_state:
        st.session_state.df_vic = pd.DataFrame([{
            "Nombre": "YOLANDA SANTAMARIA MARROQUÍN",
            "Género": "Femenino",
            "Edad": "52",
            "DUI": "02956955-0",
            "Residencia": "Comunidad los Almendros, Acajutla",
        }])

    df_victimas = st.data_editor(st.session_state.df_vic, num_rows="dynamic", use_container_width=True, key="tabla_vic_editor")

    imputados_lista = []
    for fila in df_imputados.fillna("").to_dict("records"):
        delito_final = fila.get("Delito", "").strip()
        manual = fila.get("Delito_Manual", "").strip()
        if delito_final == OPCION_DELITO_MANUAL:
            delito_final = manual.upper() if manual else ""
        fila["Delito"] = delito_final
        fila.pop("Delito_Manual", None)
        imputados_lista.append(fila)

    victimas_lista = df_victimas.fillna("").to_dict("records")
    return imputados_lista, victimas_lista


def render_relato() -> tuple[str, str]:
    st.subheader("4. Relato del Hecho")
    lugar_hecho = st.text_input(
        "Ubicación Hecho (Oficios)",
        "sobre la calle que conduce a Playa Los Almendros, Cantón Punta Remedios",
    )
    relato_hecho = st.text_area("Relato del Hecho (Acta)", "en momentos que nos encontrábamos...", height=120)
    return lugar_hecho, relato_hecho


def validar_caso(imputados_lista: list[dict], victimas_lista: list[dict]) -> list[str]:
    errores = []
    if not imputados_lista:
        errores.append("Debe haber al menos un imputado.")
    for indice, imputado in enumerate(imputados_lista, start=1):
        if not imputado.get("Nombre", "").strip():
            errores.append(f"Imputado #{indice}: falta el Nombre.")
        if not imputado.get("Delito", "").strip():
            errores.append(f"Imputado #{indice}: falta el Delito.")
        if not imputado.get("Articulo_CP", "").strip():
            errores.append(f"Imputado #{indice}: falta el Artículo C.P.")

    if not victimas_lista:
        errores.append("Debe haber al menos una víctima.")
    for indice, victima in enumerate(victimas_lista, start=1):
        if not victima.get("Nombre", "").strip():
            errores.append(f"Víctima #{indice}: falta el Nombre.")

    return errores


def construir_datos_caso(configuracion: dict, imputados_lista: list[dict], victimas_lista: list[dict], lugar_hecho: str, relato_hecho: str) -> dict:
    meses_lista = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
    ]
    fecha_acta = configuracion["fecha_acta_input"]
    hora_acta = configuracion["hora_acta_input"]

    return {
        "codigo_expediente": configuracion["codigo_expediente"],
        "lugar_acta": configuracion["lugar_acta"],
        "hora_acta_texto": hora_a_letras(hora_acta.hour),
        "minutos_acta_texto": numero_a_letras(hora_acta.minute),
        "dia_acta_texto": numero_a_letras(fecha_acta.day),
        "mes_acta_texto": meses_lista[fecha_acta.month - 1],
        "anio_acta_texto": anio_a_letras(fecha_acta.year),
        "nombre_agente_1": configuracion["nombre_agente_1"],
        "oni_agente_1": configuracion["oni_agente_1"],
        "nombre_agente_2": configuracion["nombre_agente_2"],
        "oni_agente_2": configuracion["oni_agente_2"],
        "cargo_nombre_agente_1": configuracion["cargo_nombre_agente_1"],
        "cargo_nombre_agente_2": configuracion["cargo_nombre_agente_2"],
        "relato_hecho": relato_hecho,
        "lugar_resguardo": configuracion["lugar_resguardo"],
        "unidad_policial": configuracion["unidad_policial"],
        "emisor_grado_nombre": configuracion["emisor_grado_nombre"],
        "numero_oficio": "S/N",
        "lugar_hecho": lugar_hecho,
        "fecha_oficio": f"{fecha_acta.day:02d} de {meses_lista[fecha_acta.month - 1].lower()} del {fecha_acta.year}",
        "fecha_hecho": f"{fecha_acta.day:02d}/{fecha_acta.month:02d}/{fecha_acta.year}",
        "hora_hecho": f"{hora_acta.hour:02d}:{hora_acta.minute:02d}",
        "nombre_investigador": configuracion["nombre_investigador"],
        "codigo_sati": configuracion["codigo_sati"],
        "lista_imputados": imputados_lista,
        "lista_victimas": victimas_lista,
    }


def descargar_expediente(archivos: list[str], fecha_acta_input: datetime.date) -> None:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for ruta_archivo in archivos:
            if os.path.exists(ruta_archivo):
                zip_file.write(ruta_archivo, os.path.basename(ruta_archivo))
    zip_buffer.seek(0)

    nombre_zip = f"expediente_{fecha_acta_input.strftime('%Y-%m-%d')}_{datetime.datetime.now().strftime('%H%M%S')}.zip"
    st.download_button(
        label="📥 Descargar expediente completo (.zip)",
        data=zip_buffer,
        file_name=nombre_zip,
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )
    st.caption("📁 Los archivos también quedaron guardados en la carpeta `expediente_generado/`.")


def main() -> None:
    configurar_pagina()
    modo = render_tipo_procedimiento()
    configuracion = render_fechas_y_agentes()

    if modo == "Procedimiento Individual (1 Imputado y 1 Víctima)":
        imputados_lista, victimas_lista = render_individual()
    else:
        imputados_lista, victimas_lista = render_multiple()

    st.divider()
    lugar_hecho, relato_hecho = render_relato()
    enviado = st.button("Generar Expediente Completo", type="primary")

    if not enviado:
        return

    errores = validar_caso(imputados_lista, victimas_lista)
    if errores:
        st.error("⚠️ Corrige los siguientes errores antes de generar:\n\n- " + "\n- ".join(errores))
        return

    datos_caso = construir_datos_caso(configuracion, imputados_lista, victimas_lista, lugar_hecho, relato_hecho)
    try:
        archivos = generar_paquete_diligencias(datos_caso)
        st.success(f"¡Expediente generado con éxito! Se crearon {len(archivos)} documentos.")
        descargar_expediente(archivos, configuracion["fecha_acta_input"])
    except Exception as exc:
        st.error(f"Error al generar el expediente: {exc}")


if __name__ == "__main__":
    main()
