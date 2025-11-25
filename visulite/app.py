"""Application bootstrap helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import QApplication

from .common.logging import configure_logging
from .ui.main_window import MainWindow
from .ui.styles import QSS


def run_app() -> int:
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

    # Apply modern QSS style
    app.setStyleSheet(QSS)

    window = MainWindow()
    window.show()
    return app.exec()


__all__ = ["run_app"]
