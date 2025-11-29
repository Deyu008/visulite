"""Chart rendering utilities."""

from __future__ import annotations

import logging
from typing import Sequence, List

import matplotlib.pyplot as plt
import pandas as pd

from visulite.models.chart_config import ChartConfig

logger = logging.getLogger("visulite.chart_manager")

# Default color cycle for multiple lines
DEFAULT_COLORS: List[str] = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


class ChartManager:
    """Create matplotlib charts from pandas data."""

    SUPPORTED_TYPES = {"line", "bar", "scatter", "histogram", "boxplot", "heatmap"}

    def plot(
        self, 
        axes: plt.Axes, 
        frame: pd.DataFrame, 
        config: ChartConfig,
        theme: str = "default"
    ) -> None:
        if config.chart_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported chart type {config.chart_type}")
        if not config.x_column:
            raise ValueError("X column not selected")
        if not config.y_columns:
            raise ValueError("At least one Y column is required")

        logger.info("Rendering chart type=%s with theme=%s", config.chart_type, theme)
        
        # Apply theme
        if theme and theme != "default":
            try:
                plt.style.use(theme)
            except Exception:
                logger.warning("Theme '%s' not available, using default", theme)
                plt.style.use("default")
        else:
            plt.style.use("default")
        
        axes.clear()

        if config.chart_type == "histogram":
            self._plot_histogram(axes, frame, config)
        elif config.chart_type == "boxplot":
            self._plot_boxplot(axes, frame, config)
        elif config.chart_type == "heatmap":
            self._plot_heatmap(axes, frame, config)
        else:
            self._plot_xy(axes, frame, config)

        axes.set_title(config.title)
        axes.grid(config.show_grid)
        
        # Set axis labels
        if config.x_label:
            axes.set_xlabel(config.x_label)
        if config.y_label:
            axes.set_ylabel(config.y_label)
        
        if config.show_legend:
            axes.legend(loc="best")
        canvas = getattr(axes.figure, "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def _get_colors(self, config: ChartConfig, count: int) -> List[str]:
        """Get colors for the plot based on config."""
        if config.color_scheme == "auto":
            return [DEFAULT_COLORS[i % len(DEFAULT_COLORS)] for i in range(count)]
        else:
            # Use the same custom color for all lines
            return [config.color_scheme] * count

    def _plot_xy(self, axes: plt.Axes, frame: pd.DataFrame, config: ChartConfig) -> None:
        x_series = frame[config.x_column]
        colors = self._get_colors(config, len(config.y_columns))
        
        for i, column in enumerate(config.y_columns):
            y_series = frame[column]
            color = colors[i]
            marker = config.marker_style if config.marker_style else None
            
            if config.chart_type == "line":
                axes.plot(
                    x_series, y_series,
                    linestyle=config.line_style,
                    marker=marker,
                    color=color,
                    label=column
                )
            elif config.chart_type == "bar":
                axes.bar(x_series, y_series, label=column, alpha=0.7, color=color)
            elif config.chart_type == "scatter":
                scatter_marker = marker if marker else "o"
                axes.scatter(x_series, y_series, label=column, color=color, marker=scatter_marker)

    def _plot_histogram(self, axes: plt.Axes, frame: pd.DataFrame, config: ChartConfig) -> None:
        numeric_columns: Sequence[str] = [
            col for col in config.y_columns if pd.api.types.is_numeric_dtype(frame[col])
        ]
        if not numeric_columns:
            raise ValueError("Histogram requires numeric Y columns")
        
        colors = self._get_colors(config, len(numeric_columns))
        axes.hist(
            [frame[col].dropna() for col in numeric_columns],
            label=list(numeric_columns),
            bins=30,
            alpha=0.6,
            color=colors[:len(numeric_columns)],
        )

    def _plot_boxplot(self, axes: plt.Axes, frame: pd.DataFrame, config: ChartConfig) -> None:
        numeric_columns: Sequence[str] = [
            col for col in config.y_columns if pd.api.types.is_numeric_dtype(frame[col])
        ]
        if not numeric_columns:
            raise ValueError("Boxplot requires at least one numeric column")
        data = [frame[col].dropna() for col in numeric_columns]
        axes.boxplot(data, labels=list(numeric_columns), vert=True, patch_artist=True)

    def _plot_heatmap(self, axes: plt.Axes, frame: pd.DataFrame, config: ChartConfig) -> None:
        numeric_frame = frame[config.y_columns].select_dtypes(include="number")
        if numeric_frame.empty:
            raise ValueError("Heatmap requires numeric columns")
        corr = numeric_frame.corr()
        axes.clear()
        image = axes.imshow(corr, cmap="viridis", aspect="auto")
        axes.set_xticks(range(len(corr.columns)))
        axes.set_yticks(range(len(corr.index)))
        axes.set_xticklabels(corr.columns, rotation=45, ha="right")
        axes.set_yticklabels(corr.index)
        axes.figure.colorbar(image, ax=axes, fraction=0.046, pad=0.04)


__all__ = ["ChartManager"]
