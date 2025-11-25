"""Simple JSON based persistence for app preferences."""

from __future__ import annotations

import json
from pathlib import Path

from visulite.models.chart_config import ChartConfig


class ConfigManager:
    """Read and write chart configurations."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path.home() / ".visulite"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.base_dir / "chart_config.json"

    def save_chart_config(self, config: ChartConfig) -> Path:
        with self.config_path.open("w", encoding="utf-8") as fh:
            json.dump(config.to_dict(), fh, indent=2, ensure_ascii=False)
        return self.config_path

    def load_chart_config(self) -> ChartConfig | None:
        if not self.config_path.exists():
            return None
        with self.config_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return ChartConfig(**data)


__all__ = ["ConfigManager"]
