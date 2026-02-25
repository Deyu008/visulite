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
    history_limit: int = 30
    _undo_stack: list[pd.DataFrame] = field(default_factory=list, init=False, repr=False)
    _redo_stack: list[pd.DataFrame] = field(default_factory=list, init=False, repr=False)

    def has_data(self) -> bool:
        return self.data_frame is not None and not self.data_frame.empty

    def set_dataset(self, frame: pd.DataFrame, meta: DatasetMeta) -> None:
        """Store a fresh dataset and reset processing state."""
        self.original_frame = frame.copy(deep=True)
        self.data_frame = frame.copy(deep=True)
        self.dataset_meta = meta
        self.clear_history()

    def reset_view(self) -> pd.DataFrame | None:
        """Revert to the original dataframe."""
        if self.original_frame is None:
            return None
        self.data_frame = self.original_frame.copy(deep=True)
        return self.data_frame

    def update_view(self, frame: pd.DataFrame) -> None:
        """Persist the current working dataframe."""
        self.data_frame = frame.copy(deep=True)

    def clear_history(self) -> None:
        """Reset all undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self._undo_stack) and self.data_frame is not None

    def can_redo(self) -> bool:
        return bool(self._redo_stack) and self.data_frame is not None

    def push_history(self, frame_before: pd.DataFrame | None) -> None:
        """Store a snapshot before a mutating operation."""
        if frame_before is None:
            return
        self._undo_stack.append(frame_before.copy(deep=True))
        if len(self._undo_stack) > self.history_limit:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> pd.DataFrame | None:
        """Revert to the previous dataframe snapshot."""
        if not self.can_undo() or self.data_frame is None:
            return None
        self._redo_stack.append(self.data_frame.copy(deep=True))
        if len(self._redo_stack) > self.history_limit:
            self._redo_stack.pop(0)
        previous = self._undo_stack.pop()
        self.data_frame = previous.copy(deep=True)
        return self.data_frame

    def redo(self) -> pd.DataFrame | None:
        """Restore a dataframe snapshot from the redo stack."""
        if not self.can_redo() or self.data_frame is None:
            return None
        self._undo_stack.append(self.data_frame.copy(deep=True))
        if len(self._undo_stack) > self.history_limit:
            self._undo_stack.pop(0)
        restored = self._redo_stack.pop()
        self.data_frame = restored.copy(deep=True)
        return self.data_frame


__all__ = ["AppState", "DatasetMeta"]
