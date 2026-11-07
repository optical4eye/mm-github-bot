import json
import os
import tempfile
from pathlib import Path


class State:
    def __init__(self, path: str):
        self.path = Path(path)
        self._data = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, repo_key: str):
        return self._data.get(repo_key)

    def set(self, repo_key: str, version: str):
        self._data[repo_key] = version
        self._save()

    def _save(self):
        # Atomic write via temp file + rename
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent, delete=False, suffix=".tmp"
        ) as tmp:
            json.dump(self._data, tmp, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp.name)
        tmp_path.replace(self.path)