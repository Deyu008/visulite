"""Small, reusable visual effects for Qt Widgets.

Keep this module lightweight and safe: effects should be optional and never crash
if the underlying platform/style cannot support them.
"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def apply_subtle_shadow(
    widget: QWidget,
    *,
    blur_radius: int = 28,
    offset_y: int = 8,
    alpha: float = 0.14,
    dark: bool = False,
) -> None:
    """Apply a soft shadow. Intended for a small number of container surfaces.

    Notes:
    - Do not apply to large, frequently repainted views (tables) for performance.
    - Shadow is a visual enhancement only; failure should not affect behavior.
    """

    # Qt expects 0..255 alpha.
    a = max(0, min(255, int(alpha * 255)))
    color = QColor(0, 0, 0, a) if not dark else QColor(0, 0, 0, max(a - 20, 0))

    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0, offset_y)
    effect.setColor(color)
    widget.setGraphicsEffect(effect)


__all__ = ["apply_subtle_shadow"]

