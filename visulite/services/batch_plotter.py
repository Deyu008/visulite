"""Batch plotting utilities that reuse chart configuration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from matplotlib.backends.backend_agg import FigureCanvasAgg  # type: ignore
from matplotlib.figure import Figure

from visulite.models.chart_config import ChartConfig
from visulite.services.chart_manager import ChartManager
from visulite.services.data_loader import DataLoader
from visulite.services.export_manager import ExportManager

logger = logging.getLogger("visulite.batch_plotter")


class BatchPlotter:
    """Render charts for every supported data file inside a directory."""

    def __init__(
        self,
        data_loader: DataLoader,
        chart_manager: ChartManager,
        export_manager: ExportManager,
    ) -> None:
        self.data_loader = data_loader
        self.chart_manager = chart_manager
        self.export_manager = export_manager

    def run(
        self,
        source_dir: Path,
        target_dir: Path,
        config: ChartConfig,
        figure_size: tuple[float, float],
        dpi: int,
        fmt: str,
    ) -> List[Path]:
        exported: List[Path] = []
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
        for file_path in sorted(source_dir.iterdir()):
            if file_path.suffix.lower() not in self.data_loader.SUPPORTED_EXTENSIONS:
                continue
            try:
                frame, _ = self.data_loader.load(file_path)
                required_columns = [config.x_column] if config.x_column else []
                required_columns += list(config.y_columns)
                missing = [col for col in required_columns if col and col not in frame.columns]
                if missing:
                    logger.warning(
                        "Skip %s due to missing columns: %s", file_path.name, ", ".join(missing)
                    )
                    continue
                figure = Figure(figsize=figure_size, tight_layout=True)
                FigureCanvasAgg(figure)
                axes = figure.add_subplot(111)
                self.chart_manager.plot(axes, frame, config)
                output_path = target_dir / f"{file_path.stem}.{fmt}"
                self.export_manager.export(figure, output_path, dpi=dpi, fmt=fmt)
                exported.append(output_path)
            except Exception:  # pragma: no cover - logged for operator
                logger.exception("Failed to render %s", file_path)
        return exported


__all__ = ["BatchPlotter"]
