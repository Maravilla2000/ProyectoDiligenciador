# catalogo.py

# --- CATÁLOGO DE DELITOS ---
CATALOGO_DELITOS = {
    "LESIONES": "ciento cuarenta y dos",
    "AMENAZAS": "ciento cincuenta y cuatro",
    "ROBO": "doscientos trece",
    "ROBO AGRAVADO": "doscientos trece y doscientos catorce",
    "HURTO": "doscientos siete",
    "HURTO AGRAVADO": "doscientos ocho",
    "EXACCIÓN VIOLENTA (EXTORSIÓN)": "doscientos catorce",
    "HOMICIDIO SIMPLE": "ciento veintiocho",
    "HOMICIDIO AGRAVADO": "ciento veintinueve",
    "DISPAROS DE ARMA DE FUEGO": "ciento catorce",
    "POSESIÓN Y TENENCIA DE DROGAS": "treinta y cuatro de la Ley Reguladora de las Actividades Relativas a las Drogas",
    "PORTACIÓN O CONDUCCIÓN ILEGAL DE ARMA DE FUEGO": "trescientos cuarenta y seis-A",
    "AGRUPACIONES ILÍCITAS": "doscientos cuarenta y cinco",
    "RESISTENCIA": "trescientos treinta y siete",
    "VIOLENCIA INTRAFAMILIAR": "doscientos dos-A",
    "CONDUCCIÓN PELIGROSA DE VEHÍCULOS AUTOMOTORES": "ciento cuarenta y siete-A",
    "DAÑOS": "doscientos veintiuno",
    "OTRO / INGRESAR MANUALMENTE": ""
}

# --- CATÁLOGO DE AGENTES ---
CATALOGO_AGENTES = [
    {'grado': 'SUB-INSP.', 'nombre': 'RIGOBERTO ANTONIO FIGUEROA ORELLANA', 'oni_letras': 'E-mil cuatrocientos treinta y siete', 'oni_numeros': 'E-1437'},
    {'grado': 'CABO', 'nombre': 'SAUL HUMBERTO PARADA CASTRO', 'oni_letras': 'once mil seiscientos sesenta', 'oni_numeros': '11660'},
    {'grado': 'CABO', 'nombre': 'RONMEL ANTONIO HUEZO DELGADO', 'oni_letras': 'diecinueve mil quinientos seis', 'oni_numeros': '19506'},
    {'grado': 'AGTE.', 'nombre': 'ROBERTO TOBIAS PEREZ CONCE', 'oni_letras': 'veintiseis mil quinientos noventa y tres', 'oni_numeros': '26593'},
    {'grado': 'AGTE.', 'nombre': 'ALEJANDRO HUMBERTO AGUILAR LEIVA', 'oni_letras': 'veintinueve mil novecientos ochenta y uno', 'oni_numeros': '29981'},
    {'grado': 'AGTE.', 'nombre': 'KEVIN ALEXANDER ALVARADO RAMIREZ', 'oni_letras': 'treinta y cuatro mil ciento sesenta y siete', 'oni_numeros': '34167'},
    {'grado': 'AGTE.', 'nombre': 'GABRIELA BELINDA VASQUEZ GARCÍA', 'oni_letras': 'treinta y cuatro mil seiscientos seis', 'oni_numeros': '34606'},
    {'grado': 'AGTE.', 'nombre': 'BLANCA MARISOL ALVAREZ RIVAS', 'oni_letras': 'treinta y cinco mil novecientos setenta y siete', 'oni_numeros': '35977'},
    {'grado': 'AGTE.', 'nombre': 'DANILO ARMANDO CASTANEDA RUIZ', 'oni_letras': 'treinta y seis mil doscientos quince', 'oni_numeros': '36215'},
    {'grado': 'AGTE.', 'nombre': 'ANA IRIS LOPEZ ESPINOZA', 'oni_letras': 'treinta y seis mil cuatrocientos diez', 'oni_numeros': '36410'},
    {'grado': 'AGTE.', 'nombre': 'GERARDO ENRIQUE HERNANDEZ MARAVILLA', 'oni_letras': 'treinta y seis mil seiscientos noventa y tres', 'oni_numeros': '36693'},
    {'grado': 'OTRO / MANUAL', 'nombre': 'OTRO / INGRESAR MANUALMENTE', 'oni_letras': '', 'oni_numeros': ''}
]

# --- Constante para detectar cuándo usar delito manual en modo múltiple ---
OPCION_DELITO_MANUAL = "OTRO / INGRESAR MANUALMENTE"