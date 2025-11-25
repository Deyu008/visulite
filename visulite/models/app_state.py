"""Central state container for the UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .chart_config import ChartConfig


@dataclass
class DatasetMeta:
    """Lightweight description of the current dataset."""

    path: Optional[Path] = None
    rows: int = 0
    columns: int = 0
    column_types: List[str] = field(default_factory=list)
    missing_summary: List[str] = field(default_factory=list)


@dataclass
class AppState:
    """Holds the loaded dataframe and chart configuration."""

    data_frame: pd.DataFrame | None = None
    original_frame: pd.DataFrame | None = None
    dataset_meta: DatasetMeta = field(default_factory=DatasetMeta)
    chart_config: ChartConfig = field(default_factory=ChartConfig)

    def has_data(self) -> bool:
        return self.data_frame is not None and not self.data_frame.empty

    def set_dataset(self, frame: pd.DataFrame, meta: DatasetMeta) -> None:
        """Store a fresh dataset and reset processing state."""
        self.original_frame = frame.copy()
        self.data_frame = frame
        self.dataset_meta = meta

    def reset_view(self) -> pd.DataFrame | None:
        """Revert to the original dataframe."""
        if self.original_frame is None:
            return None
        self.data_frame = self.original_frame.copy()
        return self.data_frame

    def update_view(self, frame: pd.DataFrame) -> None:
        """Persist the current working dataframe."""
        self.data_frame = frame


__all__ = ["AppState", "DatasetMeta"]
