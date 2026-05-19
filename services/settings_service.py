import json
import os
import sys
from pathlib import Path


class SettingsService:
    def __init__(self) -> None:
        app_data = os.getenv("APPDATA")
        base_dir = Path(app_data) if app_data else Path.home()
        self.settings_dir = base_dir / "WagonWMS"
        self.settings_path = self.settings_dir / "settings.json"
        self.settings_dir.mkdir(parents=True, exist_ok=True)

    def get_reports_dir(self) -> Path:
        settings = self._load()
        reports_dir = settings.get("reports_dir")
        if reports_dir:
            path = Path(reports_dir)
        else:
            path = self._default_reports_dir()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def set_reports_dir(self, path: str | Path) -> Path:
        reports_dir = Path(path)
        reports_dir.mkdir(parents=True, exist_ok=True)
        settings = self._load()
        settings["reports_dir"] = str(reports_dir)
        self._save(settings)
        return reports_dir

    def reset_reports_dir(self) -> Path:
        settings = self._load()
        settings.pop("reports_dir", None)
        self._save(settings)
        return self.get_reports_dir()

    def _default_reports_dir(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / "reports"
        return Path(__file__).resolve().parent.parent / "reports"

    def _load(self) -> dict[str, str]:
        if not self.settings_path.exists():
            return {}
        try:
            return json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, settings: dict[str, str]) -> None:
        self.settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


settings_service = SettingsService()
