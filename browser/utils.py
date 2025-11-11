from bisect import bisect_left
import os
import logging
import json
from functools import cache
from pathlib import Path
from typing import List

from PyQt6.QtGui import QFont, QFontDatabase


def deep_merge(default: dict, user: dict) -> dict:
    """Merge user config with default config, adding missing keys"""
    result = default.copy()

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


@cache
def read_config():
    """Read the configuration file"""
    root_dir = Path(__file__).parent.parent
    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    config_file = os.path.join(data_dir, "config.json")
    default_config_file = os.path.join(root_dir, "browser/default_config.json")

    with open(default_config_file, "r") as f:
        default_config = json.load(f)

    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(config_file, "r") as f:
        user_config = json.load(f)

    merged_config = deep_merge(default_config, user_config)

    with open(config_file, "w") as f:
        json.dump(merged_config, f, indent=2)

    merged_config["remote_version"] = default_config["local_version"]

    return merged_config


@cache
def setup_logging():
    """Configure logging system"""
    config = read_config()

    root_dir = Path(__file__).parent.parent
    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    log_dir = os.path.join(data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "veil_browser.log")

    handlers: list[logging.Handler] = [logging.FileHandler(log_file, encoding="utf-8")]

    if config["stdout_log"]:
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
    font_path = os.path.join(Path(__file__).parent, "icons.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
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
