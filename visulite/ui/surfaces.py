"""Reusable surface containers.

These wrappers provide a consistent structure for:
- stroke (border) and rounded corners via QSS,
- subtle shadows via QGraphicsDropShadowEffect,
- optional glass-like (semi-transparent) containers.

The actual visuals are defined in QSS using the `surface` dynamic property.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame


class SurfaceFrame(QFrame):
    """A styled container with a `surface` dynamic property.

    Valid values (enforced by convention in QSS):
    - glass
    - card
    - panel
    """

    def __init__(
        self,
        *,
        surface: str,
        parent: Optional[QFrame] = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("surface", surface)
        # Ensure QSS background is painted for frames.
        self.setAttribute(Qt.WA_StyledBackground, True)


class ColorSwatch(QFrame):
    """A small, rounded color preview that does not rely on per-widget stylesheets."""

    def __init__(self, color: str = "#1f77b4", parent: Optional[QFrame] = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setProperty("class", "swatch")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(24, 24)

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        # Paint the color fill inside the styled border.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Leave a 1px inset so the QSS border stays crisp.
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = min(rect.width(), rect.height()) / 2.5
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._color)
        painter.drawRoundedRect(rect, radius, radius)


__all__ = ["SurfaceFrame", "ColorSwatch"]

