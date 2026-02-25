#!/usr/bin/env python
# -*- mode: python ; coding: utf-8 -*-

# NOTE: This spec is executed by PyInstaller at build time.
# When building from a conda environment, many runtime DLLs live in
# $CONDA_PREFIX/Library/bin and are not discoverable unless that directory is
# on PATH. If these DLLs are missed, the packaged app may crash at startup
# (e.g. _ctypes.pyd failing to load due to missing ffi.dll).

import os
import sys
from pathlib import Path
from typing import Optional

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('matplotlib')
hiddenimports += collect_submodules('PySide6')


def _prepend_to_path(path: Path) -> None:
    if not path.exists():
        return
    current = os.environ.get("PATH", "")
    os.environ["PATH"] = str(path) + os.pathsep + current


def _find_dll(dll_dirs: list[Path], name: str) -> Optional[Path]:
    # Fast path: exact match.
    for directory in dll_dirs:
        candidate = directory / name
        if candidate.exists():
            return candidate
    # Case-insensitive fallback / alternate naming (e.g. LIBBZ2.dll vs libbz2.dll).
    lowered = name.lower()
    for directory in dll_dirs:
        try:
            for entry in directory.iterdir():
                if entry.is_file() and entry.name.lower() == lowered:
                    return entry
        except FileNotFoundError:
            continue
    return None


# Make conda's DLLs discoverable for dependency resolution.
_prefix = Path(sys.base_prefix)
_dll_dirs = [_prefix / "Library" / "bin", _prefix / "DLLs"]
for _dir in _dll_dirs:
    _prepend_to_path(_dir)

# Defensive: explicitly bundle core conda DLLs that Python stdlib extensions
# (and PyInstaller runtime hooks) often need at startup.
_dll_names = [
    "ffi.dll",
    "libcrypto-3-x64.dll",
    "libssl-3-x64.dll",
    "liblzma.dll",
    "libbz2.dll",
    "libexpat.dll",
    "sqlite3.dll",
    "tcl86t.dll",
    "tk86t.dll",
]
_extra_binaries: list[tuple[str, str]] = []
for _name in _dll_names:
    _path = _find_dll(_dll_dirs, _name)
    if _path is not None:
        _extra_binaries.append((str(_path), "."))


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=_extra_binaries,
    datas=[('visulite', 'visulite')],
    hiddenimports=hiddenimports,
    # Local hooks override problematic upstream hooks in some environments.
    hookspath=['hooks'],
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
    name='VisuLite',
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
    name='VisuLite',
)
