from collections.abc import Callable
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QToolButton, QWidget

from browser.data import get_icon_font, read_config, setup_logging


class ToolButton(QToolButton):
    def __init__(
        self, on_click: Callable[[], None] = lambda: None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("QToolButton { padding: 5px; background: transparent; }")
        _ = self.clicked.connect(on_click)

    def update_icon(
        self, icon_text: str, theme_icon: QIcon.ThemeIcon, is_dark: bool | None = True
    ) -> None:
        logger = setup_logging()
        config = read_config()
        icon = QIcon.fromTheme(theme_icon)

        try:
            if config["icon_theme"] == "system":
                self.setIcon(icon)
                return
            elif config["icon_theme"] == "automatic":
                color = QColor("white") if is_dark else QColor("#333333")
            else:
                color = QColor(config["icon_theme"])

            palette = self.palette()
            icon_font = get_icon_font()
            palette.setColor(QPalette.ColorRole.ButtonText, color)
            self.setPalette(palette)
            if icon_font:
                self.setFont(icon_font)
                self.setText(icon_text)
            else:
                self.setIcon(icon)
        except Exception as e:
            logger.warning(f"[ICON FAILURE] {e}")
