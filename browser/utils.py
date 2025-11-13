from bisect import bisect_left
import logging
import json
from functools import cache
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, List, Literal
from dataclasses import asdict, dataclass, field

from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget


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


KeybindingsType = Literal[
    "new_tab",
    "close_tab",
    "next_tab",
    "prev_tab",
    "prev_page",
    "next_page",
    "refresh",
    "address_focus",
    "devtools",
    "page_source",
    "print_page",
    "save_as",
    "copy_address",
    "duplicate_tab",
    "reset_zoom",
    "increase_zoom",
    "decrease_zoom",
    "open_config",
    # TODO: find a way to make this work: "reload_config",
]


@dataclass
class Keybindings:
    new_tab: list[str] = field(default_factory=lambda: ["Ctrl+T"])
    close_tab: list[str] = field(default_factory=lambda: ["Ctrl+W"])
    next_tab: list[str] = field(default_factory=lambda: ["Ctrl+Tab"])
    prev_tab: list[str] = field(default_factory=lambda: ["Ctrl+Shift+Tab"])
    prev_page: list[str] = field(default_factory=lambda: ["Alt+Left", "Alt+Backspace"])
    next_page: list[str] = field(
        default_factory=lambda: ["Alt+Right", "Alt+Shift+Backspace"]
    )
    refresh: list[str] = field(default_factory=lambda: ["F5", "Ctrl+R"])
    address_focus: list[str] = field(default_factory=lambda: ["Ctrl+L"])
    devtools: list[str] = field(default_factory=lambda: ["F12", "Ctrl+Shift+I"])
    page_source: list[str] = field(default_factory=lambda: ["Ctrl+U"])
    print_page: list[str] = field(default_factory=lambda: ["Ctrl+P"])
    save_as: list[str] = field(default_factory=lambda: ["Ctrl+S"])
    copy_address: list[str] = field(default_factory=lambda: ["Ctrl+Shift+C"])
    duplicate_tab: list[str] = field(default_factory=lambda: ["Ctrl+D"])
    reset_zoom: list[str] = field(default_factory=lambda: ["Ctrl+0"])
    increase_zoom: list[str] = field(default_factory=lambda: ["Ctrl+="])
    decrease_zoom: list[str] = field(default_factory=lambda: ["Ctrl+-"])
    open_config: list[str] = field(default_factory=lambda: ["Ctrl+,"])
    reload_config: list[str] = field(default_factory=lambda: ["Ctrl+Shift+,"])

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

    def sequences(self, name: KeybindingsType) -> list[QKeySequence]:
        sequences: list[QKeySequence] = []
        keybinds: set[str] = self.__getattribute__(name)
        for keybind in keybinds:
            sequences.append(QKeySequence(keybind))
        return sequences

    def bind_shortcuts(
        self,
        name: KeybindingsType,
        action: Callable[..., Any] | pyqtBoundSignal | QAction | None = lambda: None,
        parent: QWidget | None = None,
    ) -> None:
        sequences = self.sequences(name)
        for sequence in sequences:
            shortcut = QShortcut(sequence, parent)
            if not action:
                return
            elif isinstance(action, QAction):
                shortcut.activated.connect(action.trigger)
            else:
                shortcut.activated.connect(action)


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


def open_in_default_editor(filepath: str | Path):
    filepath = str(Path(filepath).resolve())

    if sys.platform == "darwin":
        subprocess.run(["open", filepath], check=True)
    elif sys.platform == "win32":
        subprocess.run(["cmd", "/c", "start", "", filepath], check=True)
    else:
        subprocess.run(["xdg-open", filepath], check=True)


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
