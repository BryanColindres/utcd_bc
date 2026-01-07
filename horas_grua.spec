# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['ui']
hiddenimports += collect_submodules('ui')


a = Analysis(
    ['horas_grua\\ui\\loging.py'],
    pathex=['horas_grua'],
    binaries=[],
    datas=[('horas_grua/resources/plantilla_control_servicios.xlsx', 'resources'), ('horas_grua/imagenes/grua.png', 'imagenes')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='horas_grua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
