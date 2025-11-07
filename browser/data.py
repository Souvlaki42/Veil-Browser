import os
import logging
import shutil
import json
from functools import cache
from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase


@cache
def read_config():
    """Read the configuration file"""

    root_dir = Path(__file__).parent.parent
    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    config_file = os.path.join(data_dir, "config.json")

    if not os.path.exists(config_file):
        _ = shutil.copyfile(
            os.path.join(root_dir, "browser/default_config.json"),
            config_file,
            follow_symlinks=True,
        )

    with open(config_file, "r") as f:
        return json.load(f)


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
