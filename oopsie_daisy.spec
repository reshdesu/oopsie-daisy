# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
datas = []

# Hidden imports for Windows 11 compatibility
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'send2trash',
    'numpy',
    'psutil',
    'pathlib',
    'typing',
    'subprocess',
    'platform',
    'concurrent.futures',
    'threading',
    'queue',
    'time',
    'sys',
    'os',
    'math',
    'random',
    'encodings.cp1252',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
]

# Try to include OpenCL if available
try:
    import pyopencl
    hiddenimports.extend([
        'pyopencl',
        'pyopencl.tools',
        'pyopencl.elementwise',
        'pyopencl.reduction'
    ])
except ImportError:
    pass

a = Analysis(
    ['src/oopsie_daisy/__init__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OopsieDaisy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)