"""Windows-only backdrop helpers (Mica/Acrylic + dark titlebar).

Safe no-op on non-Windows platforms. All public functions return a bool and
never raise.
"""

from __future__ import annotations

from typing import Optional

import ctypes
import sys


# DWM window attributes
_DWMWA_USE_IMMERSIVE_DARK_MODE_1809 = 19
_DWMWA_USE_IMMERSIVE_DARK_MODE_1903 = 20
_DWMWA_SYSTEMBACKDROP_TYPE = 38
_DWMWA_WINDOW_CORNER_PREFERENCE = 33


# DWM system backdrop types (DWMSBT_*)
_DWMSBT_AUTO = 0
_DWMSBT_NONE = 1
_DWMSBT_MAINWINDOW = 2  # Mica (Win11)
_DWMSBT_TRANSIENTWINDOW = 3
_DWMSBT_TABBEDWINDOW = 4


# DWM window corner preference (DWM_WINDOW_CORNER_PREFERENCE)
_DWMWCP_DEFAULT = 0
_DWMWCP_DONOTROUND = 1
_DWMWCP_ROUND = 2
_DWMWCP_ROUNDSMALL = 3


def set_window_corner_preference(hwnd: int, preference: int) -> bool:
    """Set Win11 rounded corner preference for a window.

    Works best on Windows 11+. Safe no-op on unsupported systems.
    """

    if not _is_windows() or not hwnd:
        return False

    try:
        dwmapi = _load_windll("dwmapi")
        if dwmapi is None:
            return False

        DwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute
        DwmSetWindowAttribute.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        DwmSetWindowAttribute.restype = ctypes.c_int  # HRESULT

        value = ctypes.c_int(int(preference))
        hr = int(
            DwmSetWindowAttribute(
                ctypes.c_void_p(int(hwnd)),
                ctypes.c_uint(_DWMWA_WINDOW_CORNER_PREFERENCE),
                ctypes.byref(value),
                ctypes.c_uint(ctypes.sizeof(value)),
            )
        )
        return hr == 0
    except Exception:
        return False


# SetWindowCompositionAttribute (undocumented)
_WCA_ACCENT_POLICY = 19
_ACCENT_DISABLED = 0
_ACCENT_ENABLE_ACRYLICBLURBEHIND = 4


def apply_backdrop(
    hwnd: int,
    *,
    prefer_mica: bool = True,
    dark_titlebar: bool = True,
    acrylic_gradient_color: int = 0xCC000000,
) -> bool:
    """Apply Win11 Mica (preferred) or fallback Acrylic blur; optionally set dark titlebar."""

    if not _is_windows() or not hwnd:
        return False

    if dark_titlebar:
        # Titlebar setting is best-effort and does not affect the final result.
        set_immersive_dark_titlebar(hwnd, True)

    ok_backdrop = False
    if prefer_mica:
        ok_backdrop = set_system_backdrop_type(hwnd, _DWMSBT_MAINWINDOW)

    if not ok_backdrop:
        ok_backdrop = set_acrylic_blur(hwnd, True, gradient_color=acrylic_gradient_color)

    return bool(ok_backdrop)


def set_immersive_dark_titlebar(hwnd: int, enabled: bool = True) -> bool:
    """Toggle immersive dark titlebar (best-effort)."""

    if not _is_windows() or not hwnd:
        return False

    try:
        dwmapi = _load_windll("dwmapi")
        if dwmapi is None:
            return False

        DwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute
        DwmSetWindowAttribute.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        DwmSetWindowAttribute.restype = ctypes.c_int  # HRESULT

        value = ctypes.c_int(1 if enabled else 0)
        size = ctypes.sizeof(value)

        # Try the newer attribute first; fall back to the older one.
        for attr in (_DWMWA_USE_IMMERSIVE_DARK_MODE_1903, _DWMWA_USE_IMMERSIVE_DARK_MODE_1809):
            hr = int(
                DwmSetWindowAttribute(
                    ctypes.c_void_p(int(hwnd)),
                    ctypes.c_uint(attr),
                    ctypes.byref(value),
                    ctypes.c_uint(size),
                )
            )
            if hr == 0:
                return True
        return False
    except Exception:
        return False


def set_system_backdrop_type(hwnd: int, backdrop_type: int) -> bool:
    """Set DWMWA_SYSTEMBACKDROP_TYPE (Win11 Mica/Tabbed/etc)."""

    if not _is_windows() or not hwnd:
        return False

    try:
        dwmapi = _load_windll("dwmapi")
        if dwmapi is None:
            return False

        DwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute
        DwmSetWindowAttribute.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        DwmSetWindowAttribute.restype = ctypes.c_int  # HRESULT

        value = ctypes.c_int(int(backdrop_type))
        hr = int(
            DwmSetWindowAttribute(
                ctypes.c_void_p(int(hwnd)),
                ctypes.c_uint(_DWMWA_SYSTEMBACKDROP_TYPE),
                ctypes.byref(value),
                ctypes.c_uint(ctypes.sizeof(value)),
            )
        )
        return hr == 0
    except Exception:
        return False


def set_acrylic_blur(hwnd: int, enabled: bool = True, *, gradient_color: int = 0xCC000000) -> bool:
    """Enable Acrylic blur via SetWindowCompositionAttribute (Win10/11 best-effort)."""

    if not _is_windows() or not hwnd:
        return False

    try:
        user32 = _load_windll("user32")
        if user32 is None:
            return False

        SetWindowCompositionAttribute = getattr(user32, "SetWindowCompositionAttribute", None)
        if SetWindowCompositionAttribute is None:
            return False

        class _ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint32),
                ("AnimationId", ctypes.c_int),
            ]

        class _WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t),
            ]

        SetWindowCompositionAttribute.argtypes = [ctypes.c_void_p, ctypes.POINTER(_WINDOWCOMPOSITIONATTRIBDATA)]
        SetWindowCompositionAttribute.restype = ctypes.c_int  # BOOL

        accent_state = _ACCENT_ENABLE_ACRYLICBLURBEHIND if enabled else _ACCENT_DISABLED
        accent = _ACCENT_POLICY(
            AccentState=int(accent_state),
            AccentFlags=2 if enabled else 0,
            GradientColor=int(gradient_color) & 0xFFFFFFFF,
            AnimationId=0,
        )

        data = _WINDOWCOMPOSITIONATTRIBDATA(
            Attribute=_WCA_ACCENT_POLICY,
            Data=ctypes.cast(ctypes.byref(accent), ctypes.c_void_p),
            SizeOfData=ctypes.sizeof(accent),
        )

        ok = int(SetWindowCompositionAttribute(ctypes.c_void_p(int(hwnd)), ctypes.byref(data))) != 0
        return bool(ok)
    except Exception:
        return False


def _is_windows() -> bool:
    return sys.platform == "win32"


def _load_windll(name: str) -> Optional[ctypes.CDLL]:
    if not _is_windows():
        return None
    try:
        # WinDLL uses stdcall which matches most Win32 APIs.
        return ctypes.WinDLL(name)
    except Exception:
        return None
