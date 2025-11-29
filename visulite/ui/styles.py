
"""QSS Styles for VisuLite - Windows 11 Inspired Modern Theme."""

# Light theme (default)
QSS_LIGHT = """
/* ============================================
   Global Styles - Win11 Fluent Design Inspired (Light)
   ============================================ */

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 11pt;
    color: #1a1a1a;
}

QMainWindow {
    background-color: #f5f5f5;
}

QWidget#central_widget {
    background-color: #f5f5f5;
}

/* ============================================
   Scroll Area - Seamless Integration
   ============================================ */

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Modern Scrollbar - Win11 Style */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

/* ============================================
   Card Style - Fluent Design Cards
   ============================================ */

QFrame[class="card"] {
    background-color: #ffffff;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
}

QLabel[class="card-title"] {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 8px;
}

/* ============================================
   Buttons - Win11 Style
   ============================================ */

QPushButton {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 6px 14px;
    color: #1a1a1a;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #f9fafb;
    border-color: #c0c5cc;
}

QPushButton:pressed {
    background-color: #f0f1f3;
    border-color: #b0b5bb;
}

QPushButton:disabled {
    background-color: #f5f5f5;
    border-color: #e0e0e0;
    color: #a0a0a0;
}

/* Primary Button - Accent Color */
QPushButton[class="primary"] {
    background-color: #0078d4;
    border: 1px solid #0078d4;
    color: #ffffff;
}

QPushButton[class="primary"]:hover {
    background-color: #1084d8;
    border-color: #1084d8;
}

QPushButton[class="primary"]:pressed {
    background-color: #006cbe;
    border-color: #006cbe;
}

/* ============================================
   Input Controls - Clean Modern Style
   ============================================ */

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    min-height: 22px;
}

QLineEdit:hover {
    border-color: #b0b5bb;
}

QLineEdit:focus {
    border-color: #0078d4;
    border-width: 2px;
    padding: 5px 9px;
}

/* ============================================
   ComboBox - Full Modern Style with Dropdown
   ============================================ */

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 6px 10px;
    padding-right: 30px;
    min-height: 22px;
    color: #1a1a1a;
}

QComboBox:hover {
    border-color: #b0b5bb;
}

QComboBox:focus {
    border-color: #0078d4;
    border-width: 2px;
    padding: 5px 9px;
    padding-right: 29px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 24px;
    border: none;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666666;
}

QComboBox::down-arrow:hover {
    border-top-color: #1a1a1a;
}

/* ComboBox Dropdown List - Critical for readability */
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    selection-background-color: #e5f1fb;
    selection-color: #1a1a1a;
}

QComboBox QAbstractItemView::item {
    background-color: #ffffff;
    color: #1a1a1a;
    padding: 6px 10px;
    border-radius: 4px;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f5f5f5;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #e5f1fb;
    color: #1a1a1a;
}

/* Dropdown scrollbar */
QComboBox QAbstractItemView QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 8px;
}

QComboBox QAbstractItemView QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 4px;
}

/* ============================================
   SpinBox - Consistent Style
   ============================================ */

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 6px 10px;
    padding-right: 24px;
    min-height: 22px;
    color: #1a1a1a;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #b0b5bb;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #0078d4;
    border-width: 2px;
    padding: 5px 9px;
    padding-right: 23px;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}

/* ============================================
   List Widget - Modern Selection
   ============================================ */

QListWidget {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    color: #1a1a1a;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QListWidget::item:selected {
    background-color: #e5f1fb;
    color: #1a1a1a;
}

/* ============================================
   Table View - Clean Data Grid
   ============================================ */

QTableView {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    gridline-color: #f0f0f0;
    selection-background-color: #e5f1fb;
    selection-color: #1a1a1a;
    alternate-background-color: #fafbfc;
}

QTableView::item {
    padding: 4px 8px;
}

QTableView::item:selected {
    background-color: #e5f1fb;
}

QHeaderView::section {
    background-color: #f8f9fa;
    color: #505050;
    font-weight: 600;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #e0e0e0;
    border-right: 1px solid #f0f0f0;
}

QHeaderView::section:hover {
    background-color: #f0f1f3;
}

/* ============================================
   Text Edit - Multi-line Input
   ============================================ */

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

QTextEdit:focus {
    border-color: #0078d4;
}

/* ============================================
   Plain Text Edit - Stats Display
   ============================================ */

QPlainTextEdit {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

QPlainTextEdit:focus {
    border-color: #0078d4;
}

/* ============================================
   Checkbox - Modern Toggle Style
   ============================================ */

QCheckBox {
    spacing: 8px;
    color: #1a1a1a;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #d0d5dd;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #b0b5bb;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

/* ============================================
   Splitter - Subtle Divider
   ============================================ */

QSplitter::handle {
    background-color: #e5e5e5;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #0078d4;
}

/* ============================================
   Menu Bar - Win11 Style with Light Theme
   ============================================ */

QMenuBar {
    background-color: #f8f9fa;
    border-bottom: 1px solid #e5e5e5;
    padding: 2px 0;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 2px 2px;
    color: #1a1a1a;
}

QMenuBar::item:selected {
    background-color: #e5e5e5;
}

QMenuBar::item:pressed {
    background-color: #d8d8d8;
}

/* ============================================
   Menu - Dropdown with Light Theme (Critical Fix)
   ============================================ */

QMenu {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    background-color: transparent;
    color: #1a1a1a;
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    margin: 2px 4px;
}

QMenu::item:selected {
    background-color: #e5f1fb;
    color: #1a1a1a;
}

QMenu::item:disabled {
    color: #a0a0a0;
}

QMenu::separator {
    height: 1px;
    background-color: #e5e5e5;
    margin: 4px 8px;
}

QMenu::icon {
    padding-left: 8px;
}

/* ============================================
   Status Bar - Subtle Footer
   ============================================ */

QStatusBar {
    background-color: #f8f9fa;
    border-top: 1px solid #e5e5e5;
    color: #505050;
    padding: 4px 8px;
}

QStatusBar::item {
    border: none;
}

/* ============================================
   ToolTip - Modern Appearance
   ============================================ */

QToolTip {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px 10px;
    color: #1a1a1a;
}

/* ============================================
   Dialog - Modal Windows
   ============================================ */

QDialog {
    background-color: #f5f5f5;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* ============================================
   Group Box - Legacy Support (if used)
   ============================================ */

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #1a1a1a;
    background-color: #ffffff;
}

/* ============================================
   Tab Widget (if used in future)
   ============================================ */

QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: transparent;
    border: none;
    padding: 8px 16px;
    color: #505050;
}

QTabBar::tab:selected {
    color: #0078d4;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    color: #1a1a1a;
    background-color: #f5f5f5;
}

/* ============================================
   Matplotlib Navigation Toolbar - Enhanced Background Focus
   ============================================ */

#matplotlib-toolbar {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 4px;
}

/* 主要样式：为按钮添加方形背景框 */
#matplotlib-toolbar QToolButton {
    background-color: #e0e0e0;  /* 默认灰色背景 */
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
    min-height: 28px;
    min-width: 28px;
    icon-size: 16px;
}

#matplotlib-toolbar QToolButton:hover {
    background-color: #0078d4;  /* 悬停时蓝色背景 */
    border-color: #0066cc;
}

#matplotlib-toolbar QToolButton:pressed {
    background-color: #0052a3;  /* 按下时更深的蓝色 */
    border-color: #004080;
}

#matplotlib-toolbar QToolButton:checked {
    background-color: #0078d4;  /* 选中状态蓝色背景 */
    border-color: #0066cc;
}

#matplotlib-toolbar QToolButton:disabled {
    background-color: #f5f5f5;
    border-color: #e0e0e0;
    color: #999999;
}

/* 备用选择器：确保样式覆盖 */
QToolBar QToolButton {
    background-color: #e0e0e0;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
    min-height: 28px;
    min-width: 28px;
}

QToolBar QToolButton:hover {
    background-color: #0078d4;
    border-color: #0066cc;
}

QToolBar QToolButton:checked {
    background-color: #0078d4;
    border-color: #0066cc;
}
"""

# Dark theme
QSS_DARK = """
/* ============================================
   Global Styles - Win11 Fluent Design Inspired (Dark)
   ============================================ */

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 11pt;
    color: #e4e4e4;
    background-color: #1e1e1e;
}

QMainWindow {
    background-color: #1e1e1e;
}

QWidget#central_widget {
    background-color: #1e1e1e;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Scrollbar */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #5a5a5a;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #787878;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #5a5a5a;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #787878;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

/* Card Style */
QFrame[class="card"] {
    background-color: #2d2d2d;
    border-radius: 8px;
    border: 1px solid #3d3d3d;
}

QLabel[class="card-title"] {
    font-size: 14px;
    font-weight: 600;
    color: #e4e4e4;
    padding-bottom: 8px;
    border-bottom: 1px solid #3d3d3d;
    margin-bottom: 8px;
}

/* Buttons */
QPushButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 6px 14px;
    color: #e4e4e4;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #4d4d4d;
    border-color: #5d5d5d;
}

QPushButton:pressed {
    background-color: #2d2d2d;
    border-color: #3d3d3d;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #6a6a6a;
}

QPushButton[class="primary"] {
    background-color: #0078d4;
    border: 1px solid #0078d4;
    color: #ffffff;
}

QPushButton[class="primary"]:hover {
    background-color: #1084d8;
    border-color: #1084d8;
}

QPushButton[class="primary"]:pressed {
    background-color: #006cbe;
    border-color: #006cbe;
}

/* Input Controls */
QLineEdit {
    background-color: #3d3d3d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    min-height: 22px;
}

QLineEdit:hover {
    border-color: #5d5d5d;
}

QLineEdit:focus {
    border-color: #0078d4;
    border-width: 2px;
    padding: 5px 9px;
}

/* ComboBox */
QComboBox {
    background-color: #3d3d3d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 6px 10px;
    padding-right: 30px;
    min-height: 22px;
}

QComboBox:hover {
    border-color: #5d5d5d;
}

QComboBox:focus {
    border-color: #0078d4;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 24px;
    border: none;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #a0a0a0;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    selection-background-color: #3d5a80;
    selection-color: #e4e4e4;
}

QComboBox QAbstractItemView::item {
    background-color: #2d2d2d;
    color: #e4e4e4;
    padding: 6px 10px;
    border-radius: 4px;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #3d3d3d;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #3d5a80;
}

/* SpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #3d3d3d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #5d5d5d;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #0078d4;
}

/* List Widget */
QListWidget {
    background-color: #2d2d2d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    color: #e4e4e4;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QListWidget::item:selected {
    background-color: #3d5a80;
    color: #e4e4e4;
}

/* Table View */
QTableView {
    background-color: #2d2d2d;
    color: #e4e4e4;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    gridline-color: #3d3d3d;
    selection-background-color: #3d5a80;
    selection-color: #e4e4e4;
    alternate-background-color: #262626;
}

QTableView::item {
    padding: 4px 8px;
    color: #e4e4e4;
}

QTableView::item:selected {
    background-color: #3d5a80;
    color: #e4e4e4;
}

QHeaderView::section {
    background-color: #2a2a2a;
    color: #a0a0a0;
    font-weight: 600;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #3d3d3d;
    border-right: 1px solid #3a3a3a;
}

QHeaderView::section:hover {
    background-color: #3a3a3a;
}

/* Text Edit */
QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #e4e4e4;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0078d4;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    color: #e4e4e4;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #5d5d5d;
    border-radius: 4px;
    background-color: #3d3d3d;
}

QCheckBox::indicator:hover {
    border-color: #7d7d7d;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

/* Splitter */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:hover {
    background-color: #0078d4;
}

/* Menu Bar */
QMenuBar {
    background-color: #2a2a2a;
    border-bottom: 1px solid #3d3d3d;
    padding: 2px 0;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 2px 2px;
    color: #e4e4e4;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenuBar::item:pressed {
    background-color: #4d4d4d;
}

/* Menu */
QMenu {
    background-color: #2d2d2d;
    color: #e4e4e4;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    background-color: transparent;
    color: #e4e4e4;
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    margin: 2px 4px;
}

QMenu::item:selected {
    background-color: #3d5a80;
    color: #e4e4e4;
}

QMenu::item:disabled {
    color: #6a6a6a;
}

QMenu::separator {
    height: 1px;
    background-color: #3d3d3d;
    margin: 4px 8px;
}

/* Status Bar */
QStatusBar {
    background-color: #2a2a2a;
    border-top: 1px solid #3d3d3d;
    color: #a0a0a0;
    padding: 4px 8px;
}

QStatusBar::item {
    border: none;
}

/* ToolTip */
QToolTip {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e4e4e4;
}

/* Dialog */
QDialog {
    background-color: #1e1e1e;
}

/* Group Box */
QGroupBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #e4e4e4;
    background-color: #2d2d2d;
}

/* Tab Widget */
QTabWidget::pane {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: transparent;
    border: none;
    padding: 8px 16px;
    color: #a0a0a0;
}

QTabBar::tab:selected {
    color: #0078d4;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    color: #e4e4e4;
    background-color: #3d3d3d;
}

/* Matplotlib Toolbar */
#matplotlib-toolbar {
    background-color: #2a2a2a;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 4px;
}

#matplotlib-toolbar QToolButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
    min-height: 28px;
    min-width: 28px;
}

#matplotlib-toolbar QToolButton:hover {
    background-color: #0078d4;
    border-color: #0066cc;
}

#matplotlib-toolbar QToolButton:pressed {
    background-color: #0052a3;
    border-color: #004080;
}

#matplotlib-toolbar QToolButton:checked {
    background-color: #0078d4;
    border-color: #0066cc;
}

QToolBar QToolButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
    min-height: 28px;
    min-width: 28px;
}

QToolBar QToolButton:hover {
    background-color: #0078d4;
    border-color: #0066cc;
}

QToolBar QToolButton:checked {
    background-color: #0078d4;
    border-color: #0066cc;
}

/* Label */
QLabel {
    color: #e4e4e4;
    background-color: transparent;
}
"""

# Default QSS (light theme for backward compatibility)
QSS = QSS_LIGHT
