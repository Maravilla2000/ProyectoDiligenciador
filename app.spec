# -*- mode: python ; coding: utf-8 -*-

import os
import streamlit

streamlit_path = os.path.dirname(streamlit.__file__)

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('generador.py', '.'),
        ('plantillas', 'plantillas'),
        (streamlit_path, 'streamlit'),
    ],
    hiddenimports=[
        'streamlit',
        'docxtpl',
        'docx',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GeneradorDiligencias',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Cambiar a False si no deseas que se vea la consola negra de fondo
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeneradorDiligencias',
)