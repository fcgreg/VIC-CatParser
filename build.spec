# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

ijson_hiddenimports = collect_submodules('ijson') + [
    'ijson.backends',
    'ijson.backends.python',
    'ijson.backends.yajl2_c',
    'ijson.backends.yajl2_cffi',
]

core_hiddenimports = ijson_hiddenimports + [
    'tqdm',
    'vic_catparser',
    'vic_catparser.parser',
    'vic_catparser.formatter',
    'vic_catparser.service',
    'vic_catparser.cli',
]

# ---------------------------------------------------------------------------
# CLI target: VIC-CatParser.exe (console)
# ---------------------------------------------------------------------------
cli_a = Analysis(
    ['vic_catparser/cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=core_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['customtkinter', 'tkinterdnd2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name='VIC-CatParser',
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

# ---------------------------------------------------------------------------
# GUI target: VIC-CatParser-GUI.exe (windowed)
# ---------------------------------------------------------------------------
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

gui_hiddenimports = core_hiddenimports + list(ctk_hiddenimports) + [
    'tkinterdnd2',
]

gui_datas = ctk_datas + collect_data_files('tkinterdnd2')

gui_a = Analysis(
    ['gui/app.py'],
    pathex=['.'],
    binaries=ctk_binaries,
    datas=gui_datas,
    hiddenimports=gui_hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_customtkinter.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name='VIC-CatParser-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Both executables share one folder and one _internal runtime.
coll = COLLECT(
    cli_exe,
    gui_exe,
    cli_a.binaries,
    gui_a.binaries,
    cli_a.zipfiles,
    gui_a.zipfiles,
    cli_a.datas,
    gui_a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='VIC-CatParser',
)
