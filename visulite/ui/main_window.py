# -*- coding: utf-8 -*-
"""Qt main window implementation for VisuLite."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QSettings, Qt, QSortFilterProxyModel
from PySide6.QtGui import QAction, QCloseEvent, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from visulite.models.app_state import AppState
from visulite.models.chart_config import ChartConfig
from visulite.models.dataframe_model import DataFrameModel
from visulite.services.batch_plotter import BatchPlotter
from visulite.services.chart_manager import ChartManager
from visulite.services.config_manager import ConfigManager
from visulite.services.data_loader import DataLoader, UnsupportedFormatError
from visulite.services.data_processor import DataProcessor, FilterCriteria
from visulite.services.export_manager import ExportManager
from visulite.services.recent_files import RecentFilesManager
from visulite.ui.styles import QSS_LIGHT, QSS_DARK
from visulite.ui.surfaces import ColorSwatch, SurfaceFrame
from visulite.ui.effects import apply_subtle_shadow
from visulite.ui.widgets import ChartWidget

logger = logging.getLogger("visulite.ui.main_window")


class NumericSortProxy(QSortFilterProxyModel):
    """Proxy model with numeric-aware sorting for pandas data."""

    def __init__(self) -> None:
        super().__init__()
        self._filter_tokens: list[str] = []

    def set_filter_text(self, text: str) -> None:
        normalized = text.strip().lower()
        self._filter_tokens = [token for token in normalized.split() if token]
        # Qt6 deprecates invalidateFilter(); invalidate() is the supported refresh.
        self.invalidate()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:  # type: ignore[override]
        if not self._filter_tokens:
            return True
        model = self.sourceModel()
        if model is None:
            return True
        parts: list[str] = []
        for column in range(model.columnCount(source_parent)):
            index = model.index(source_row, column, source_parent)
            value = model.data(index, Qt.DisplayRole)
            if value is not None:
                parts.append(str(value).lower())
        row_text = " ".join(parts)
        return all(token in row_text for token in self._filter_tokens)

    def lessThan(self, left, right):  # type: ignore[override]
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)

        def to_float(value):
            try:
                return float(str(value))
            except (TypeError, ValueError):
                return None

        l_val = to_float(left_data)
        r_val = to_float(right_data)
        if l_val is not None and r_val is not None:
            return l_val < r_val
        # Fallback to string comparison
        return str(left_data) < str(right_data)


class MainWindow(QMainWindow):
    """Main application window."""

    VERSION = "1.0.0"
    SETTINGS_NAMESPACE = "ui"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"VisuLite v{self.VERSION} - 轻量级数据可视化工具")
        self.resize(1400, 800)

        self.state = AppState()
        self.table_model = DataFrameModel()
        self.proxy_model = NumericSortProxy()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.setDynamicSortFilter(True)
        self.data_loader = DataLoader()
        self.chart_manager = ChartManager()
        self.export_manager = ExportManager()
        self.config_manager = ConfigManager()
        self.data_processor = DataProcessor()
        self.recent_files_manager = RecentFilesManager()
        self.selected_color: str = "auto"
        self.chart_theme: str = "default"  # Chart matplotlib style
        self.settings = QSettings()
        self._sidebar_previous_sizes: list[int] = [450, 830]
        self._content_previous_sizes: list[int] = [3, 2]
        self._chart_focus_mode = False
        self.undo_action: QAction | None = None
        self.redo_action: QAction | None = None
        self._system_backdrop_enabled = False
        self._system_backdrop_initialized = False

        self._build_menu_bar()
        self._build_ui()
        self._setup_shortcuts()
        self._restore_ui_preferences()
        self._update_history_actions()
        
        # Enable drag and drop
        self.setAcceptDrops(True)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if self._system_backdrop_initialized:
            return
        self._system_backdrop_initialized = True
        self._apply_system_backdrop()

    def _apply_system_backdrop(self) -> None:
        """Enable Windows backdrop (Mica/Acrylic) if available; no-op otherwise."""
        if sys.platform != "win32":
            return
        hwnd = int(self.winId())
        dark = bool(getattr(self, "dark_mode_action", None) and self.dark_mode_action.isChecked())
        try:
            from visulite.ui.windows_backdrop import (
                apply_backdrop,
                set_immersive_dark_titlebar,
            )
        except Exception:
            return

        try:
            set_immersive_dark_titlebar(hwnd, dark)
        except Exception:
            pass

        enabled = False
        try:
            acrylic = 0xCC000000 if dark else 0xCCFFFFFF
            enabled = bool(
                apply_backdrop(
                    hwnd,
                    prefer_mica=True,
                    dark_titlebar=False,
                    acrylic_gradient_color=acrylic,
                )
            )
        except Exception:
            enabled = False

        self._system_backdrop_enabled = enabled
        # Drive semi-transparent QSS variants via dynamic property.
        marker = "on" if enabled else "off"
        self.setProperty("backdrop", marker)
        central = self.centralWidget()
        if central is not None:
            central.setProperty("backdrop", marker)
            self._repolish(central)
        self._repolish(self)

    # Menu bar -----------------------------------------------------------------------

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("文件(&F)")
        
        open_action = QAction("打开文件(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        self.recent_menu = QMenu("最近文件(&R)", self)
        file_menu.addMenu(self.recent_menu)
        self._update_recent_files_menu()

        file_menu.addSeparator()

        batch_action = QAction("批量绘图(&B)", self)
        batch_action.triggered.connect(self._on_batch_plot)
        file_menu.addAction(batch_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("编辑(&E)")

        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self._undo_last_change)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcuts(
            [QKeySequence.Redo, QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")]
        )
        self.redo_action.triggered.connect(self._redo_last_change)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()
        
        export_action = QAction("导出图表(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_chart)
        edit_menu.addAction(export_action)

        save_config_action = QAction("保存配置(&S)", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.triggered.connect(self._on_save_config)
        edit_menu.addAction(save_config_action)

        load_config_action = QAction("加载配置(&L)", self)
        load_config_action.triggered.connect(self._on_load_config)
        edit_menu.addAction(load_config_action)

        # View menu
        view_menu = menu_bar.addMenu("视图(&V)")
        
        refresh_action = QAction("刷新图表(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._on_update_chart)
        view_menu.addAction(refresh_action)

        reset_data_action = QAction("重置数据(&D)", self)
        reset_data_action.triggered.connect(self._reset_dataset)
        view_menu.addAction(reset_data_action)

        view_menu.addSeparator()

        toggle_sidebar_action = QAction("显示/隐藏侧栏(&B)", self)
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        focus_chart_action = QAction("图表专注模式(&2)", self)
        focus_chart_action.triggered.connect(self._toggle_chart_focus)
        view_menu.addAction(focus_chart_action)

        restore_layout_action = QAction("恢复默认布局(&1)", self)
        restore_layout_action.triggered.connect(self._restore_balanced_view)
        view_menu.addAction(restore_layout_action)

        view_menu.addSeparator()

        # Chart theme submenu
        theme_menu = QMenu("图表主题(&T)", self)
        self.theme_actions = {}
        for theme_name, theme_label in [
            ("default", "默认"),
            ("seaborn-v0_8-whitegrid", "Seaborn 白格"),
            ("ggplot", "GGPlot"),
            ("bmh", "BMH"),
            ("dark_background", "深色背景"),
            ("fivethirtyeight", "FiveThirtyEight"),
        ]:
            action = QAction(theme_label, self)
            action.setCheckable(True)
            action.setChecked(theme_name == "default")
            action.triggered.connect(lambda checked, t=theme_name: self._set_chart_theme(t))
            self.theme_actions[theme_name] = action
            theme_menu.addAction(action)
        view_menu.addMenu(theme_menu)

        view_menu.addSeparator()

        # UI Theme (Light/Dark mode)
        self.dark_mode_action = QAction("深色模式(&D)", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(False)
        self.dark_mode_action.triggered.connect(self._toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Help menu
        help_menu = menu_bar.addMenu("帮助(&H)")
        
        about_action = QAction("关于 VisuLite(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("快捷键列表(&K)", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _setup_shortcuts(self) -> None:
        """Setup additional keyboard shortcuts."""
        # Update chart with Enter
        QShortcut(QKeySequence(Qt.Key_Return), self, self._on_update_chart)
        # Quick export with Ctrl+Shift+E
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, self._quick_export)
        # Focus global table search
        QShortcut(QKeySequence("Ctrl+F"), self, self._focus_table_search)
        # Toggle sidebar
        QShortcut(QKeySequence("Ctrl+B"), self, self._toggle_sidebar)
        # Switch chart focus
        QShortcut(QKeySequence("Ctrl+2"), self, self._toggle_chart_focus)
        # Restore layout
        QShortcut(QKeySequence("Ctrl+1"), self, self._restore_balanced_view)

    def _set_chart_theme(self, theme: str) -> None:
        """Set the matplotlib chart theme."""
        self.chart_theme = theme
        # Update checkmarks
        for name, action in self.theme_actions.items():
            action.setChecked(name == theme)
        # Refresh chart if data is loaded
        if self.state.has_data():
            self._on_update_chart()
        self.statusBar().showMessage("图表主题已切换")

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "关于 VisuLite",
            f"""<h2>VisuLite v{self.VERSION}</h2>
            <p>轻量级数据可视化与分析工具</p>
            <p><b>功能特性：</b></p>
            <ul>
                <li>支持 CSV、TSV、Excel、JSON 数据文件</li>
                <li>多种图表类型：折线图、柱状图、散点图</li>
                <li>数据预处理：筛选、类型转换、缺失处理</li>
                <li>高质量图表导出 (PNG/JPG/PDF/SVG)</li>
                <li>批量绘图和配置管理</li>
            </ul>
            <p>基于 PySide6 + Matplotlib 构建</p>
            <p>© 2024-2025 VisuLite Team</p>"""
        )

    def _show_shortcuts(self) -> None:
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
        <h3>键盘快捷键</h3>
        <table cellpadding="5">
            <tr><td><b>Ctrl+O</b></td><td>打开文件</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>保存配置</td></tr>
            <tr><td><b>Ctrl+E</b></td><td>导出图表</td></tr>
            <tr><td><b>Ctrl+Z</b></td><td>撤销上一步数据操作</td></tr>
            <tr><td><b>Ctrl+Y / Ctrl+Shift+Z</b></td><td>重做上一步数据操作</td></tr>
            <tr><td><b>Ctrl+Shift+E</b></td><td>快速导出 (PNG)</td></tr>
            <tr><td><b>Ctrl+F</b></td><td>聚焦表格搜索</td></tr>
            <tr><td><b>Ctrl+B</b></td><td>显示/隐藏侧栏</td></tr>
            <tr><td><b>Ctrl+2</b></td><td>图表专注模式</td></tr>
            <tr><td><b>Ctrl+1</b></td><td>恢复默认布局</td></tr>
            <tr><td><b>F5 / Enter</b></td><td>刷新图表</td></tr>
            <tr><td><b>Ctrl+Q</b></td><td>退出程序</td></tr>
            <tr><td><b>F1</b></td><td>显示此帮助</td></tr>
        </table>
        """
        QMessageBox.information(self, "快捷键列表", shortcuts_text)

    def _toggle_dark_mode(self, checked: bool) -> None:
        """Toggle between light and dark mode."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet(QSS_DARK if checked else QSS_LIGHT)
            # Re-apply backdrop attributes on Windows so the titlebar/backdrop matches the theme.
            try:
                self._apply_system_backdrop()
            except Exception:
                pass
            try:
                self.chart_widget.apply_theme(bool(checked))
            except Exception:
                pass
            # Update existing surface shadows (subtle tweak per theme).
            try:
                for frame in self.findChildren(SurfaceFrame):
                    if frame.property("surface") == "card":
                        apply_subtle_shadow(frame, dark=checked)
            except Exception:
                pass
            self.statusBar().showMessage("已切换到" + ("深色模式" if checked else "浅色模式"))

    def _quick_export(self) -> None:
        """Quick export chart as PNG to desktop."""
        if not self.chart_widget.figure.axes:
            self.statusBar().showMessage("请先绘制图表")
            return
        
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = desktop / f"VisuLite_Chart_{timestamp}.png"
        
        try:
            self.export_manager.export(self.chart_widget.figure, target, dpi=300)
            self.statusBar().showMessage(f"已快速导出到桌面: {target.name}")
        except Exception as exc:
            self.statusBar().showMessage(f"导出失败: {exc}")

    def _update_recent_files_menu(self) -> None:
        self.recent_menu.clear()
        recent_files = self.recent_files_manager.get_recent()
        
        if not recent_files:
            no_recent = QAction("(无最近文件)", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
            return

        for file_path in recent_files:
            action = QAction(str(file_path), self)
            action.triggered.connect(lambda checked, p=file_path: self._load_file(p))
            self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()
        clear_action = QAction("清除记录", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_menu.addAction(clear_action)

    def _clear_recent_files(self) -> None:
        self.recent_files_manager.clear()
        self._update_recent_files_menu()
        self._refresh_quick_recent_actions()

    def _refresh_quick_recent_actions(self) -> None:
        while self.quick_recent_layout.count():
            item = self.quick_recent_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        recent_files = self.recent_files_manager.get_recent()[:3]
        if not recent_files:
            placeholder = QLabel("最近文件：无")
            placeholder.setProperty("class", "toolbar-label")
            self.quick_recent_layout.addWidget(placeholder)
            return

        label = QLabel("最近：")
        label.setProperty("class", "toolbar-label")
        self.quick_recent_layout.addWidget(label)

        for file_path in recent_files:
            button = QPushButton(file_path.name)
            button.setProperty("class", "ghost")
            button.setToolTip(str(file_path))
            if not file_path.exists():
                button.setEnabled(False)
                button.setText(f"{file_path.name} (缺失)")
            button.clicked.connect(lambda checked=False, p=file_path: self._load_file(p))
            self.quick_recent_layout.addWidget(button)

    # UI construction -----------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central_widget")  # For QSS targeting
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        command_bar = self._build_command_bar()
        layout.addWidget(command_bar)

        # Main horizontal splitter: sidebar | content area
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(4)
        main_splitter.setOpaqueResize(True)
        main_splitter.setChildrenCollapsible(True)
        self.main_splitter = main_splitter

        # Left sidebar with scroll area
        sidebar_container = SurfaceFrame(surface="panel")
        sidebar_container.setProperty("class", "panel")
        sidebar_container.setProperty("role", "sidebar-panel")
        sidebar_container.setMinimumWidth(280)  # Minimum width to ensure readability
        sidebar_container.setMaximumWidth(450)  # Maximum width to prevent over-expansion
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        self.sidebar_scroll_area = QScrollArea()
        self.sidebar_scroll_area.setWidgetResizable(True)
        self.sidebar_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sidebar_scroll_area.setFrameShape(QFrame.NoFrame)
        # Avoid shrinking the viewport: it can cause visual clipping at narrow widths.
        self.sidebar_scroll_area.setViewportMargins(0, 0, 0, 0)

        control_panel = self._build_control_panel()
        self.sidebar_scroll_area.setWidget(control_panel)
        sidebar_layout.addWidget(self.sidebar_scroll_area, 1)

        self.sidebar_action_dock = self._build_sidebar_action_dock()
        sidebar_layout.addWidget(self.sidebar_action_dock, 0)

        # Right content area (table + chart)
        content_area = self._build_content_area()

        # Add widgets to main splitter
        main_splitter.addWidget(sidebar_container)
        main_splitter.addWidget(content_area)

        # Only valid after widgets are added.
        if main_splitter.count() >= 2:
            main_splitter.setCollapsible(0, True)
            main_splitter.setCollapsible(1, False)

        # Set stretch factors: sidebar gets less, content gets more
        main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        main_splitter.setStretchFactor(1, 1)  # Content area stretches

        # Set initial sizes (sidebar: 450px, content: 830px)
        main_splitter.setSizes([450, 830])
        if main_splitter.count() > 1:
            main_splitter.handle(1).setCursor(Qt.SplitHCursor)

        layout.addWidget(main_splitter)
        self.setCentralWidget(central)
        self.status_hint_label = QLabel("提示: 支持拖拽 CSV/TSV/Excel/JSON 到窗口快速加载")
        self.status_hint_label.setProperty("class", "toolbar-label")
        self.statusBar().addPermanentWidget(self.status_hint_label, 1)
        self.statusBar().showMessage("准备就绪")

    def _build_command_bar(self) -> QFrame:
        bar = SurfaceFrame(surface="glass")
        bar.setObjectName("command-bar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        title = QLabel("VisuLite Studio")
        title.setObjectName("hero-title")
        subtitle = QLabel("数据探索 · 图表制作 · 高质量导出")
        subtitle.setObjectName("hero-subtitle")
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)
        layout.addLayout(brand_layout, 1)

        self.dataset_badge = QLabel("数据集: 未加载")
        self.dataset_badge.setProperty("class", "metric-badge")
        self.dataset_badge.setAttribute(Qt.WA_StyledBackground, True)
        self.dataset_rows_badge = QLabel("行数: -")
        self.dataset_rows_badge.setProperty("class", "metric-badge")
        self.dataset_rows_badge.setAttribute(Qt.WA_StyledBackground, True)
        self.dataset_columns_badge = QLabel("列数: -")
        self.dataset_columns_badge.setProperty("class", "metric-badge")
        self.dataset_columns_badge.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self.dataset_badge)
        layout.addWidget(self.dataset_rows_badge)
        layout.addWidget(self.dataset_columns_badge)

        quick_open = QPushButton("打开数据")
        quick_open.setProperty("class", "primary")
        quick_open.clicked.connect(self._on_open_file)
        layout.addWidget(quick_open)

        quick_update = QPushButton("刷新图表")
        quick_update.clicked.connect(self._on_update_chart)
        layout.addWidget(quick_update)

        quick_export = QPushButton("导出图表")
        quick_export.clicked.connect(self._on_export_chart)
        layout.addWidget(quick_export)

        self.toggle_sidebar_button = QPushButton("隐藏侧栏")
        self.toggle_sidebar_button.setProperty("class", "toolbar-action")
        self.toggle_sidebar_button.clicked.connect(self._toggle_sidebar)
        layout.addWidget(self.toggle_sidebar_button)

        self.focus_chart_button = QPushButton("专注图表")
        self.focus_chart_button.setProperty("class", "toolbar-action")
        self.focus_chart_button.clicked.connect(self._toggle_chart_focus)
        layout.addWidget(self.focus_chart_button)

        self.restore_layout_button = QPushButton("恢复布局")
        self.restore_layout_button.setProperty("class", "ghost")
        self.restore_layout_button.clicked.connect(self._restore_balanced_view)
        layout.addWidget(self.restore_layout_button)

        self.quick_recent_frame = QFrame()
        self.quick_recent_frame.setObjectName("quick-recent-frame")
        quick_recent_layout = QHBoxLayout(self.quick_recent_frame)
        quick_recent_layout.setContentsMargins(0, 0, 0, 0)
        quick_recent_layout.setSpacing(6)
        self.quick_recent_layout = quick_recent_layout
        layout.addWidget(self.quick_recent_frame)

        self._refresh_quick_recent_actions()
        return bar

    def _create_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """Helper to create a consistent card-style container."""
        card = SurfaceFrame(surface="card")
        card.setProperty("class", "card")
        card.setProperty("role", "sidebar-card")
        apply_subtle_shadow(card, dark=self.dark_mode_action.isChecked())
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "card-title")
        card_layout.addWidget(title_label)
        
        return card, card_layout

    def _build_control_panel(self) -> QWidget:
        panel = QWidget()
        # panel.setMinimumWidth(360) # Handled by scroll area width
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        layout.addWidget(self._build_file_group())
        layout.addWidget(self._build_chart_group())
        layout.addWidget(self._build_processing_group())
        layout.addWidget(self._build_stats_group())
        layout.addStretch(1)
        return panel

    def _build_sidebar_action_dock(self) -> QFrame:
        dock = SurfaceFrame(surface="glass")
        dock.setObjectName("sidebar-action-dock")

        dock_layout = QHBoxLayout(dock)
        dock_layout.setContentsMargins(10, 8, 10, 8)
        dock_layout.setSpacing(8)

        self.sidebar_update_button = QPushButton("更新图表")
        self.sidebar_update_button.setProperty("class", "sticky-primary")
        self.sidebar_update_button.clicked.connect(self._on_update_chart)
        dock_layout.addWidget(self.sidebar_update_button, 1)

        self.sidebar_export_button = QPushButton("导出图表")
        self.sidebar_export_button.setProperty("class", "sticky-secondary")
        self.sidebar_export_button.clicked.connect(self._on_export_chart)
        dock_layout.addWidget(self.sidebar_export_button, 1)

        # Keep backward-compatible references used by existing code/tests.
        self.update_chart_button = self.sidebar_update_button
        self.export_button = self.sidebar_export_button
        return dock

    def _configure_form_layout(
        self,
        form_layout: QFormLayout,
        *,
        min_label_width: int,
        wrap_long_rows: bool = True,
    ) -> None:
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setRowWrapPolicy(
            QFormLayout.WrapLongRows if wrap_long_rows else QFormLayout.DontWrapRows
        )

        for i in range(form_layout.rowCount()):
            item = form_layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget() and isinstance(item.widget(), QLabel):
                label = item.widget()
                label.setWordWrap(True)
                label.setMinimumWidth(min_label_width)
                label.setProperty("class", "form-label")

    def _build_file_group(self) -> QFrame:
        card, layout = self._create_card("数据文件")

        self.open_button = QPushButton("打开数据文件")
        self.open_button.setProperty("class", "primary")
        self.open_button.setMinimumHeight(40)
        self.open_button.clicked.connect(self._on_open_file)
        layout.addWidget(self.open_button)

        overview_row = QHBoxLayout()
        overview_row.setSpacing(8)
        self.file_rows_badge = QLabel("行数: -")
        self.file_rows_badge.setProperty("class", "metric-badge")
        self.file_rows_badge.setAttribute(Qt.WA_StyledBackground, True)
        self.file_columns_badge = QLabel("列数: -")
        self.file_columns_badge.setProperty("class", "metric-badge")
        self.file_columns_badge.setAttribute(Qt.WA_StyledBackground, True)
        self.file_missing_badge = QLabel("缺失值: -")
        self.file_missing_badge.setProperty("class", "metric-badge")
        self.file_missing_badge.setAttribute(Qt.WA_StyledBackground, True)
        overview_row.addWidget(self.file_rows_badge)
        overview_row.addWidget(self.file_columns_badge)
        overview_row.addWidget(self.file_missing_badge)
        layout.addLayout(overview_row)

        self.file_info = QTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setPlaceholderText("未加载数据")
        self.file_info.setMinimumHeight(100)
        layout.addWidget(self.file_info)
        return card

    def _build_chart_group(self) -> QFrame:
        card, layout = self._create_card("图表设置")
        
        form_layout = QFormLayout()
        self._configure_form_layout(form_layout, min_label_width=104)

        self.x_combo = QComboBox()
        form_layout.addRow("X 轴列", self.x_combo)

        y_container = QVBoxLayout()
        y_container.setSpacing(4)
        self.y_list = QListWidget()
        self.y_list.setSelectionMode(QListWidget.MultiSelection)
        self.y_list.setMinimumHeight(110)
        y_container.addWidget(self.y_list)
        
        y_button_row = QHBoxLayout()
        y_button_row.setSpacing(6)
        self.select_all_y_button = QPushButton("全选")
        self.select_all_y_button.setFixedHeight(24)
        self.select_all_y_button.clicked.connect(self._select_all_y_columns)
        y_button_row.addWidget(self.select_all_y_button)
        self.deselect_all_y_button = QPushButton("全不选")
        self.deselect_all_y_button.setFixedHeight(24)
        self.deselect_all_y_button.clicked.connect(self._deselect_all_y_columns)
        y_button_row.addWidget(self.deselect_all_y_button)
        y_container.addLayout(y_button_row)
        form_layout.addRow("Y 轴列", y_container)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem("折线图", "line")
        self.chart_type_combo.addItem("柱状图", "bar")
        self.chart_type_combo.addItem("散点图", "scatter")
        self.chart_type_combo.addItem("直方图", "histogram")
        self.chart_type_combo.addItem("箱线图", "boxplot")
        self.chart_type_combo.addItem("热力图", "heatmap")
        self.chart_type_combo.currentIndexChanged.connect(self._on_chart_type_changed)
        form_layout.addRow("图表类型", self.chart_type_combo)

        self.line_style_combo = QComboBox()
        self.line_style_combo.addItem("实线", "-")
        self.line_style_combo.addItem("虚线", "--")
        self.line_style_combo.addItem("点划线", "-.")
        self.line_style_label = QLabel("线型")
        form_layout.addRow(self.line_style_label, self.line_style_combo)

        # Marker style selection
        self.marker_style_combo = QComboBox()
        self.marker_style_combo.addItem("无标记", "")
        self.marker_style_combo.addItem("圆形 (o)", "o")
        self.marker_style_combo.addItem("叉号 (x)", "x")
        self.marker_style_combo.addItem("加号 (+)", "+")
        self.marker_style_combo.addItem("方形 (s)", "s")
        self.marker_style_combo.addItem("三角形(^)", "^")
        self.marker_style_combo.addItem("菱形 (D)", "D")
        self.marker_style_label = QLabel("点样式")
        form_layout.addRow(self.marker_style_label, self.marker_style_combo)

        # Color selection
        color_row = QHBoxLayout()
        self.color_combo = QComboBox()
        self.color_combo.addItem("自动配色", "auto")
        self.color_combo.addItem("自定义颜色...", "custom")
        self.color_combo.currentIndexChanged.connect(self._on_color_changed)
        color_row.addWidget(self.color_combo)
        self.color_preview = ColorSwatch("#1f77b4")
        color_row.addWidget(self.color_preview)
        form_layout.addRow("颜色", color_row)

        self.title_edit = QLineEdit("VisuLite Chart")
        form_layout.addRow("图表标题", self.title_edit)

        # Axis labels
        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("X 轴标题(可空)")
        form_layout.addRow("X 轴标题", self.x_label_edit)

        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("Y 轴标题(可空)")
        form_layout.addRow("Y 轴标题", self.y_label_edit)

        self.legend_checkbox = QCheckBox("显示图例")
        self.legend_checkbox.setChecked(True)
        self.grid_checkbox = QCheckBox("显示网格")
        self.grid_checkbox.setChecked(True)
        form_layout.addRow(self.legend_checkbox, self.grid_checkbox)

        self.fig_width_spin = QDoubleSpinBox()
        self.fig_width_spin.setRange(2.0, 20.0)
        self.fig_width_spin.setValue(6.0)
        self.fig_width_spin.setSuffix(" in")
        self.fig_height_spin = QDoubleSpinBox()
        self.fig_height_spin.setRange(2.0, 20.0)
        self.fig_height_spin.setValue(4.0)
        self.fig_height_spin.setSuffix(" in")
        size_row = QHBoxLayout()
        size_row.addWidget(self.fig_width_spin)
        size_row.addWidget(self.fig_height_spin)
        form_layout.addRow("图表尺寸 (in)", size_row)

        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        form_layout.addRow("导出 DPI", self.dpi_spin)

        # Export naming template
        self.name_template_combo = QComboBox()
        self.name_template_combo.addItem("chart", "chart")
        self.name_template_combo.addItem("{xcol}-{ycol}", "{xcol}-{ycol}")
        self.name_template_combo.addItem("figure-{timestamp}", "figure-{timestamp}")
        self.name_template_combo.setEditable(True)
        form_layout.addRow("导出文件名模板", self.name_template_combo)

        self._configure_form_layout(form_layout, min_label_width=104)
        layout.addLayout(form_layout)

        config_row = QHBoxLayout()
        self.save_config_button = QPushButton("保存配置")
        self.save_config_button.clicked.connect(self._on_save_config)
        config_row.addWidget(self.save_config_button)
        self.load_config_button = QPushButton("加载配置")
        self.load_config_button.clicked.connect(self._on_load_config)
        config_row.addWidget(self.load_config_button)
        layout.addLayout(config_row)
        return card

    def _build_processing_group(self) -> QFrame:
        card, layout = self._create_card("数据预处理")
        
        form_layout = QFormLayout()
        self._configure_form_layout(form_layout, min_label_width=104)

        # Data slicing controls
        slice_controls = QWidget()
        slice_row = QHBoxLayout(slice_controls)
        slice_row.setContentsMargins(0, 0, 0, 0)
        slice_row.setSpacing(6)
        self.head_n_spin = QSpinBox()
        self.head_n_spin.setRange(0, 1000000)
        self.head_n_spin.setValue(0)
        self.head_n_spin.setSpecialValueText("全部")
        slice_row.addWidget(self.head_n_spin)
        self.slice_button = QPushButton("截取")
        self.slice_button.clicked.connect(self._slice_data)
        slice_row.addWidget(self.slice_button)
        slice_row.addStretch(1)
        form_layout.addRow("截取前 N 行", slice_controls)

        # Type conversion
        type_controls = QWidget()
        type_row = QHBoxLayout(type_controls)
        type_row.setContentsMargins(0, 0, 0, 0)
        type_row.setSpacing(6)
        self.convert_column_combo = QComboBox()
        type_row.addWidget(self.convert_column_combo, 1)
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItem("字符串", "string")
        self.target_type_combo.addItem("整数", "int")
        self.target_type_combo.addItem("浮点数", "float")
        self.target_type_combo.addItem("日期时间", "datetime")
        type_row.addWidget(self.target_type_combo, 1)
        self.convert_type_button = QPushButton("转换")
        self.convert_type_button.clicked.connect(self._convert_column_type)
        type_row.addWidget(self.convert_type_button)
        form_layout.addRow("类型转换", type_controls)

        self.filter_column_combo = QComboBox()
        form_layout.addRow("文本筛选列", self.filter_column_combo)
        self.filter_text_input = QLineEdit()
        self.filter_text_input.setPlaceholderText("包含关键词...")
        form_layout.addRow("关键词", self.filter_text_input)

        self.range_column_combo = QComboBox()
        form_layout.addRow("数值列", self.range_column_combo)
        self.range_min_input = QLineEdit()
        self.range_min_input.setPlaceholderText("最小值(可空)")
        self.range_max_input = QLineEdit()
        self.range_max_input.setPlaceholderText("最大值(可空)")
        range_controls = QWidget()
        range_row = QHBoxLayout(range_controls)
        range_row.setContentsMargins(0, 0, 0, 0)
        range_row.setSpacing(6)
        range_row.addWidget(self.range_min_input)
        range_row.addWidget(self.range_max_input)
        form_layout.addRow("数值范围", range_controls)

        self.dropna_column_combo = QComboBox()
        self.dropna_column_combo.addItem("不处理")
        form_layout.addRow("缺失值删除列", self.dropna_column_combo)

        self.fill_method_combo = QComboBox()
        self.fill_method_combo.addItem("均值填充", "mean")
        self.fill_method_combo.addItem("中位数填充", "median")
        self.fill_method_combo.addItem("0 填充", "zero")
        self.fill_method_combo.addItem("前向填充", "ffill")
        self.fill_method_combo.addItem("后向填充", "bfill")
        form_layout.addRow("缺失值填充策略", self.fill_method_combo)

        self._configure_form_layout(form_layout, min_label_width=104)
        layout.addLayout(form_layout)

        action_row = QHBoxLayout()
        self.apply_filter_button = QPushButton("应用筛选")
        self.apply_filter_button.clicked.connect(self._apply_filters)
        action_row.addWidget(self.apply_filter_button)
        self.reset_data_button = QPushButton("重置数据")
        self.reset_data_button.clicked.connect(self._reset_dataset)
        action_row.addWidget(self.reset_data_button)
        layout.addLayout(action_row)

        fill_row = QHBoxLayout()
        self.fill_missing_button = QPushButton("执行填充")
        self.fill_missing_button.clicked.connect(self._fill_missing)
        fill_row.addWidget(self.fill_missing_button)
        layout.addLayout(fill_row)
        return card

    def _build_stats_group(self) -> QFrame:
        card, layout = self._create_card("数据统计")
        
        # Stats info label
        self.stats_info_label = QLabel("加载数据后显示统计信息")
        self.stats_info_label.setProperty("class", "caption")
        self.stats_info_label.setProperty("tone", "muted")
        layout.addWidget(self.stats_info_label)
        
        # Stats table
        self.stats_table = QTableWidget()
        self.stats_table.setMinimumHeight(220)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stats_table.setSelectionMode(QTableWidget.SingleSelection)
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.horizontalHeader().setHighlightSections(False)
        self.stats_table.horizontalHeader().setFixedHeight(36)
        self.stats_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        self.stats_table.verticalHeader().setDefaultSectionSize(34)
        self.stats_table.verticalHeader().setMinimumSectionSize(28)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.setProperty("class", "table-stats")

        table_shell = SurfaceFrame(surface="panel")
        table_shell.setProperty("class", "panel")
        table_shell.setProperty("role", "stats-shell")
        table_shell_layout = QVBoxLayout(table_shell)
        table_shell_layout.setContentsMargins(8, 8, 8, 8)
        table_shell_layout.setSpacing(0)
        table_shell_layout.addWidget(self.stats_table)
        layout.addWidget(table_shell)
        return card

    @staticmethod
    def _repolish(widget: QWidget) -> None:
        """Force re-application of QSS after dynamic property changes."""
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()
    def _build_content_area(self) -> QWidget:
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        toolbar = SurfaceFrame(surface="glass")
        toolbar.setObjectName("content-toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(10)

        search_label = QLabel("全局搜索")
        search_label.setProperty("class", "toolbar-label")
        toolbar_layout.addWidget(search_label)

        self.table_search_input = QLineEdit()
        self.table_search_input.setProperty("class", "table-search")
        self.table_search_input.setPlaceholderText("输入关键词过滤表格（支持多关键词）")
        self.table_search_input.textChanged.connect(self._on_table_search_changed)
        toolbar_layout.addWidget(self.table_search_input, 1)

        self.table_search_clear_button = QPushButton("清除")
        self.table_search_clear_button.setProperty("class", "ghost")
        self.table_search_clear_button.clicked.connect(
            lambda: self.table_search_input.setText("")
        )
        toolbar_layout.addWidget(self.table_search_clear_button)

        self.table_result_badge = QLabel("显示: 0 / 0")
        self.table_result_badge.setProperty("class", "metric-badge")
        self.table_result_badge.setAttribute(Qt.WA_StyledBackground, True)
        toolbar_layout.addWidget(self.table_result_badge)
        content_layout.addWidget(toolbar)

        panel = SurfaceFrame(surface="panel")
        panel.setProperty("class", "panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(10)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(4)
        splitter.setOpaqueResize(True)
        self.content_splitter = splitter

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setHighlightSections(False)
        self.table_view.horizontalHeader().setFixedHeight(36)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setAlternatingRowColors(True)  # Better readability
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.verticalHeader().setDefaultSectionSize(34)
        self.table_view.verticalHeader().setMinimumSectionSize(28)
        self.table_view.verticalHeader().setVisible(True)  # Show row numbers

        self.chart_widget = ChartWidget()
        splitter.addWidget(self.table_view)
        splitter.addWidget(self.chart_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        if splitter.count() > 1:
            splitter.handle(1).setCursor(Qt.SplitVCursor)
        panel_layout.addWidget(splitter)
        content_layout.addWidget(panel)
        return content

    # Drag and drop support -----------------------------------------------------------

    def dragEnterEvent(self, event) -> None:
        """Accept drag events for supported file types."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() in self.data_loader.SUPPORTED_EXTENSIONS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event) -> None:
        """Handle dropped files."""
        for url in event.mimeData().urls():
            file_path = Path(url.toLocalFile())
            if file_path.suffix.lower() in self.data_loader.SUPPORTED_EXTENSIONS:
                self._load_file(file_path)
                break  # Only load the first valid file

    # Event handlers ------------------------------------------------------------------

    def _on_chart_type_changed(self, index: int) -> None:
        """Show/hide controls based on chart type."""
        chart_type = self.chart_type_combo.currentData()
        
        # Line style is only relevant for line charts
        line_relevant = chart_type == "line"
        self.line_style_combo.setVisible(line_relevant)
        self.line_style_label.setVisible(line_relevant)
        
        # Marker style is relevant for line and scatter charts
        marker_relevant = chart_type in {"line", "scatter"}
        self.marker_style_combo.setVisible(marker_relevant)
        self.marker_style_label.setVisible(marker_relevant)

    def _select_all_y_columns(self) -> None:
        """Select all items in Y column list."""
        for i in range(self.y_list.count()):
            self.y_list.item(i).setSelected(True)

    def _deselect_all_y_columns(self) -> None:
        """Deselect all items in Y column list."""
        for i in range(self.y_list.count()):
            self.y_list.item(i).setSelected(False)

    def _on_color_changed(self, index: int) -> None:
        if self.color_combo.currentData() == "custom":
            color = QColorDialog.getColor(QColor(self.selected_color if self.selected_color != "auto" else "#1f77b4"), self, "选择颜色")
            if color.isValid():
                self.selected_color = color.name()
                self.color_preview.set_color(self.selected_color)
            else:
                self.color_combo.setCurrentIndex(0)
        else:
            self.selected_color = "auto"
            self.color_preview.set_color("#1f77b4")

    def _focus_table_search(self) -> None:
        self.table_search_input.setFocus()
        self.table_search_input.selectAll()

    def _on_table_search_changed(self, text: str) -> None:
        self.proxy_model.set_filter_text(text)
        self._update_table_result_badge()

    def _apply_data_mutation(self, frame: pd.DataFrame, success_message: str) -> None:
        """Apply a dataframe mutation with undo/redo tracking."""
        current = self.state.data_frame
        if current is None:
            return
        if frame.equals(current):
            self.statusBar().showMessage("数据未发生变化")
            return
        self.state.push_history(current)
        self.state.update_view(frame)
        if self.state.data_frame is None:
            return
        self.table_model.update_frame(self.state.data_frame)
        self._refresh_stats()
        self._update_history_actions()
        self.statusBar().showMessage(success_message)

    def _undo_last_change(self) -> None:
        frame = self.state.undo()
        if frame is None:
            self.statusBar().showMessage("无可撤销的数据操作")
            self._update_history_actions()
            return
        self.table_model.update_frame(frame)
        self._refresh_stats()
        self._update_history_actions()
        self.statusBar().showMessage("已撤销上一步数据操作")

    def _redo_last_change(self) -> None:
        frame = self.state.redo()
        if frame is None:
            self.statusBar().showMessage("无可重做的数据操作")
            self._update_history_actions()
            return
        self.table_model.update_frame(frame)
        self._refresh_stats()
        self._update_history_actions()
        self.statusBar().showMessage("已重做上一步数据操作")

    def _update_history_actions(self) -> None:
        if self.undo_action is not None:
            self.undo_action.setEnabled(self.state.can_undo())
        if self.redo_action is not None:
            self.redo_action.setEnabled(self.state.can_redo())

    def _toggle_sidebar(self) -> None:
        left, right = self.main_splitter.sizes()
        if left <= 20:
            restored = self._sidebar_previous_sizes[:]
            if len(restored) != 2 or restored[0] <= 20:
                restored = [420, max(right, 900)]
            self.main_splitter.setSizes(restored)
            self.toggle_sidebar_button.setText("隐藏侧栏")
            self.statusBar().showMessage("已显示侧栏")
            return

        self._sidebar_previous_sizes = [left, right]
        self.main_splitter.setSizes([0, left + right])
        self.toggle_sidebar_button.setText("显示侧栏")
        self.statusBar().showMessage("已隐藏侧栏")

    def _toggle_chart_focus(self) -> None:
        table_size, chart_size = self.content_splitter.sizes()
        if not self._chart_focus_mode:
            self._content_previous_sizes = [table_size, chart_size]
            self.content_splitter.setSizes([0, max(chart_size, 1)])
            self.focus_chart_button.setText("退出专注")
            self._chart_focus_mode = True
            self.statusBar().showMessage("已进入图表专注模式")
            return

        restored = self._content_previous_sizes[:]
        if len(restored) != 2 or restored[0] <= 0:
            restored = [3, 2]
        self.content_splitter.setSizes(restored)
        self.focus_chart_button.setText("专注图表")
        self._chart_focus_mode = False
        self.statusBar().showMessage("已退出图表专注模式")

    def _restore_balanced_view(self) -> None:
        self.main_splitter.setSizes([450, 830])
        self.content_splitter.setSizes([3, 2])
        self.toggle_sidebar_button.setText("隐藏侧栏")
        self.focus_chart_button.setText("专注图表")
        self._chart_focus_mode = False
        self.statusBar().showMessage("布局已恢复")

    def _on_open_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            "",
            "Data Files (*.csv *.tsv *.xlsx *.xls *.json)",
        )
        if not file_name:
            return
        self._load_file(Path(file_name))

    def _load_file(self, file_path: Path) -> None:
        if not file_path.exists():
            QMessageBox.warning(self, "文件不存在", f"找不到文件\n{file_path}")
            self._update_recent_files_menu()
            self._refresh_quick_recent_actions()
            return
        try:
            frame, meta = self.data_loader.load(file_path)
        except UnsupportedFormatError as exc:
            QMessageBox.warning(self, "格式不支持", str(exc))
            return
        except Exception as exc:  # pragma: no cover - GUI feedback
            logger.exception("Failed to load file")
            QMessageBox.critical(self, "加载失败", str(exc))
            return

        self.state.set_dataset(frame, meta)
        self.table_model.update_frame(frame)
        self.table_search_input.setText("")
        self._update_file_info(meta)
        self._populate_columns(frame.columns.tolist())
        self._refresh_stats()
        self._update_history_actions()
        
        # Update recent files
        self.recent_files_manager.add_file(file_path)
        self._update_recent_files_menu()
        self._refresh_quick_recent_actions()
        
        # Update window title with filename
        self.setWindowTitle(f"VisuLite v{self.VERSION} - {meta.path.name}")
        
        self.statusBar().showMessage(
            f"已加载 {meta.path.name} ({meta.rows:,} 行 × {meta.columns} 列)"
        )

    def _on_update_chart(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件")
            return
        config = self._collect_chart_config()
        self.state.chart_config = config
        try:
            self.chart_manager.plot(
                self.chart_widget.axes, 
                self.state.data_frame, 
                config,
                theme=self.chart_theme
            )  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover - GUI feedback
            QMessageBox.warning(self, "绘图失败", str(exc))
            logger.exception("Chart rendering error")
        else:
            self.statusBar().showMessage("图表已更新")

    def _on_export_chart(self) -> None:
        if not self.chart_widget.figure.axes:
            QMessageBox.information(self, "提示", "请先绘制图表")
            return
        
        # Generate default filename from template
        default_name = self._generate_export_filename()
        
        target, _ = QFileDialog.getSaveFileName(
            self,
            "导出图表",
            default_name,
            "Images (*.png *.jpg *.svg *.pdf)",
        )
        if not target:
            return
        figure = self.chart_widget.figure
        original_size = figure.get_size_inches()
        figure.set_size_inches(
            self.fig_width_spin.value(), self.fig_height_spin.value(), forward=True
        )
        try:
            self.export_manager.export(
                figure, Path(target), dpi=self.dpi_spin.value()
            )
            self._show_export_success(Path(target))
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "导出失败", str(exc))
        finally:
            figure.set_size_inches(*original_size, forward=True)

    def _show_export_success(self, file_path: Path) -> None:
        """Show export success dialog with options to open file or folder."""
        msg = QMessageBox(self)
        msg.setWindowTitle("导出成功")
        msg.setText(f"图表已成功导出到:\n{file_path}")
        msg.setIcon(QMessageBox.Information)
        
        open_file_btn = msg.addButton("打开文件", QMessageBox.ActionRole)
        open_folder_btn = msg.addButton("打开文件夹", QMessageBox.ActionRole)
        msg.addButton("关闭", QMessageBox.RejectRole)
        
        msg.exec()
        
        clicked = msg.clickedButton()
        if clicked == open_file_btn:
            self._open_file_in_system(file_path)
        elif clicked == open_folder_btn:
            self._open_folder_in_explorer(file_path.parent)
        
        self.statusBar().showMessage(f"已导出到 {file_path}")

    def _open_file_in_system(self, file_path: Path) -> None:
        """Open file with default system application."""
        try:
            os.startfile(str(file_path))
        except Exception as exc:
            logger.warning("Failed to open file: %s", exc)

    def _open_folder_in_explorer(self, folder_path: Path) -> None:
        """Open folder in system file explorer."""
        try:
            subprocess.run(["explorer", str(folder_path)], check=False)
        except Exception as exc:
            logger.warning("Failed to open folder: %s", exc)

    def _generate_export_filename(self) -> str:
        """Generate filename based on the template."""
        template = self.name_template_combo.currentText()
        x_col = self.x_combo.currentText() or "x"
        y_cols = [item.text() for item in self.y_list.selectedItems()]
        y_col = y_cols[0] if y_cols else "y"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = template.replace("{xcol}", x_col).replace("{ycol}", y_col).replace("{timestamp}", timestamp)
        if not filename.endswith((".png", ".jpg", ".svg", ".pdf")):
            filename += ".png"
        return filename

    def _on_batch_plot(self) -> None:
        """Open batch plotting dialog."""
        dialog = BatchPlotDialog(self, self.state.chart_config)
        if dialog.exec() == QDialog.Accepted:
            source_dir, target_dir, config, fig_size, dpi, fmt = dialog.get_settings()
            batch_plotter = BatchPlotter(self.data_loader, self.chart_manager, self.export_manager)
            try:
                exported = batch_plotter.run(
                    source_dir, target_dir, config, fig_size, dpi, fmt, 
                    theme=self.chart_theme
                )
                QMessageBox.information(self, "完成", f"成功导出 {len(exported)} 个图表到 {target_dir}")
            except Exception as exc:
                QMessageBox.critical(self, "批量绘图失败", str(exc))

    def _on_save_config(self) -> None:
        config = self._collect_chart_config()
        path = self.config_manager.save_chart_config(config)
        self.statusBar().showMessage(f"配置已保存到 {path}")

    def _on_load_config(self) -> None:
        config = self.config_manager.load_chart_config()
        if not config:
            QMessageBox.information(self, "提示", "暂未保存配置")
            return
        self._apply_chart_config(config)
        self.statusBar().showMessage("配置已加载")

    # Helpers ------------------------------------------------------------------------

    def _update_file_info(self, meta) -> None:
        info_lines = [
            f"文件: {meta.path}",
            f"行数: {meta.rows}",
            f"列数: {meta.columns}",
            "列类型:",
            *meta.column_types,
        ]
        if meta.missing_summary:
            info_lines.append("缺失值:")
            info_lines.extend(meta.missing_summary)
        self.file_info.setPlainText("\n".join(info_lines))
        self._update_dataset_badges(meta)

    def _update_dataset_badges(self, meta=None) -> None:
        """Refresh KPI badges for current dataset and current view."""
        frame = self.state.data_frame
        if meta is None:
            meta = self.state.dataset_meta

        if frame is None:
            self.dataset_badge.setText("数据集: 未加载")
            self.dataset_rows_badge.setText("行数: -")
            self.dataset_columns_badge.setText("列数: -")
            self.file_rows_badge.setText("行数: -")
            self.file_columns_badge.setText("列数: -")
            self.file_missing_badge.setText("缺失值: -")
            return

        dataset_name = meta.path.name if getattr(meta, "path", None) else "当前数据"
        missing_count = int(frame.isna().sum().sum())
        self.dataset_badge.setText(f"数据集: {dataset_name}")
        self.dataset_rows_badge.setText(f"行数: {len(frame):,}")
        self.dataset_columns_badge.setText(f"列数: {len(frame.columns)}")
        self.file_rows_badge.setText(f"行数: {len(frame):,}")
        self.file_columns_badge.setText(f"列数: {len(frame.columns)}")
        self.file_missing_badge.setText(f"缺失值: {missing_count:,}")

    def _update_table_result_badge(self) -> None:
        total = self.table_model.rowCount()
        shown = self.proxy_model.rowCount()
        if total == 0:
            self.table_result_badge.setText("显示: 0 / 0")
            return
        self.table_result_badge.setText(f"显示: {shown:,} / {total:,}")

    def _restore_ui_preferences(self) -> None:
        self.settings.beginGroup(self.SETTINGS_NAMESPACE)
        sidebar_sizes = self.settings.value("main_splitter_sizes")
        content_sizes = self.settings.value("content_splitter_sizes")
        chart_focus = self.settings.value("chart_focus", False, bool)
        dark_mode = self.settings.value("dark_mode", False, bool)
        self.settings.endGroup()

        if isinstance(sidebar_sizes, list) and len(sidebar_sizes) == 2:
            self.main_splitter.setSizes([int(v) for v in sidebar_sizes])
        if isinstance(content_sizes, list) and len(content_sizes) == 2:
            self.content_splitter.setSizes([int(v) for v in content_sizes])
        if dark_mode != self.dark_mode_action.isChecked():
            self.dark_mode_action.setChecked(bool(dark_mode))
            self._toggle_dark_mode(bool(dark_mode))
        if chart_focus:
            self._toggle_chart_focus()

    def _save_ui_preferences(self) -> None:
        self.settings.beginGroup(self.SETTINGS_NAMESPACE)
        self.settings.setValue("main_splitter_sizes", self.main_splitter.sizes())
        self.settings.setValue("content_splitter_sizes", self.content_splitter.sizes())
        self.settings.setValue("chart_focus", self._chart_focus_mode)
        self.settings.setValue("dark_mode", self.dark_mode_action.isChecked())
        self.settings.endGroup()

    def _populate_columns(self, columns: list[str]) -> None:
        self.x_combo.clear()
        self.x_combo.addItems(columns)
        self.y_list.clear()
        for column in columns:
            item = QListWidgetItem(column)
            item.setSelected(False)
            self.y_list.addItem(item)
        self.filter_column_combo.clear()
        self.filter_column_combo.addItems(columns)
        self.range_column_combo.clear()
        self.range_column_combo.addItems(columns)
        self.dropna_column_combo.clear()
        self.dropna_column_combo.addItem("不处理")
        self.dropna_column_combo.addItems(columns)
        self.convert_column_combo.clear()
        self.convert_column_combo.addItems(columns)

    def _collect_chart_config(self) -> ChartConfig:
        y_columns = [item.text() for item in self.y_list.selectedItems()]
        return ChartConfig(
            x_column=self.x_combo.currentText() or None,
            y_columns=y_columns,
            chart_type=self.chart_type_combo.currentData(),
            show_legend=self.legend_checkbox.isChecked(),
            show_grid=self.grid_checkbox.isChecked(),
            title=self.title_edit.text() or "VisuLite Chart",
            line_style=self.line_style_combo.currentData(),
            marker_style=self.marker_style_combo.currentData(),
            color_scheme=self.selected_color,
            x_label=self.x_label_edit.text() or None,
            y_label=self.y_label_edit.text() or None,
        )

    def _apply_chart_config(self, config: ChartConfig) -> None:
        idx = self.x_combo.findText(config.x_column or "")
        if idx >= 0:
            self.x_combo.setCurrentIndex(idx)
        for i in range(self.y_list.count()):
            item = self.y_list.item(i)
            item.setSelected(item.text() in config.y_columns)
        idx = self.chart_type_combo.findData(config.chart_type)
        if idx >= 0:
            self.chart_type_combo.setCurrentIndex(idx)
        idx = self.line_style_combo.findData(config.line_style)
        if idx >= 0:
            self.line_style_combo.setCurrentIndex(idx)
        idx = self.marker_style_combo.findData(config.marker_style)
        if idx >= 0:
            self.marker_style_combo.setCurrentIndex(idx)
        self.legend_checkbox.setChecked(config.show_legend)
        self.grid_checkbox.setChecked(config.show_grid)
        self.title_edit.setText(config.title)
        self.x_label_edit.setText(config.x_label or "")
        self.y_label_edit.setText(config.y_label or "")
        
        # Color scheme
        if config.color_scheme and config.color_scheme != "auto":
            self.selected_color = config.color_scheme
            self.color_combo.setCurrentIndex(1)  # custom
            self.color_preview.set_color(config.color_scheme)
        else:
            self.selected_color = "auto"
            self.color_combo.setCurrentIndex(0)
            self.color_preview.set_color("#1f77b4")

    def _slice_data(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件")
            return
        head_n = self.head_n_spin.value()
        if head_n == 0:
            return
        frame = self.state.data_frame
        if frame is None:
            return
        sliced = self.data_processor.slice_rows(frame, head_n=head_n)
        self._apply_data_mutation(sliced, f"已截取前 {head_n} 行")

    def _convert_column_type(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件")
            return
        column = self.convert_column_combo.currentText()
        target_type = self.target_type_combo.currentData()
        if not column:
            return
        frame = self.state.data_frame
        if frame is None:
            return
        try:
            converted = self.data_processor.convert_column_type(frame, column, target_type)
            self._apply_data_mutation(converted, f"已将列 '{column}' 转换为 {target_type}")
        except Exception as exc:
            QMessageBox.warning(self, "类型转换失败", str(exc))

    def _apply_filters(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件")
            return
        text_filters = None
        column = self.filter_column_combo.currentText()
        keyword = self.filter_text_input.text().strip()
        if column and keyword:
            text_filters = {column: keyword}

        numeric_ranges = None
        range_column = self.range_column_combo.currentText()
        min_value = self._parse_float(self.range_min_input.text())
        max_value = self._parse_float(self.range_max_input.text())
        if range_column and (min_value is not None or max_value is not None):
            numeric_ranges = {range_column: (min_value, max_value)}

        drop_column = self.dropna_column_combo.currentText()
        dropna_columns = None
        if drop_column and drop_column != "不处理":
            dropna_columns = [drop_column]

        criteria = FilterCriteria(
            text_filters=text_filters,
            numeric_ranges=numeric_ranges,
            dropna_columns=dropna_columns,
        )
        frame = self.state.data_frame
        if frame is None:
            return
        filtered = self.data_processor.apply_filters(frame, criteria)
        self._apply_data_mutation(filtered, "已应用筛选条件")

    def _reset_dataset(self) -> None:
        original = self.state.original_frame
        if original is None:
            return
        self._apply_data_mutation(original.copy(deep=True), "已恢复原始数据")

    def _fill_missing(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件")
            return
        frame = self.state.data_frame
        if frame is None:
            return
        method = self.fill_method_combo.currentData()
        filled = self.data_processor.fill_missing(frame.copy(), method)
        self._apply_data_mutation(filled, "缺失值已处理")

    def _refresh_stats(self) -> None:
        if self.state.data_frame is None:
            self.stats_table.setRowCount(0)
            self.stats_table.setColumnCount(0)
            self.stats_info_label.setText("加载数据后显示统计信息")
            self.stats_info_label.setProperty("tone", "muted")
            self._repolish(self.stats_info_label)
            self._update_dataset_badges()
            self._update_table_result_badge()
            self._update_history_actions()
            return
        frame = self.state.data_frame
        if frame is None or frame.empty:
            self.stats_table.setRowCount(0)
            self.stats_table.setColumnCount(0)
            self.stats_info_label.setText("数据为空")
            self.stats_info_label.setProperty("tone", "muted")
            self._repolish(self.stats_info_label)
            self._update_dataset_badges()
            self._update_table_result_badge()
            self._update_history_actions()
            return
        try:
            self._populate_stats_table(frame)
            num_cols = len(frame.columns)
            numeric_cols = len(frame.select_dtypes(include=['number']).columns)
            self.stats_info_label.setText(
                f"行数 {len(frame)} × {num_cols} | 数值列: {numeric_cols}"
            )
            self.stats_info_label.setProperty("tone", "info")
            self._repolish(self.stats_info_label)
            self._update_dataset_badges()
            self._update_table_result_badge()
            self._update_history_actions()
        except Exception as exc:
            logger.exception("Failed to generate stats")
            self.stats_info_label.setText(f"统计信息生成失败: {exc}")
            self.stats_info_label.setProperty("tone", "danger")
            self._repolish(self.stats_info_label)
            self._update_history_actions()

    def _populate_stats_table(self, frame: pd.DataFrame) -> None:
        """Populate the stats table with descriptive statistics."""
        # Column name translations
        header_map = {
            "column": "列名",
            "count": "计数",
            "mean": "平均值",
            "std": "标准差",
            "min": "最小值",
            "25%": "25%分位",
            "50%": "中位数",
            "75%": "75%分位",
            "max": "最大值",
        }
        
        numeric_frame = frame.select_dtypes(include=['number'])
        
        if numeric_frame.empty:
            # Show basic info for non-numeric data
            self.stats_table.setColumnCount(3)
            self.stats_table.setHorizontalHeaderLabels(["列名", "数据类型", "非空值数"])
            self.stats_table.setRowCount(len(frame.columns))
            
            for row, col in enumerate(frame.columns):
                dtype = str(frame[col].dtype)
                non_null = frame[col].count()
                self.stats_table.setItem(row, 0, QTableWidgetItem(col))
                self.stats_table.setItem(row, 1, QTableWidgetItem(dtype))
                self.stats_table.setItem(row, 2, QTableWidgetItem(str(non_null)))
            
            self.stats_table.resizeColumnsToContents()
            return
        
        # Get descriptive statistics
        desc = numeric_frame.describe().transpose()
        col_order = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
        available = [c for c in col_order if c in desc.columns]
        desc = desc[available].reset_index().rename(columns={"index": "column"})
        
        # Setup table
        self.stats_table.setColumnCount(len(desc.columns))
        self.stats_table.setRowCount(len(desc))
        
        # Set headers with Chinese names
        headers = [header_map.get(c, c) for c in desc.columns]
        self.stats_table.setHorizontalHeaderLabels(headers)
        
        # Format function
        def fmt(val):
            if pd.isna(val):
                return "-"
            if isinstance(val, float):
                if abs(val) >= 1000:
                    return f"{val:,.2f}"
                elif abs(val) < 0.01 and val != 0:
                    return f"{val:.4e}"
                else:
                    return f"{val:.4g}"
            if isinstance(val, int):
                return f"{val:,}"
            return str(val)
        
        # Populate table
        for row_idx in range(len(desc)):
            for col_idx, col_name in enumerate(desc.columns):
                val = desc.iloc[row_idx, col_idx]
                item = QTableWidgetItem(fmt(val))
                
                # Center align numeric values, left align column names
                if col_name == "column":
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                self.stats_table.setItem(row_idx, col_idx, item)
        
        self.stats_table.resizeColumnsToContents()

    @staticmethod
    def _parse_float(text: str) -> float | None:
        value = text.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._save_ui_preferences()
        super().closeEvent(event)


class BatchPlotDialog(QDialog):
    """Dialog for batch plotting settings."""

    def __init__(self, parent: QWidget, current_config: ChartConfig) -> None:
        super().__init__(parent)
        self.setWindowTitle("批量绘图设置")
        self.setMinimumWidth(500)
        self.config = current_config
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QFormLayout(self)

        # Source directory
        source_row = QHBoxLayout()
        self.source_dir_edit = QLineEdit()
        self.source_dir_edit.setReadOnly(True)
        source_row.addWidget(self.source_dir_edit)
        self.browse_source_button = QPushButton("浏览...")
        self.browse_source_button.clicked.connect(self._browse_source)
        source_row.addWidget(self.browse_source_button)
        layout.addRow("源文件夹", source_row)

        # Target directory
        target_row = QHBoxLayout()
        self.target_dir_edit = QLineEdit()
        self.target_dir_edit.setReadOnly(True)
        target_row.addWidget(self.target_dir_edit)
        self.browse_target_button = QPushButton("浏览...")
        self.browse_target_button.clicked.connect(self._browse_target)
        target_row.addWidget(self.browse_target_button)
        layout.addRow("输出文件夹", target_row)

        # X column
        self.x_column_edit = QLineEdit(self.config.x_column or "")
        layout.addRow("X 轴列", self.x_column_edit)

        # Y columns
        self.y_columns_edit = QLineEdit(", ".join(self.config.y_columns))
        layout.addRow("Y 轴列(逗号分隔)", self.y_columns_edit)

        # Chart type
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem("折线图", "line")
        self.chart_type_combo.addItem("柱状图", "bar")
        self.chart_type_combo.addItem("散点图", "scatter")
        idx = self.chart_type_combo.findData(self.config.chart_type)
        if idx >= 0:
            self.chart_type_combo.setCurrentIndex(idx)
        layout.addRow("图表类型", self.chart_type_combo)

        # Figure size
        size_row = QHBoxLayout()
        self.fig_width_spin = QDoubleSpinBox()
        self.fig_width_spin.setRange(2.0, 20.0)
        self.fig_width_spin.setValue(6.0)
        self.fig_width_spin.setSuffix(" in")
        size_row.addWidget(self.fig_width_spin)
        self.fig_height_spin = QDoubleSpinBox()
        self.fig_height_spin.setRange(2.0, 20.0)
        self.fig_height_spin.setValue(4.0)
        self.fig_height_spin.setSuffix(" in")
        size_row.addWidget(self.fig_height_spin)
        layout.addRow("图表尺寸", size_row)

        # DPI
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        layout.addRow("DPI", self.dpi_spin)

        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItem("PNG", "png")
        self.format_combo.addItem("JPG", "jpg")
        self.format_combo.addItem("PDF", "pdf")
        self.format_combo.addItem("SVG", "svg")
        layout.addRow("导出格式", self.format_combo)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def _browse_source(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if directory:
            self.source_dir_edit.setText(directory)

    def _browse_target(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if directory:
            self.target_dir_edit.setText(directory)

    def get_settings(self) -> tuple:
        source_dir = Path(self.source_dir_edit.text())
        target_dir = Path(self.target_dir_edit.text())
        
        y_columns = [col.strip() for col in self.y_columns_edit.text().split(",") if col.strip()]
        config = ChartConfig(
            x_column=self.x_column_edit.text() or None,
            y_columns=y_columns,
            chart_type=self.chart_type_combo.currentData(),
            show_legend=self.config.show_legend,
            show_grid=self.config.show_grid,
            title=self.config.title,
            line_style=self.config.line_style,
            marker_style=self.config.marker_style,
            color_scheme=self.config.color_scheme,
        )
        fig_size = (self.fig_width_spin.value(), self.fig_height_spin.value())
        dpi = self.dpi_spin.value()
        fmt = self.format_combo.currentData()
        
        return source_dir, target_dir, config, fig_size, dpi, fmt


__all__ = ["MainWindow", "BatchPlotDialog"]