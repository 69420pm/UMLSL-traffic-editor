# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pse/umlsl_editor/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['networkx', 'matplotlib'],
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
    [],
    exclude_binaries=True,
    name='UMLSL Traffic Visual Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UMLSL Traffic Visual Editor',
)
app = BUNDLE(
    coll,
    name='UMLSL Traffic Visual Editor.app',
    icon=None,
    bundle_identifier=None,
)
