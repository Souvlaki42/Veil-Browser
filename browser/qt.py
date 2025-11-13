from collections.abc import Callable
from typing import Any, TypeAlias
from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtGui import QAction, QColor, QIcon, QPalette
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QToolButton, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from browser.utils import (
    get_icon_font,
    Config,
    setup_logging,
)

WebView: TypeAlias = QWebEngineView
WebPage: TypeAlias = QWebEnginePage
WebAction: TypeAlias = WebPage.WebAction


class ToolButton(QToolButton):
    def __init__(
        self,
        on_click: Callable[..., Any] | pyqtBoundSignal | QAction | None = lambda: None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("QToolButton { padding: 5px; background: transparent; }")

        if not on_click:
            return
        elif isinstance(on_click, QAction):
            self.clicked.connect(on_click.trigger)
        else:
            self.clicked.connect(on_click)

    def update_icon(
        self, icon_text: str, theme_icon: QIcon.ThemeIcon, is_dark: bool | None = True
    ) -> None:
        logger = setup_logging()
        config = Config.load()
        icon = QIcon.fromTheme(theme_icon)

        try:
            if config.icon_theme == "system":
                self.setIcon(icon)
                return
            elif config.icon_theme == "automatic":
                color = QColor("white") if is_dark else QColor("#333333")
            else:
                color = QColor(config.icon_theme)

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
