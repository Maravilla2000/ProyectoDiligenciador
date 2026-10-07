# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_all, copy_metadata

project_dir = SPECPATH
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
tzdata_datas, tzdata_binaries, tzdata_hiddenimports = collect_all("tzdata")

datas = streamlit_datas + tzdata_datas + [
    (os.path.join(project_dir, "app.py"), "."),
    (os.path.join(project_dir, "01_ACTA_DE_REMISION_PLANTILLA.docx"), "."),
    (os.path.join(project_dir, "02_OFICIO_FGR_PLANTILLA.docx"), "."),
    (os.path.join(project_dir, "03_OFICIO_PGR_PLANTILLA.docx"), "."),
    (os.path.join(project_dir, "04_OFICIO_PDH_PLANTILLA.docx"), "."),
    (os.path.join(project_dir, "05_OFICIO_CUSTODIA_911_PLANTILLA.docx"), "."),
    (os.path.join(project_dir, "06_ACTA_DE_IDENTIFICACION_PLANTILLA.docx"), "."),
]
datas += copy_metadata("streamlit")

a = Analysis(
    [os.path.join(project_dir, "run_app.py")],
    pathex=[project_dir],
    binaries=streamlit_binaries + tzdata_binaries,
    datas=datas,
    hiddenimports=[
        "catalogo",
        "generador",
        *streamlit_hiddenimports,
        *tzdata_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GeneradorDiligencias",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
