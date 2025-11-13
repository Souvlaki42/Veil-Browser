from bisect import bisect_left
import logging
import json
from functools import cache
from pathlib import Path
from typing import List, Literal
from dataclasses import asdict, dataclass

from PyQt6.QtGui import QFont, QFontDatabase


@dataclass
class Config:
    local_version: str = "2.0.0"
    homepage: str = "https://google.com"
    search_engine: str = "https://google.com/search?q=%s"
    stdout_log: bool = True
    icon_theme: Literal["automatic", "system"] | str = "automatic"
    close_after_last_tab: bool = False
    zoom_level: int = 100

    @classmethod
    @cache
    def load(cls):
        root_dir = Path(__file__).parent.parent
        data_dir = root_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        config_file = data_dir / "config.json"

        if config_file.exists():
            with open(config_file, "r") as f:
                user_config = json.load(f)
                config = cls(**user_config)
        else:
            config = cls()

        with open(config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)

        return config

    @classmethod
    def reload(cls):
        cls.load.cache_clear()
        return cls.load()


@dataclass
class Keybindings:
    new_tab: str = "Ctrl+T"
    close_tab: str = "Ctrl+W"
    next_tab: str = "Ctrl+Tab"
    prev_tab: str = "Ctrl+Shift+Tab"
    refresh_1: str = "F5"
    refresh_2: str = "Ctrl+R"
    address_focus: str = "Ctrl+L"
    devtools_1: str = "F12"
    devtools_2: str = "Ctrl+Shift+I"
    page_source: str = "Ctrl+U"
    print_page: str = "Ctrl+P"
    save_as: str = "Ctrl+S"
    copy_address: str = "Ctrl+Shift+C"
    duplicate_tab: str = "Ctrl+D"
    reset_zoom: str = "Ctrl+0"
    increase_zoom: str = "Ctrl+="
    decrease_zoom: str = "Ctrl+-"
    open_config: str = "Ctrl+,"
    reload_config: str = "Ctrl+Shift+,"

    @classmethod
    @cache
    def load(cls):
        root_dir = Path(__file__).parent.parent
        data_dir = root_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        keybinds_file = data_dir / "keybinds.json"

        if keybinds_file.exists():
            with open(keybinds_file, "r") as f:
                user_keybinds = json.load(f)
                keybinds = cls(**user_keybinds)
        else:
            keybinds = cls()

        with open(keybinds_file, "w") as f:
            json.dump(asdict(keybinds), f, indent=2)

        return keybinds

    @classmethod
    def reload(cls):
        cls.load.cache_clear()
        return cls.load()


@cache
def setup_logging():
    """Configure logging system"""
    config = Config.load()

    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "veil_browser.log"

    handlers: list[logging.Handler] = [logging.FileHandler(log_file, encoding="utf-8")]

    if config.stdout_log:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    return logging.getLogger(__name__)


@cache
def get_icon_font():
    """Configure fonts for icons"""
    logger = setup_logging()
    font_path = Path(__file__).parent / "icons.ttf"
    font_id = QFontDatabase.addApplicationFont(str(font_path))
    if font_id == -1:
        logger.warning("Font file was not available!")
        return
    families = QFontDatabase.applicationFontFamilies(font_id)
    font = QFont(families[0])
    font.setPixelSize(16)
    return font


class StepCycler:
    def __init__(self, steps: List[int], initial_value: int | None = None):
        self.steps = sorted(steps)

        if initial_value is not None:
            self.current_index = self._find_closest_index(initial_value)
        else:
            self.current_index = 0

        self.initial_index = self.current_index

    def _find_closest_index(self, value: int) -> int:
        pos = bisect_left(self.steps, value)

        if pos == 0:
            return 0
        if pos == len(self.steps):
            return len(self.steps) - 1

        before = self.steps[pos - 1]
        after = self.steps[pos]

        if after - value < value - before:
            return pos
        else:
            return pos - 1

    def up(self) -> int:
        self.current_index = min(self.current_index + 1, len(self.steps) - 1)
        return self.steps[self.current_index]

    def down(self) -> int:
        self.current_index = max(self.current_index - 1, 0)
        return self.steps[self.current_index]

    def current(self) -> int:
        return self.steps[self.current_index]

    def reset(self) -> int:
        self.current_index = self.initial_index
        return self.steps[self.current_index]
