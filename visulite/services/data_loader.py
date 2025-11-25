"""File loading utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, List

import pandas as pd

from visulite.models.app_state import DatasetMeta

logger = logging.getLogger("visulite.data_loader")


class UnsupportedFormatError(Exception):
    """Raised when the user selects an unsupported format."""


class DataLoader:
    """Load CSV/TSV/Excel/JSON files into pandas DataFrames."""

    SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".json"}
    # Common encodings to try in order
    ENCODINGS: List[str] = ["utf-8", "utf-8-sig", "gbk", "gb2312", "utf-16", "latin-1"]

    def _detect_encoding(self, file_path: Path) -> str:
        """Try multiple encodings and return the first one that works."""
        for encoding in self.ENCODINGS:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    f.read(8192)  # Read first 8KB to test
                logger.info("Detected encoding: %s", encoding)
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        # Fallback to utf-8 with error handling
        logger.warning("Could not detect encoding, falling back to utf-8 with errors='replace'")
        return "utf-8"

    def load(self, file_path: Path) -> Tuple[pd.DataFrame, DatasetMeta]:
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFormatError(f"Unsupported file format: {suffix}")

        logger.info("Loading data file %s", file_path)
        
        if suffix == ".csv":
            encoding = self._detect_encoding(file_path)
            try:
                frame = pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                frame = pd.read_csv(file_path, encoding="utf-8", errors="replace")
        elif suffix == ".tsv":
            encoding = self._detect_encoding(file_path)
            try:
                frame = pd.read_csv(file_path, sep="\t", encoding=encoding)
            except UnicodeDecodeError:
                frame = pd.read_csv(file_path, sep="\t", encoding="utf-8", errors="replace")
        elif suffix in {".xlsx", ".xls"}:
            frame = pd.read_excel(file_path)
        else:  # json
            encoding = self._detect_encoding(file_path)
            try:
                frame = pd.read_json(file_path, encoding=encoding)
            except UnicodeDecodeError:
                frame = pd.read_json(file_path, encoding="utf-8")

        meta = DatasetMeta(
            path=file_path,
            rows=len(frame.index),
            columns=len(frame.columns),
            column_types=[f"{col}: {dtype}" for col, dtype in frame.dtypes.items()],
            missing_summary=self._missing_summary(frame),
        )
        logger.info("Loaded dataset rows=%s cols=%s", meta.rows, meta.columns)
        return frame, meta

    @staticmethod
    def _missing_summary(frame: pd.DataFrame) -> list[str]:
        missing = frame.isna().sum()
        summary: list[str] = []
        for column, count in missing.items():
            if count > 0:
                summary.append(f"{column}: {count}")
        return summary


__all__ = ["DataLoader", "UnsupportedFormatError"]
