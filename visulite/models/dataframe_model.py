"""Qt table model backed by a pandas DataFrame."""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
import pandas as pd


class DataFrameModel(QAbstractTableModel):
    """Expose pandas frames to Qt's model/view framework."""

    def __init__(self, frame: pd.DataFrame | None = None) -> None:
        super().__init__()
        self._frame = frame if frame is not None else pd.DataFrame()

    def update_frame(self, frame: pd.DataFrame) -> None:
        self.beginResetModel()
        self._frame = frame
        self.endResetModel()

    # Qt overrides
    def flags(self, index: QModelIndex):  # noqa: N802
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else len(self._frame.index)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else len(self._frame.columns)

    def data(  # noqa: N802
        self, index: QModelIndex, role: int = Qt.DisplayRole
    ) -> str | None:
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        value = self._frame.iat[index.row(), index.column()]
        return "" if pd.isna(value) else str(value)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return (
                str(self._frame.columns[section])
                if section < len(self._frame.columns)
                else ""
            )
        return str(self._frame.index[section])

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # noqa: N802
        if self._frame.empty or column < 0 or column >= len(self._frame.columns):
            return
        col_name = self._frame.columns[column]
        series = pd.to_numeric(self._frame[col_name], errors="coerce")
        if series.notna().any():
            sort_key = series
        else:
            sort_key = self._frame[col_name].astype(str)

        ascending = order == Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._frame = (
            self._frame.assign(__sort_key=sort_key)
            .sort_values(by="__sort_key", ascending=ascending, kind="mergesort")
            .drop(columns="__sort_key")
            .reset_index(drop=True)
        )
        self.layoutChanged.emit()


__all__ = ["DataFrameModel"]
