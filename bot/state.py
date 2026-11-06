import json
import os


class State:
    def __init__(self, path: str):
        self.path = path
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

    def get(self, repo_key: str):
        return self._data.get(repo_key)

    def set(self, repo_key: str, version: str):
        self._data[repo_key] = version
        self._save()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
