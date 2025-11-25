
"""QSS Styles for VisuLite - Windows 11 Inspired Modern Theme."""

QSS = """
/* ============================================
   Global Styles - Win11 Fluent Design Inspired
   ============================================ */

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
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
"""
