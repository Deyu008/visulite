"""Runtime tweaks that QSS alone cannot reliably achieve.

On Windows 11, translucent popup windows (needed for QSS border-radius to show
true rounded corners) can produce black artifacts in the corner/shadow regions.

This module prefers using Windows DWM rounded window corners for QMenu popups.
That avoids translucency and keeps the popup edges clean.
"""

from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QApplication, QMenu

from visulite.ui.windows_backdrop import (
    _DWMWCP_ROUND,
    set_window_corner_preference,
)


def _polish_menu(menu: QMenu) -> None:
    # Avoid re-polishing the same menu repeatedly.
    if bool(menu.property("_visulite_polished")):
        return
    menu.setProperty("_visulite_polished", True)

    # Prevent the platform style from filling a square background under our
    # rounded QSS background.
    menu.setAutoFillBackground(False)
    menu.setAttribute(Qt.WA_StyledBackground, True)
    menu.setAttribute(Qt.WA_NoSystemBackground, False)

    # Prefer OS-rounded corners without translucency to avoid black artifacts.
    if sys.platform == "win32":
        hwnd = int(menu.winId())
        set_window_corner_preference(hwnd, _DWMWCP_ROUND)

    menu.setAttribute(Qt.WA_TranslucentBackground, False)


class _PopupPolishFilter(QObject):
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # type: ignore[override]
        # Limit to QMenu only.
        # Polishing private popup containers (e.g. combo boxes) can trigger
        # platform-specific Qt crashes on Windows.
        if isinstance(obj, QMenu) and event.type() in (QEvent.Polish, QEvent.Show):
            _polish_menu(obj)
        return super().eventFilter(obj, event)


def install_popup_tweaks(app: Optional[QApplication] = None) -> None:
    """Install the popup polish filter.

    Must keep a reference to the filter, otherwise Python GC will collect it and
    the event filter will silently stop working.
    """

    if app is None:
        app = QApplication.instance()
        if app is None:
            return

    if getattr(app, "_visulite_popup_filter", None) is not None:
        return

    filt = _PopupPolishFilter(app)
    app.installEventFilter(filt)
    setattr(app, "_visulite_popup_filter", filt)


__all__ = ["install_popup_tweaks"]
