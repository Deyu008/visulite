"""Chart export helpers."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt

logger = logging.getLogger("visulite.export_manager")


class ExportManager:
    """Persist matplotlib figures to disk with sensible defaults."""

    SUPPORTED_FORMATS = {"png", "jpg", "svg", "pdf"}

    def export(
        self, figure: plt.Figure, target_path: Path, dpi: int = 300, fmt: str | None = None
    ) -> Path:
        fmt = fmt or target_path.suffix.lstrip(".").lower()
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported export format: {fmt}")

        logger.info("Exporting chart to %s", target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(target_path, dpi=dpi, format=fmt, bbox_inches="tight")
        return target_path


__all__ = ["ExportManager"]
