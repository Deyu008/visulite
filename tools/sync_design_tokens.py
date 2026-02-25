"""Sync VisuLite theme tokens into the Pencil .pen design file.

This keeps `designs/visulite.pen` variables aligned with `visulite.ui.styles`.

Usage:
  python tools/sync_design_tokens.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
PEN_PATH = ROOT / "designs" / "visulite.pen"


_RGBA_RE = re.compile(
    r"^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)$",
    re.IGNORECASE,
)
_RGB_RE = re.compile(
    r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$",
    re.IGNORECASE,
)


def _clamp_int(v: int, lo: int = 0, hi: int = 255) -> int:
    return max(lo, min(hi, int(v)))


def qss_color_to_pen(color: str) -> str:
    """Convert QSS color strings to .pen compatible color.

    - Pass through #RGB/#RRGGBB/#RRGGBBAA
    - Convert rgba(r,g,b,a) to #RRGGBBAA
    - Convert rgb(r,g,b) to #RRGGBB
    """

    s = (color or "").strip()
    if not s:
        return s

    if s.startswith("#"):
        return s.upper()

    m = _RGBA_RE.match(s)
    if m:
        r, g, b = (_clamp_int(int(m.group(i))) for i in (1, 2, 3))
        a_f = float(m.group(4))
        a = _clamp_int(round(max(0.0, min(1.0, a_f)) * 255))
        return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

    m = _RGB_RE.match(s)
    if m:
        r, g, b = (_clamp_int(int(m.group(i))) for i in (1, 2, 3))
        return f"#{r:02X}{g:02X}{b:02X}"

    # Unknown format; return as-is.
    return s


def _set_theme_color_var(doc: Dict[str, Any], key: str, light: str, dark: str) -> None:
    variables = doc.setdefault("variables", {})
    variables[key] = {
        "type": "color",
        "value": [
            {"theme": {"mode": "light"}, "value": qss_color_to_pen(light)},
            {"theme": {"mode": "dark"}, "value": qss_color_to_pen(dark)},
        ],
    }


def _set_number_var(doc: Dict[str, Any], key: str, value: int) -> None:
    doc.setdefault("variables", {})[key] = {"type": "number", "value": int(value)}


def _set_string_var(doc: Dict[str, Any], key: str, value: str) -> None:
    doc.setdefault("variables", {})[key] = {"type": "string", "value": str(value)}


def main() -> int:
    # Allow running as a script without installing the package.
    sys.path.insert(0, str(ROOT))

    from visulite.ui.styles import DARK_TOKENS, LIGHT_TOKENS

    if not PEN_PATH.exists():
        raise SystemExit(f"Missing {PEN_PATH}")

    doc = json.loads(PEN_PATH.read_text(encoding="utf-8"))
    doc.setdefault("themes", {"mode": ["light", "dark"]})

    _set_theme_color_var(doc, "bg", LIGHT_TOKENS.bg, DARK_TOKENS.bg)
    _set_theme_color_var(doc, "surface", LIGHT_TOKENS.surface, DARK_TOKENS.surface)
    _set_theme_color_var(doc, "surface_2", LIGHT_TOKENS.surface_2, DARK_TOKENS.surface_2)
    _set_theme_color_var(doc, "surface_3", LIGHT_TOKENS.surface_3, DARK_TOKENS.surface_3)
    _set_theme_color_var(doc, "glass", LIGHT_TOKENS.glass, DARK_TOKENS.glass)
    _set_theme_color_var(doc, "stroke", LIGHT_TOKENS.stroke, DARK_TOKENS.stroke)
    _set_theme_color_var(doc, "stroke_subtle", LIGHT_TOKENS.stroke_subtle, DARK_TOKENS.stroke_subtle)
    _set_theme_color_var(doc, "text", LIGHT_TOKENS.text, DARK_TOKENS.text)
    _set_theme_color_var(doc, "text_muted", LIGHT_TOKENS.text_muted, DARK_TOKENS.text_muted)
    _set_theme_color_var(doc, "accent", LIGHT_TOKENS.accent, DARK_TOKENS.accent)
    _set_theme_color_var(doc, "accent_soft", LIGHT_TOKENS.accent_soft, DARK_TOKENS.accent_soft)
    _set_theme_color_var(doc, "selection_bg", LIGHT_TOKENS.selection_bg, DARK_TOKENS.selection_bg)

    _set_number_var(doc, "radius_sm", LIGHT_TOKENS.radius_sm)
    _set_number_var(doc, "radius_md", LIGHT_TOKENS.radius_md)
    _set_number_var(doc, "radius_lg", LIGHT_TOKENS.radius_lg)

    # For Pencil preview, prefer a Windows-available font to avoid warnings.
    _set_string_var(doc, "font_primary", "Segoe UI")

    PEN_PATH.write_text(json.dumps(doc, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
