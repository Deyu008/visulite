"""Reusable Qt widgets."""

from __future__ import annotations

from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure


class MatplotlibCanvas(FigureCanvasQTAgg):
    """Lightweight matplotlib canvas with default figure."""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(5, 4), tight_layout=True)
        super().__init__(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    @property
    def axes(self):
        if not self.figure.axes:
            return self.figure.add_subplot(111)
        return self.figure.axes[0]


class ChartWidget(QWidget):
    """Widget containing a matplotlib canvas with navigation toolbar."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.canvas = MatplotlibCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setObjectName("matplotlib-toolbar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    @property
    def figure(self):
        return self.canvas.figure

    @property
    def axes(self):
        return self.canvas.axes


__all__ = ["MatplotlibCanvas", "ChartWidget"]
