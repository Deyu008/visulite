"""QSS styles for VisuLite.

This module intentionally contains styling only.

Design goal:
- Token-driven light/dark themes.
- iOS-like surfaces and overlay scrollbars.

Public API expected by the app:
- QSS_LIGHT / QSS_DARK / QSS
- LIGHT_TOKENS / DARK_TOKENS
- build_qss(tokens) -> str
"""

from __future__ import annotations

from dataclasses import dataclass
from string import Template


@dataclass(frozen=True)
class ThemeTokens:
    """Theme tokens used to generate QSS.

    Notes:
    - Keep values as plain strings/ints that can be safely interpolated into QSS.
    - Prefer ASCII for cross-platform editor compatibility.
    """

    name: str
    is_dark: bool

    # Typography
    font_family: str
    base_font_pt: int
    small_font_pt: int

    # Radii
    radius_sm: int
    radius_md: int
    radius_lg: int

    # Core colors
    bg: str
    surface: str
    surface_2: str
    surface_3: str
    glass: str
    stroke: str
    stroke_subtle: str

    text: str
    text_muted: str
    text_faint: str
    text_disabled: str

    accent: str
    accent_hover: str
    accent_pressed: str
    accent_soft: str

    danger: str
    warning: str
    success: str

    selection_bg: str
    selection_text: str
    focus_ring: str

    # Widget-specific
    button_bg: str
    button_bg_hover: str
    button_bg_pressed: str
    button_stroke: str

    input_bg: str
    input_stroke: str
    input_stroke_hover: str

    menu_bg: str
    tooltip_bg: str

    scrollbar_handle: str
    scrollbar_handle_hover: str

    badge_bg: str
    badge_stroke: str
    badge_text: str

    # Used by matplotlib canvas welcome styling.
    chart_bg: str


LIGHT_TOKENS = ThemeTokens(
    name="light",
    is_dark=False,
    font_family='"SF Pro Text", "SF Pro Display", "Segoe UI Variable", "Segoe UI", "Helvetica Neue", sans-serif',
    base_font_pt=11,
    small_font_pt=10,
    radius_sm=10,
    radius_md=12,
    radius_lg=12,
    # iOS-like system grouped backgrounds
    bg="#F2F2F7",
    surface="#FFFFFF",
    surface_2="#F9F9FB",
    surface_3="#EFEFF4",
    # Slightly more opaque so small/secondary text stays readable over Mica/Acrylic.
    glass="rgba(255, 255, 255, 0.86)",
    stroke="rgba(60, 60, 67, 0.29)",
    stroke_subtle="rgba(60, 60, 67, 0.22)",
    text="#000000",
    # Use #RRGGBBAA so the same token works in both Qt (QSS) and matplotlib.
    # Light theme readability: avoid overly faint labels on translucent surfaces.
    text_muted="#3C3C43F0",
    text_faint="#3C3C43C8",
    text_disabled="#3C3C4396",
    accent="#007AFF",
    accent_hover="#0A84FF",
    accent_pressed="#0062CC",
    accent_soft="rgba(0, 122, 255, 0.14)",
    danger="#FF3B30",
    warning="#FF9F0A",
    success="#34C759",
    selection_bg="rgba(0, 122, 255, 0.18)",
    selection_text="#000000",
    focus_ring="rgba(0, 122, 255, 0.45)",
    button_bg="rgba(118, 118, 128, 0.12)",
    button_bg_hover="rgba(118, 118, 128, 0.18)",
    button_bg_pressed="rgba(118, 118, 128, 0.24)",
    button_stroke="rgba(60, 60, 67, 0.26)",
    input_bg="#FFFFFF",
    input_stroke="rgba(60, 60, 67, 0.24)",
    input_stroke_hover="rgba(60, 60, 67, 0.40)",
    menu_bg="#FFFFFF",
    tooltip_bg="#FFFFFF",
    scrollbar_handle="rgba(60, 60, 67, 0.34)",
    scrollbar_handle_hover="rgba(60, 60, 67, 0.50)",
    badge_bg="rgba(118, 118, 128, 0.12)",
    badge_stroke="rgba(60, 60, 67, 0.26)",
    badge_text="rgba(60, 60, 67, 0.92)",
    chart_bg="#F9F9FB",
)


DARK_TOKENS = ThemeTokens(
    name="dark",
    is_dark=True,
    font_family='"SF Pro Text", "SF Pro Display", "Segoe UI Variable", "Segoe UI", "Helvetica Neue", sans-serif',
    base_font_pt=11,
    small_font_pt=10,
    radius_sm=10,
    radius_md=12,
    radius_lg=12,
    # iOS-like system grouped backgrounds (dark)
    bg="#0B0B0C",
    surface="#1C1C1E",
    surface_2="#2C2C2E",
    surface_3="#3A3A3C",
    glass="rgba(28, 28, 30, 0.78)",
    stroke="rgba(84, 84, 88, 0.60)",
    stroke_subtle="rgba(84, 84, 88, 0.40)",
    text="#FFFFFF",
    # Use #RRGGBBAA so the same token works in both Qt (QSS) and matplotlib.
    text_muted="#EBEBF599",
    text_faint="#EBEBF561",
    text_disabled="#EBEBF53D",
    accent="#0A84FF",
    accent_hover="#2994FF",
    accent_pressed="#0071E3",
    accent_soft="rgba(10, 132, 255, 0.22)",
    danger="#FF453A",
    warning="#FF9F0A",
    success="#30D158",
    selection_bg="rgba(10, 132, 255, 0.26)",
    selection_text="#FFFFFF",
    focus_ring="rgba(10, 132, 255, 0.52)",
    button_bg="rgba(118, 118, 128, 0.22)",
    button_bg_hover="rgba(118, 118, 128, 0.30)",
    button_bg_pressed="rgba(118, 118, 128, 0.36)",
    button_stroke="rgba(84, 84, 88, 0.55)",
    input_bg="#1C1C1E",
    input_stroke="rgba(84, 84, 88, 0.55)",
    input_stroke_hover="rgba(84, 84, 88, 0.72)",
    menu_bg="#2C2C2E",
    tooltip_bg="#2C2C2E",
    scrollbar_handle="rgba(235, 235, 245, 0.22)",
    scrollbar_handle_hover="rgba(235, 235, 245, 0.34)",
    badge_bg="rgba(118, 118, 128, 0.24)",
    badge_stroke="rgba(84, 84, 88, 0.55)",
    badge_text="rgba(235, 235, 245, 0.82)",
    chart_bg="#1C1C1E",
)


_QSS_TEMPLATE = Template(
    r"""
/*
Generated by visulite.ui.styles.build_qss(theme=$name)

Requirements:
- UTF-8 text, no BOM, no NULL bytes.
- Styling-only; no functional behavior.
*/

/* ============ Global ============ */

QWidget {
    font-family: $font_family;
    font-size: ${base_font_pt}pt;
    color: $text;
}

QWidget:disabled {
    color: $text_disabled;
}

QMainWindow,
QDialog,
QWidget#central_widget {
    background-color: $bg;
}

/* When Windows backdrop (Mica/Acrylic) is enabled, slightly reduce opacity
   so the system material can show through. */
QMainWindow[backdrop="on"],
QDialog[backdrop="on"],
QWidget#central_widget[backdrop="on"] {
    /* Keep the base layer solid for readability; translucency is handled by surfaces. */
    background-color: $bg;
}

QLabel {
    background-color: transparent;
}

/* ============ Surfaces (QFrame + dynamic property) ============ */

QFrame[surface="glass"] {
    background-color: $glass;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

QFrame[surface="card"],
QFrame[class="card"] {
    background-color: $surface;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

QFrame[surface="panel"],
QFrame[class="panel"] {
    background-color: $surface_2;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

QFrame[role="sidebar-panel"] {
    background-color: $surface_2;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

QFrame[role="sidebar-card"] {
    border-color: $stroke_subtle;
}

QFrame[role="stats-shell"] {
    background-color: $surface;
    border-color: $stroke_subtle;
}

QLabel[class="card-title"] {
    font-size: ${base_font_pt}pt;
    font-weight: 650;
    color: $text;
    padding-bottom: 8px;
    border-bottom: 1px solid $stroke_subtle;
}

/* ============ Caption / Hint ============ */

QLabel[class="caption"],
QLabel[class="hint"] {
    font-size: ${small_font_pt}pt;
    color: $text_muted;
}

QLabel[class="caption"][tone="muted"],
QLabel[class="hint"][tone="muted"] {
    color: $text_muted;
}

QLabel[class="caption"][tone="info"],
QLabel[class="hint"][tone="info"] {
    color: $accent;
}

QLabel[class="caption"][tone="danger"],
QLabel[class="hint"][tone="danger"] {
    color: $danger;
}

QLabel[class="form-label"] {
    color: $text_muted;
    font-size: ${small_font_pt}pt;
    font-weight: 650;
}

/* ============ Badges / Pills ============ */

QLabel[class="metric-badge"] {
    background-color: $badge_bg;
    color: $badge_text;
    border: 1px solid $badge_stroke;
    border-radius: ${radius_md}px;
    padding: 5px 10px;
    font-size: ${small_font_pt}pt;
    font-weight: 600;
}

/* ============ Buttons ============ */

QPushButton {
    background-color: $button_bg;
    border: 1px solid $button_stroke;
    border-radius: ${radius_md}px;
    padding: 7px 12px;
    min-height: 26px;
    color: $text;
}

QPushButton:hover {
    background-color: $button_bg_hover;
}

QPushButton:pressed {
    background-color: $button_bg_pressed;
}

QPushButton:disabled {
    background-color: transparent;
    border-color: $stroke_subtle;
    color: $text_disabled;
}

QPushButton[class="primary"] {
    background-color: $accent;
    border: 1px solid $accent;
    color: #ffffff;
    font-weight: 650;
}

QPushButton[class="primary"]:hover {
    background-color: $accent_hover;
    border-color: $accent_hover;
}

QPushButton[class="primary"]:pressed {
    background-color: $accent_pressed;
    border-color: $accent_pressed;
}

QPushButton[class="sticky-primary"] {
    background-color: $accent;
    border: 1px solid $accent;
    color: #ffffff;
    font-weight: 650;
}

QPushButton[class="sticky-primary"]:hover {
    background-color: $accent_hover;
    border-color: $accent_hover;
}

QPushButton[class="sticky-primary"]:pressed {
    background-color: $accent_pressed;
    border-color: $accent_pressed;
}

QPushButton[class="sticky-secondary"] {
    background-color: $button_bg;
    border: 1px solid $button_stroke;
    color: $text;
    font-weight: 600;
}

QPushButton[class="sticky-secondary"]:hover {
    background-color: $button_bg_hover;
    border-color: $stroke;
}

QPushButton[class="sticky-secondary"]:pressed {
    background-color: $button_bg_pressed;
}

QPushButton[class="ghost"] {
    background-color: transparent;
    border: 1px solid $stroke_subtle;
    color: $text;
}

QPushButton[class="ghost"]:hover {
    background-color: $button_bg;
    border-color: $stroke;
}

QPushButton[class="toolbar-action"] {
    background-color: $accent_soft;
    border: 1px solid $focus_ring;
    color: $accent;
    font-weight: 600;
}

QPushButton[class="toolbar-action"]:hover {
    background-color: $selection_bg;
    border-color: $focus_ring;
}

/* ============ Inputs ============ */

QLineEdit,
QTextEdit,
QPlainTextEdit {
    background-color: $input_bg;
    border: 1px solid $input_stroke;
    border-radius: ${radius_md}px;
    padding: 7px 10px;
    selection-background-color: $selection_bg;
    selection-color: $selection_text;
}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover {
    border-color: $input_stroke_hover;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus {
    border: 2px solid $accent;
    padding: 6px 9px;
}

QLineEdit[class="table-search"] {
    background-color: $surface;
}

/* ============ ComboBox / SpinBox ============ */

QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: $input_bg;
    border: 1px solid $input_stroke;
    border-radius: ${radius_md}px;
    padding: 7px 10px;
    padding-right: 30px;
    min-height: 26px;
}

QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover {
    border-color: $input_stroke_hover;
}

QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 2px solid $accent;
    padding: 6px 9px;
    padding-right: 29px;
}

QComboBox::drop-down,
QSpinBox::up-button,
QSpinBox::down-button,
QDoubleSpinBox::up-button,
QDoubleSpinBox::down-button {
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
    border-top: 5px solid $text_faint;
}

QComboBox QAbstractItemView {
    background-color: $menu_bg;
    border: 1px solid $stroke;
    border-radius: ${radius_md}px;
    padding: 6px;
    outline: none;
    selection-background-color: $selection_bg;
    selection-color: $text;
}

QComboBox QAbstractItemView::item {
    padding: 7px 10px;
    border-radius: ${radius_md}px;
    min-height: 34px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: $button_bg;
}

/* ============ CheckBox ============ */

QCheckBox {
    spacing: 8px;
    color: $text;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid $input_stroke;
    border-radius: 6px;
    background-color: $surface;
}

QCheckBox::indicator:hover {
    border-color: $stroke;
}

QCheckBox::indicator:checked {
    background-color: $accent;
    border-color: $accent;
}

/* ============ Lists / Views ============ */

QListWidget,
QAbstractItemView {
    background-color: $surface;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
    outline: none;
}

QListWidget::item,
QAbstractItemView::item {
    padding: 7px 10px;
}

QListWidget::item:selected,
QAbstractItemView::item:selected {
    background-color: $selection_bg;
}

QListWidget::item:hover:!selected,
QAbstractItemView::item:hover:!selected {
    background-color: $button_bg;
}

/* ============ Table ============ */

QTableView,
QTableWidget,
QTableWidget[class="table-stats"] {
    background-color: $surface;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_md}px;
    gridline-color: $stroke_subtle;
    selection-background-color: $selection_bg;
    selection-color: $text;
    alternate-background-color: $surface_2;
    outline: none;
}

QTableView::item,
QTableWidget::item {
    padding: 4px 8px;
}

QTableView::item:selected,
QTableWidget::item:selected {
    background-color: $selection_bg;
}

QTableView::item:hover:!selected,
QTableWidget::item:hover:!selected {
    background-color: $button_bg;
}

QHeaderView {
    background-color: transparent;
}

QHeaderView::section {
    background-color: $surface_3;
    color: $text;
    font-weight: 650;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid $stroke;
    border-right: 1px solid $stroke_subtle;
}

QHeaderView::section:horizontal {
    min-height: 34px;
}

QHeaderView::section:vertical {
    min-width: 42px;
}

QTableCornerButton::section {
    background-color: $surface_3;
    border: none;
    border-right: 1px solid $stroke_subtle;
    border-bottom: 1px solid $stroke;
}

/* ============ Splitter ============ */

QSplitter::handle {
    background-color: $stroke_subtle;
}

QSplitter::handle:hover {
    background-color: $focus_ring;
}

/* ============ Menu Bar / Menu ============ */

QMenuBar {
    /* Let the surrounding surface paint the background to avoid square corners. */
    background-color: transparent;
    border: none;
    padding: 2px 0;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: ${radius_md}px;
    margin: 2px 2px;
    color: $text;
}

QMenuBar::item:selected {
    background-color: $button_bg;
}

QMenuBar::item:pressed {
    background-color: $button_bg_pressed;
}

QMenu {
    background-color: $menu_bg;
    border: 1px solid $stroke;
    /* Match Win11 DWM rounding better than the app's larger surface radius. */
    border-radius: 10px;
    padding: 8px;
}

QMenu::item {
    background-color: transparent;
    color: $text;
    padding: 8px 26px 8px 10px;
    border-radius: ${radius_md}px;
    margin: 2px 2px;
    min-height: 34px;
}

QMenu::item:selected {
    background-color: $selection_bg;
}

QMenu::item:disabled {
    color: $text_disabled;
}

QMenu::separator {
    height: 1px;
    background-color: $stroke_subtle;
    margin: 6px 10px;
}

/* ============ Status Bar / Tooltip ============ */

QStatusBar {
    background-color: $glass;
    border-top: 1px solid $stroke_subtle;
    color: $text;
    padding: 4px 8px;
}

QStatusBar::item {
    border: none;
}

QToolTip {
    background-color: $tooltip_bg;
    border: 1px solid $stroke;
    border-radius: ${radius_md}px;
    padding: 6px 10px;
    color: $text;
}

/* ============ Scroll Area / Overlay Scrollbars (iOS-like) ============ */

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: transparent;
    border: none;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: $scrollbar_handle;
    border-radius: 4px;
    min-height: 28px;
    margin: 2px 1px;
}

QScrollBar::handle:vertical:hover {
    background-color: $scrollbar_handle_hover;
}

QScrollBar::handle:vertical:pressed {
    background-color: $scrollbar_handle_hover;
}

QScrollBar:horizontal {
    background-color: transparent;
    border: none;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: $scrollbar_handle;
    border-radius: 4px;
    min-width: 28px;
    margin: 1px 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: $scrollbar_handle_hover;
}

QScrollBar::handle:horizontal:pressed {
    background-color: $scrollbar_handle_hover;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0;
    height: 0;
    background: none;
}

QScrollBar::add-page,
QScrollBar::sub-page {
    background: none;
}

QAbstractScrollArea::corner {
    background: transparent;
}

/* ============ Toolbars (Matplotlib + App) ============ */

#matplotlib-toolbar {
    background-color: $glass;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_md}px;
    padding: 4px;
}

#matplotlib-toolbar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: ${radius_md}px;
    padding: 4px;
    margin: 2px;
    min-height: 32px;
    min-width: 32px;
    icon-size: 18px;
}

#matplotlib-toolbar QToolButton:hover {
    background-color: $button_bg;
    border-color: $stroke_subtle;
}

#matplotlib-toolbar QToolButton:pressed {
    background-color: $button_bg_pressed;
    border-color: $stroke;
}

#matplotlib-toolbar QToolButton:checked {
    background-color: $accent_soft;
    border-color: $focus_ring;
}

QToolBar#matplotlib-toolbar::separator {
    width: 1px;
    margin: 5px 6px;
    background-color: $stroke_subtle;
}

/* ============ App Shell Specific IDs ============ */

#command-bar {
    background-color: $glass;
    border-bottom: 1px solid $stroke_subtle;
    /* Avoid visible square corners against Win11 rounded window region. */
    border-top-left-radius: ${radius_lg}px;
    border-top-right-radius: ${radius_lg}px;
}

QLabel#hero-title {
    font-size: 20px;
    font-weight: 750;
    color: $text;
    letter-spacing: 0.2px;
}

QLabel#hero-subtitle {
    font-size: ${small_font_pt}pt;
    color: $text_muted;
}

#content-toolbar {
    background-color: $glass;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

#sidebar-action-dock {
    background-color: $glass;
    border: 1px solid $stroke_subtle;
    border-radius: ${radius_lg}px;
}

#quick-recent-frame {
    background: transparent;
    border: none;
}

QLabel[class="toolbar-label"] {
    font-size: ${small_font_pt}pt;
    color: $text_muted;
    font-weight: 650;
}

/* ============ Swatch ============ */

QFrame[class="swatch"],
QPushButton[class="swatch"] {
    background-color: transparent;
    border: 1px solid $stroke;
    border-radius: ${radius_sm}px;
}

/* ============ Table Stats Container Hook ============ */

QWidget[class="table-stats"],
QFrame[class="table-stats"] {
    background-color: $surface;
}
"""
)


def build_qss(tokens: ThemeTokens) -> str:
    """Build a single QSS string for the provided tokens."""

    data = tokens.__dict__.copy()
    # Keep the generated stylesheet strictly textual.
    qss = _QSS_TEMPLATE.substitute(data)
    # Ensure a trailing newline for nicer diffs and editor behavior.
    if not qss.endswith("\n"):
        qss += "\n"
    return qss


QSS_LIGHT: str = build_qss(LIGHT_TOKENS)
QSS_DARK: str = build_qss(DARK_TOKENS)

# Backward compatibility
QSS: str = QSS_LIGHT


__all__ = [
    "ThemeTokens",
    "LIGHT_TOKENS",
    "DARK_TOKENS",
    "build_qss",
    "QSS_LIGHT",
    "QSS_DARK",
    "QSS",
]
