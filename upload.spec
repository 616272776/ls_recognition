# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['upload.py'],
    pathex=['../testorc/Lib/site-packages/paddleocr', '../testorc/Lib/site-packages/paddle/libs'],
    binaries=[('../testorc/Lib/site-packages/paddle/libs', '.')],
    datas=[('../testorc/Lib/site-packages/paddle/fluid/proto', 'paddle/fluid/proto'), ('../testorc/Lib/site-packages/paddleocr/ppocr', 'ppocr')],
    hiddenimports=['framework_pb2', 'scipy.special.cython_special', 'skimage', 'skimage.feature._orb_descriptor_positions', 'skimage.filters.edges'],
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
    name='upload',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
