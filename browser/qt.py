from collections.abc import Callable
from PyQt6.QtGui import QColor, QContextMenuEvent, QIcon, QPalette
from PyQt6.QtWidgets import QToolButton, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from browser.utils import get_icon_font, read_config, setup_logging


class ToolButton(QToolButton):
    def __init__(
        self,
        on_click: Callable[[], QWebEngineView | None] = lambda: None,
        parent: QWidget | None = None,
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


class WebView(QWebEngineView):
    def __init__(self, parent: QWidget | None = None) -> None:
        return super().__init__(parent)

    def contextMenuEvent(self, a0: QContextMenuEvent | None) -> None:
        if not a0:
            return

        page = self.page()
        if not page:
            return super().contextMenuEvent(a0)

        self.menu = self.createStandardContextMenu()
        if not self.menu:
            return super().contextMenuEvent(a0)

        actions = self.menu.actions()
        for action in actions:
            pass

        self.menu.popup(a0.globalPos())
