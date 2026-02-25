"""Regression tests.

This project uses the stdlib `unittest` runner. Keep this file free of
pytest-only fixtures so `python -m unittest discover` works in a minimal
environment.
"""

from __future__ import annotations

import builtins
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import matplotlib
import pandas as pd


# Ensure a headless backend before importing pyplot-based modules.
matplotlib.use("Agg")

from visulite.models.chart_config import ChartConfig  # noqa: E402
from visulite.services.chart_manager import ChartManager  # noqa: E402
from visulite.services.data_loader import DataLoader  # noqa: E402
from visulite.services.data_processor import DataProcessor, FilterCriteria  # noqa: E402


class RegressionTests(unittest.TestCase):
    def test_histogram_does_not_require_x_column(self) -> None:
        frame = pd.DataFrame({"values": [1, 2, 3, 4, 5]})
        config = ChartConfig(
            x_column=None,
            y_columns=["values"],
            chart_type="histogram",
        )
        manager = ChartManager()
        fig = matplotlib.figure.Figure()
        ax = fig.add_subplot(111)

        # Should not raise.
        manager.plot(ax, frame, config)

    def test_text_filter_uses_literal_match(self) -> None:
        frame = pd.DataFrame({"text": ["foo.*bar", "foo123bar", "baz"]})
        criteria = FilterCriteria(text_filters={"text": "foo.*bar"})
        processor = DataProcessor()

        filtered = processor.apply_filters(frame, criteria)

        self.assertEqual(filtered["text"].tolist(), ["foo.*bar"])

    def test_encoding_detection_cache_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "sample.csv"
            data_file.write_text("a,b\n1,2\n", encoding="utf-8")

            loader = DataLoader()
            open_calls: list[str] = []
            original_open = builtins.open

            def counting_open(*args, **kwargs):
                open_calls.append(str(args[0]))
                return original_open(*args, **kwargs)

            with mock.patch.object(builtins, "open", counting_open):
                first = loader._detect_encoding(data_file)
                second = loader._detect_encoding(data_file)

            self.assertEqual(first, "utf-8")
            self.assertEqual(second, "utf-8")
            self.assertEqual(len(open_calls), 1)


if __name__ == "__main__":
    unittest.main()

