"""Manage recently opened dataset paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class RecentFilesManager:
    """Store up to ``limit`` recently opened files on disk."""

    def __init__(self, base_dir: Path | None = None, limit: int = 5) -> None:
        self.base_dir = base_dir or Path.home() / ".visulite"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / "recent_files.json"
        self.limit = limit

    def get_recent(self) -> List[Path]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return [Path(p) for p in data if isinstance(p, str)]

    def add_file(self, file_path: Path) -> None:
        file_path = file_path.resolve()
        entries = [p for p in self.get_recent() if p != file_path]
        entries.insert(0, file_path)
        del entries[self.limit :]
        self._write(entries)

    def clear(self) -> None:
        self._write([])

    def _write(self, entries: List[Path]) -> None:
        payload = [str(p) for p in entries]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


__all__ = ["RecentFilesManager"]
