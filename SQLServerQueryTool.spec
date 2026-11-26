# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['C:/Users/6801179/AppData/Local/Programs/Python/Python313/Lib', 'C:/Users/6801179/AppData/Local/Programs/Python/Python313/DLLs'],
    binaries=[('C:/Users/6801179/AppData/Local/Programs/Python/Python313/DLLs/tcl86t.dll', '.'), ('C:/Users/6801179/AppData/Local/Programs/Python/Python313/DLLs/tk86t.dll', '.')],
    datas=[('C:/Users/6801179/AppData/Local/Programs/Python/Python313/tcl/tcl8.6', '_tcl_data'), ('C:/Users/6801179/AppData/Local/Programs/Python/Python313/tcl/tk8.6', '_tk_data')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.simpledialog', '_tkinter'],
    hookspath=['pyinstaller_hooks'],
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
    name='SQLServerQueryTool',
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
