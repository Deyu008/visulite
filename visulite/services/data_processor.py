"""Data preprocessing utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Optional

import pandas as pd

logger = logging.getLogger("visulite.data_processor")


@dataclass
class FilterCriteria:
    text_filters: Dict[str, str] | None = None
    numeric_ranges: Dict[str, tuple[float | None, float | None]] | None = None
    dropna_columns: Iterable[str] | None = None


class DataProcessor:
    """Applies simple preprocessing steps to pandas DataFrames."""

    def apply_filters(self, frame: pd.DataFrame, criteria: FilterCriteria) -> pd.DataFrame:
        logger.info("Applying filters to dataframe")
        result = frame.copy()
        if criteria.text_filters:
            for column, keyword in criteria.text_filters.items():
                if column in result.columns and keyword:
                    mask = result[column].astype(str).str.contains(keyword, case=False, na=False)
                    result = result[mask]

        if criteria.numeric_ranges:
            for column, (min_v, max_v) in criteria.numeric_ranges.items():
                if column in result.columns:
                    series = pd.to_numeric(result[column], errors="coerce")
                    if min_v is not None:
                        result = result[series >= min_v]
                    if max_v is not None:
                        result = result[series <= max_v]

        if criteria.dropna_columns:
            result = result.dropna(subset=list(criteria.dropna_columns))

        return result

    def fill_missing(self, frame: pd.DataFrame, method: str = "mean") -> pd.DataFrame:
        strategy_map = {
            "zero": 0,
            "mean": frame.mean(numeric_only=True),
            "median": frame.median(numeric_only=True),
            "ffill": "ffill",
            "bfill": "bfill",
        }
        strategy = strategy_map.get(method, frame.mean(numeric_only=True))
        if strategy in {"ffill", "bfill"}:
            return frame.fillna(method=strategy)  # type: ignore[arg-type]
        return frame.fillna(strategy)

    def convert_column_type(
        self, frame: pd.DataFrame, column: str, target_type: str
    ) -> pd.DataFrame:
        """Convert a column to a specified type.
        
        Args:
            frame: The DataFrame to modify
            column: The column name to convert
            target_type: One of 'string', 'int', 'float', 'datetime'
            
        Returns:
            A new DataFrame with the converted column
        """
        if column not in frame.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        result = frame.copy()
        logger.info("Converting column '%s' to type '%s'", column, target_type)
        
        if target_type == "string":
            result[column] = result[column].astype(str)
        elif target_type == "int":
            result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)
        elif target_type == "float":
            result[column] = pd.to_numeric(result[column], errors="coerce")
        elif target_type == "datetime":
            result[column] = pd.to_datetime(result[column], errors="coerce")
        else:
            raise ValueError(f"Unsupported target type: {target_type}")
        
        return result

    def slice_rows(
        self,
        frame: pd.DataFrame,
        start_row: Optional[int] = None,
        end_row: Optional[int] = None,
        head_n: Optional[int] = None,
    ) -> pd.DataFrame:
        """Slice rows from the DataFrame.
        
        Args:
            frame: The DataFrame to slice
            start_row: Start index (0-based, inclusive)
            end_row: End index (0-based, exclusive)
            head_n: If provided, return only first N rows (takes precedence)
            
        Returns:
            A sliced DataFrame
        """
        if head_n is not None and head_n > 0:
            logger.info("Taking first %d rows", head_n)
            return frame.head(head_n)
        
        if start_row is not None or end_row is not None:
            start = start_row if start_row is not None else 0
            end = end_row if end_row is not None else len(frame)
            logger.info("Slicing rows from %d to %d", start, end)
            return frame.iloc[start:end].reset_index(drop=True)
        
        return frame

    def select_columns(self, frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Select specific columns from the DataFrame.
        
        Args:
            frame: The DataFrame to select from
            columns: List of column names to keep
            
        Returns:
            A DataFrame with only the selected columns
        """
        missing = [col for col in columns if col not in frame.columns]
        if missing:
            raise ValueError(f"Columns not found: {', '.join(missing)}")
        
        logger.info("Selecting columns: %s", ", ".join(columns))
        return frame[columns].copy()


__all__ = ["DataProcessor", "FilterCriteria"]
