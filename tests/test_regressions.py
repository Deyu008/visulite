import builtins
import importlib.util
import sys
import types
from pathlib import Path

import matplotlib
import pandas as pd
import pytest


matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


visulite_pkg = types.ModuleType("visulite")
visulite_models_pkg = types.ModuleType("visulite.models")
visulite_services_pkg = types.ModuleType("visulite.services")

sys.modules["visulite"] = visulite_pkg
sys.modules["visulite.models"] = visulite_models_pkg
sys.modules["visulite.services"] = visulite_services_pkg

chart_config = _load_module(
    "visulite.models.chart_config", "visulite/models/chart_config.py"
)
app_state = _load_module("visulite.models.app_state", "visulite/models/app_state.py")
chart_manager = _load_module(
    "visulite.services.chart_manager", "visulite/services/chart_manager.py"
)
data_loader = _load_module(
    "visulite.services.data_loader", "visulite/services/data_loader.py"
)
data_processor = _load_module(
    "visulite.services.data_processor", "visulite/services/data_processor.py"
)

ChartConfig = chart_config.ChartConfig
ChartManager = chart_manager.ChartManager
DataLoader = data_loader.DataLoader
DataProcessor = data_processor.DataProcessor
FilterCriteria = data_processor.FilterCriteria


def test_histogram_does_not_require_x_column():
    frame = pd.DataFrame({"values": [1, 2, 3, 4, 5]})
    config = ChartConfig(
        x_column=None,
        y_columns=["values"],
        chart_type="histogram",
    )
    manager = ChartManager()
    fig = matplotlib.figure.Figure()
    ax = fig.add_subplot(111)

    manager.plot(ax, frame, config)


def test_text_filter_uses_literal_match():
    frame = pd.DataFrame({"text": ["foo.*bar", "foo123bar", "baz"]})
    criteria = FilterCriteria(text_filters={"text": "foo.*bar"})
    processor = DataProcessor()

    filtered = processor.apply_filters(frame, criteria)

    assert filtered["text"].tolist() == ["foo.*bar"]


def test_encoding_detection_cache_hits(tmp_path, monkeypatch):
    data_file = tmp_path / "sample.csv"
    data_file.write_text("a,b\n1,2\n", encoding="utf-8")

    loader = DataLoader()
    open_calls = []
    original_open = builtins.open

    def counting_open(*args, **kwargs):
        open_calls.append(args[0])
        return original_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", counting_open)

    first = loader._detect_encoding(data_file)
    second = loader._detect_encoding(data_file)

    assert first == "utf-8"
    assert second == "utf-8"
    assert len(open_calls) == 1
