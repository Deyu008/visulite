"""Application bootstrap helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont, QIcon, QPalette
from PySide6.QtWidgets import QApplication, QToolTip

from .common.logging import configure_logging
from .ui.main_window import MainWindow
from .ui.styles import QSS_LIGHT, QSS_DARK


def run_app(dark_mode: bool = False) -> int:
    """Entrypoint used by ``python -m visulite`` as well as ``main.py``."""
    configure_logging()

    app = QApplication.instance()
    if app is None:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        app = QApplication(sys.argv)
    app.setApplicationName("VisuLite")
    app.setOrganizationName("VisuLite")
    app.setApplicationDisplayName("VisuLite - Lightweight Visual Analytics")
    QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))

    icon_path = Path(__file__).with_name("resources").joinpath("icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Apply modern QSS style (light or dark)
    app.setStyleSheet(QSS_DARK if dark_mode else QSS_LIGHT)

    # Ensure a valid default font size to avoid QFont::setPointSize warnings
    font: QFont = app.font()
    # Matplotlib/Qt can emit warnings if the font has only pixelSize set.
    if font.pixelSize() > 0:
        font.setPixelSize(0)
    if font.pointSize() <= 0:
        font.setPointSize(11)
    app.setFont(font)
    QToolTip.setFont(font)

    window = MainWindow()
    window.show()
    return app.exec()


__all__ = ["run_app"]
