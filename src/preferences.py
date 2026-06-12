import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths


APP_DIR_NAME = "StarCitizenMiningOverlay"
PREFERENCES_FILE_NAME = "preferences.json"


def preferences_path() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base:
        base = str(Path.home() / "AppData" / "Roaming" / APP_DIR_NAME)
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path / PREFERENCES_FILE_NAME


def load_preferences(default_minerals: list[str]) -> dict:
    path = preferences_path()
    if not path.exists():
        return {
            "selected_minerals": default_minerals,
            "overlay_visible": False,
            "click_through": False,
            "overlay_position": None,
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "selected_minerals": default_minerals,
            "overlay_visible": False,
            "click_through": False,
            "overlay_position": None,
        }

    return {
        "selected_minerals": data.get("selected_minerals", default_minerals),
        "overlay_visible": bool(data.get("overlay_visible", False)),
        "click_through": bool(data.get("click_through", False)),
        "overlay_position": data.get("overlay_position"),
    }


def save_preferences(
    selected_minerals: list[str],
    overlay_visible: bool,
    click_through: bool,
    overlay_position: tuple[int, int] | None,
) -> None:
    data = {
        "selected_minerals": selected_minerals,
        "overlay_visible": overlay_visible,
        "click_through": click_through,
        "overlay_position": list(overlay_position) if overlay_position else None,
    }
    preferences_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
