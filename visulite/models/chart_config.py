"""Chart configuration dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class ChartConfig:
    """Stores the current chart configuration."""

    x_column: str | None = None
    y_columns: List[str] = field(default_factory=list)
    chart_type: str = "line"
    show_legend: bool = True
    show_grid: bool = True
    title: str = "VisuLite Chart"
    line_style: str = "-"
    marker_style: str = ""  # "", "o", "x", "+", "s", "^", "D"
    color_scheme: str = "auto"  # "auto" or hex color like "#FF0000"
    x_label: Optional[str] = None
    y_label: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


__all__ = ["ChartConfig"]
