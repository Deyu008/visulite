"""Reusable Qt widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt
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


class LocalizedNavigationToolbar(NavigationToolbar2QT):
    """Navigation toolbar with Chinese tooltips."""

    toolitems = (
        ("Home", "重置视图", "home", "home"),
        ("Back", "后退", "back", "back"),
        ("Forward", "前进", "forward", "forward"),
        ("Pan", "平移查看", "move", "pan"),
        ("Zoom", "框选缩放", "zoom_to_rect", "zoom"),
        ("Subplots", "子图/边距调整", "subplots", "configure_subplots"),
        ("Customize", "自定义参数", "qt4_editor_options", "edit_parameters"),
        ("Save", "保存图像", "filesave", "save_figure"),
    )

    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)


class ChartWidget(QWidget):
    """Widget containing a matplotlib canvas with navigation toolbar."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.canvas = MatplotlibCanvas()
        self.toolbar = LocalizedNavigationToolbar(self.canvas, self)
        self.toolbar.setObjectName("matplotlib-toolbar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Show welcome message
        self._show_welcome()

    def _show_welcome(self) -> None:
        """Display welcome message on empty chart."""
        ax = self.canvas.axes
        ax.set_facecolor('#f8f9fa')
        ax.text(
            0.5, 0.5,
            "欢迎使用 VisuLite\n\n"
            "1. 点击「打开数据文件」或拖放文件到窗口\n"
            "2. 选择 X 轴和 Y 轴列\n"
            "3. 点击「更新图表」生成可视化\n\n"
            "支持格式: CSV, TSV, Excel, JSON",
            ha='center', va='center',
            fontsize=12, color='#666666',
            transform=ax.transAxes,
            fontfamily='Microsoft YaHei'
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw_idle()

    @property
    def figure(self):
        return self.canvas.figure

    @property
    def axes(self):
        return self.canvas.axes


__all__ = ["MatplotlibCanvas", "ChartWidget"]
