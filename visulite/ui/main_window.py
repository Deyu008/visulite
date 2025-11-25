"""Qt main window implementation for VisuLite."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QAction, QColor
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
from visulite.ui.widgets import ChartWidget

logger = logging.getLogger("visulite.ui.main_window")


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VisuLite - Data Visualization Tool")
        self.resize(1280, 720)

        self.state = AppState()
        self.table_model = DataFrameModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.data_loader = DataLoader()
        self.chart_manager = ChartManager()
        self.export_manager = ExportManager()
        self.config_manager = ConfigManager()
        self.data_processor = DataProcessor()
        self.recent_files_manager = RecentFilesManager()
        self.selected_color: str = "auto"

        self._build_menu_bar()
        self._build_ui()

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

    # UI construction -----------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central_widget")  # For QSS targeting
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main horizontal splitter: sidebar | content area
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing completely

        # Left sidebar with scroll area
        sidebar_container = QWidget()
        sidebar_container.setMinimumWidth(280)  # Minimum width to ensure readability
        sidebar_container.setMaximumWidth(450)  # Maximum width to prevent over-expansion
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)

        control_panel = self._build_control_panel()
        scroll_area.setWidget(control_panel)
        sidebar_layout.addWidget(scroll_area)

        # Right content area (table + chart)
        content_splitter = self._build_content_area()

        # Add widgets to main splitter
        main_splitter.addWidget(sidebar_container)
        main_splitter.addWidget(content_splitter)

        # Set stretch factors: sidebar gets less, content gets more
        main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        main_splitter.setStretchFactor(1, 1)  # Content area stretches

        # Set initial sizes (sidebar: 450px, content: 830px)
        main_splitter.setSizes([450, 830])

        layout.addWidget(main_splitter)
        self.setCentralWidget(central)
        self.statusBar().showMessage("准备就绪")

    def _create_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """Helper to create a consistent card-style container."""
        card = QFrame()
        card.setProperty("class", "card")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)
        
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

    def _build_file_group(self) -> QFrame:
        card, layout = self._create_card("数据文件")

        self.open_button = QPushButton("打开数据文件")
        self.open_button.setProperty("class", "primary")
        self.open_button.clicked.connect(self._on_open_file)
        layout.addWidget(self.open_button)

        self.file_info = QTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setPlaceholderText("未加载数据")
        self.file_info.setMinimumHeight(100)
        layout.addWidget(self.file_info)
        return card

    def _build_chart_group(self) -> QFrame:
        card, layout = self._create_card("图表设置")
        
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft) # Align labels left

        self.x_combo = QComboBox()
        form_layout.addRow("X 轴列", self.x_combo)

        self.y_list = QListWidget()
        self.y_list.setSelectionMode(QListWidget.MultiSelection)
        self.y_list.setMinimumHeight(110)
        form_layout.addRow("Y 轴列", self.y_list)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem("折线图", "line")
        self.chart_type_combo.addItem("柱状图", "bar")
        self.chart_type_combo.addItem("散点图", "scatter")
        self.chart_type_combo.addItem("直方图", "histogram")
        self.chart_type_combo.addItem("箱线图", "boxplot")
        self.chart_type_combo.addItem("热力图", "heatmap")
        form_layout.addRow("图表类型", self.chart_type_combo)

        self.line_style_combo = QComboBox()
        self.line_style_combo.addItem("实线", "-")
        self.line_style_combo.addItem("虚线", "--")
        self.line_style_combo.addItem("点划线", "-.")
        form_layout.addRow("线型", self.line_style_combo)

        # Marker style selection
        self.marker_style_combo = QComboBox()
        self.marker_style_combo.addItem("无标记", "")
        self.marker_style_combo.addItem("圆形 (o)", "o")
        self.marker_style_combo.addItem("叉号 (x)", "x")
        self.marker_style_combo.addItem("加号 (+)", "+")
        self.marker_style_combo.addItem("方形 (s)", "s")
        self.marker_style_combo.addItem("三角形 (^)", "^")
        self.marker_style_combo.addItem("菱形 (D)", "D")
        form_layout.addRow("点样式", self.marker_style_combo)

        # Color selection
        color_row = QHBoxLayout()
        self.color_combo = QComboBox()
        self.color_combo.addItem("自动配色", "auto")
        self.color_combo.addItem("自定义颜色...", "custom")
        self.color_combo.currentIndexChanged.connect(self._on_color_changed)
        color_row.addWidget(self.color_combo)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet("background-color: #1f77b4; border: 1px solid gray;")
        color_row.addWidget(self.color_preview)
        form_layout.addRow("颜色", color_row)

        self.title_edit = QLineEdit("VisuLite Chart")
        form_layout.addRow("图表标题", self.title_edit)

        # Axis labels
        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("X 轴标签 (可空)")
        form_layout.addRow("X 轴标签", self.x_label_edit)

        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("Y 轴标签 (可空)")
        form_layout.addRow("Y 轴标签", self.y_label_edit)

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
        form_layout.addRow("导出尺寸 (宽/高)", size_row)

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

        # Enable word wrap for all labels in the form layout
        for i in range(form_layout.rowCount()):
            item = form_layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget():
                if isinstance(item.widget(), QLabel):
                    item.widget().setWordWrap(True)

        layout.addLayout(form_layout)

        button_row = QHBoxLayout()
        self.update_chart_button = QPushButton("更新图表")
        self.update_chart_button.setProperty("class", "primary")
        self.update_chart_button.clicked.connect(self._on_update_chart)
        button_row.addWidget(self.update_chart_button)
        self.export_button = QPushButton("导出图表")
        self.export_button.clicked.connect(self._on_export_chart)
        button_row.addWidget(self.export_button)
        layout.addLayout(button_row)

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
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Data slicing controls
        slice_row = QHBoxLayout()
        self.head_n_spin = QSpinBox()
        self.head_n_spin.setRange(0, 1000000)
        self.head_n_spin.setValue(0)
        self.head_n_spin.setSpecialValueText("全部")
        slice_row.addWidget(QLabel("前 N 行:"))
        slice_row.addWidget(self.head_n_spin)
        self.slice_button = QPushButton("截取")
        self.slice_button.clicked.connect(self._slice_data)
        slice_row.addWidget(self.slice_button)
        form_layout.addRow(slice_row)

        # Type conversion
        type_row = QHBoxLayout()
        self.convert_column_combo = QComboBox()
        type_row.addWidget(self.convert_column_combo)
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItem("字符串", "string")
        self.target_type_combo.addItem("整数", "int")
        self.target_type_combo.addItem("浮点数", "float")
        self.target_type_combo.addItem("日期时间", "datetime")
        type_row.addWidget(self.target_type_combo)
        self.convert_type_button = QPushButton("转换")
        self.convert_type_button.clicked.connect(self._convert_column_type)
        type_row.addWidget(self.convert_type_button)
        form_layout.addRow("类型转换", type_row)

        self.filter_column_combo = QComboBox()
        form_layout.addRow("文本筛选列", self.filter_column_combo)
        self.filter_text_input = QLineEdit()
        self.filter_text_input.setPlaceholderText("包含关键词...")
        form_layout.addRow("关键词", self.filter_text_input)

        self.range_column_combo = QComboBox()
        form_layout.addRow("数值列", self.range_column_combo)
        self.range_min_input = QLineEdit()
        self.range_min_input.setPlaceholderText("最小值 (可空)")
        self.range_max_input = QLineEdit()
        self.range_max_input.setPlaceholderText("最大值 (可空)")
        range_row = QHBoxLayout()
        range_row.addWidget(self.range_min_input)
        range_row.addWidget(self.range_max_input)
        form_layout.addRow("数值范围", range_row)

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

        # Enable word wrap for all labels in the form layout
        for i in range(form_layout.rowCount()):
            item = form_layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget():
                if isinstance(item.widget(), QLabel):
                    item.widget().setWordWrap(True)

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
        
        self.stats_view = QTextEdit()
        self.stats_view.setReadOnly(True)
        self.stats_view.setPlaceholderText("加载数据后显示统计信息")
        self.stats_view.setMinimumHeight(120)
        layout.addWidget(self.stats_view)
        return card

    def _build_content_area(self) -> QWidget:
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1) # Thinner splitter handle

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setAlternatingRowColors(True) # Better readability

        self.chart_widget = ChartWidget()
        splitter.addWidget(self.table_view)
        splitter.addWidget(self.chart_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        return splitter

    # Event handlers ------------------------------------------------------------------

    def _on_color_changed(self, index: int) -> None:
        if self.color_combo.currentData() == "custom":
            color = QColorDialog.getColor(QColor(self.selected_color if self.selected_color != "auto" else "#1f77b4"), self, "选择颜色")
            if color.isValid():
                self.selected_color = color.name()
                self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid gray;")
            else:
                self.color_combo.setCurrentIndex(0)
        else:
            self.selected_color = "auto"
            self.color_preview.setStyleSheet("background-color: #1f77b4; border: 1px solid gray;")

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
        self._update_file_info(meta)
        self._populate_columns(frame.columns.tolist())
        self._refresh_stats()
        
        # Update recent files
        self.recent_files_manager.add_file(file_path)
        self._update_recent_files_menu()
        
        self.statusBar().showMessage(f"已加载 {meta.path.name} ({meta.rows} 行)")

    def _on_update_chart(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件。")
            return
        config = self._collect_chart_config()
        self.state.chart_config = config
        try:
            self.chart_manager.plot(self.chart_widget.axes, self.state.data_frame, config)  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover - GUI feedback
            QMessageBox.warning(self, "绘图失败", str(exc))
            logger.exception("Chart rendering error")
        else:
            self.statusBar().showMessage("图表已更新")

    def _on_export_chart(self) -> None:
        if not self.chart_widget.figure.axes:
            QMessageBox.information(self, "提示", "请先绘制图表。")
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
            self.statusBar().showMessage(f"已导出到 {target}")
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "导出失败", str(exc))
        finally:
            figure.set_size_inches(*original_size, forward=True)

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
                exported = batch_plotter.run(source_dir, target_dir, config, fig_size, dpi, fmt)
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
            QMessageBox.information(self, "提示", "暂未保存配置。")
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
            self.color_preview.setStyleSheet(f"background-color: {config.color_scheme}; border: 1px solid gray;")
        else:
            self.selected_color = "auto"
            self.color_combo.setCurrentIndex(0)

    def _slice_data(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件。")
            return
        head_n = self.head_n_spin.value()
        if head_n == 0:
            return
        frame = self.state.data_frame
        if frame is None:
            return
        sliced = self.data_processor.slice_rows(frame, head_n=head_n)
        self.state.update_view(sliced)
        self.table_model.update_frame(sliced)
        self._refresh_stats()
        self.statusBar().showMessage(f"已截取前 {head_n} 行")

    def _convert_column_type(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件。")
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
            self.state.update_view(converted)
            self.table_model.update_frame(converted)
            self._refresh_stats()
            self.statusBar().showMessage(f"已将列 '{column}' 转换为 {target_type}")
        except Exception as exc:
            QMessageBox.warning(self, "类型转换失败", str(exc))

    def _apply_filters(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件。")
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
        self.state.update_view(filtered)
        self.table_model.update_frame(filtered)
        self._refresh_stats()
        self.statusBar().showMessage("筛选已应用")

    def _reset_dataset(self) -> None:
        frame = self.state.reset_view()
        if frame is None:
            return
        self.table_model.update_frame(frame)
        self._refresh_stats()
        self.statusBar().showMessage("已恢复原始数据")

    def _fill_missing(self) -> None:
        if not self.state.has_data():
            QMessageBox.information(self, "提示", "请先加载数据文件。")
            return
        frame = self.state.data_frame
        if frame is None:
            return
        method = self.fill_method_combo.currentData()
        filled = self.data_processor.fill_missing(frame.copy(), method)
        self.state.update_view(filled)
        self.table_model.update_frame(filled)
        self._refresh_stats()
        self.statusBar().showMessage("缺失值已处理")

    def _refresh_stats(self) -> None:
        if not self.state.has_data():
            self.stats_view.clear()
            return
        frame = self.state.data_frame
        if frame is None or frame.empty:
            self.stats_view.clear()
            return
        try:
            stats = (
                frame.describe(include="all")
                .transpose()
                .round(3)
                .fillna("")
                .head(12)
            )
            self.stats_view.setPlainText(stats.to_string())
        except Exception:
            self.stats_view.setPlainText("统计信息生成失败")

    @staticmethod
    def _parse_float(text: str) -> float | None:
        value = text.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None


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
        layout.addRow("X 轴列名", self.x_column_edit)

        # Y columns
        self.y_columns_edit = QLineEdit(", ".join(self.config.y_columns))
        layout.addRow("Y 轴列名 (逗号分隔)", self.y_columns_edit)

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
