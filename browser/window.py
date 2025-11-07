from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QPoint, QUrl, Qt
from PyQt6.QtGui import QIcon

from browser.data import read_config, setup_logging
from browser.qt import ToolButton

logger = setup_logging()


class VeilBrowser(QMainWindow):
    """Main browser window class"""

    def __init__(self):
        super().__init__()
        self.config = read_config()
        self.init_window()
        self.init_ui()

    def init_window(self):
        self.setMouseTracking(True)
        self._drag_position: QPoint = QPoint()
        self.resize(1200, 800)

        instance = QApplication.instance()
        if not instance or not isinstance(instance, QApplication):
            logger.fatal("Application window not found!")
            return

        self.instance = instance

    def init_ui(self):
        main_widget = QWidget()

        # Web view
        self.web_view: QWebEngineView = QWebEngineView()
        self.web_view.setUrl(QUrl(self.config["homepage"]))
        self.web_view.urlChanged.connect(self.update_url)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Navigation bar
        nav_bar = QHBoxLayout()
        self.back_btn = ToolButton(self.web_view.back)
        self.forward_btn = ToolButton(self.web_view.forward)
        self.refresh_btn = ToolButton(self.web_view.reload)
        self.home_btn = ToolButton(
            lambda: self.navigate(self.config["homepage"]),
        )

        self.address_bar: QLineEdit = QLineEdit()
        self.address_bar.returnPressed.connect(lambda: self.navigate(None))

        # Icons
        style_hints = self.instance.styleHints()
        if style_hints:
            style_hints.colorSchemeChanged.connect(
                lambda: self._update_icon_colors(style_hints.colorScheme())
            )
            self._update_icon_colors(style_hints.colorScheme())
        else:
            logger.warning("Style hints are not available!")

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.refresh_btn)
        nav_bar.addWidget(self.home_btn)
        nav_bar.addWidget(self.address_bar)

        layout.addLayout(nav_bar)
        layout.addWidget(self.web_view)

        self.setCentralWidget(main_widget)

    def _update_icon_colors(self, color_scheme: Qt.ColorScheme | None):
        is_dark: bool = color_scheme == Qt.ColorScheme.Dark
        self.back_btn.update_icon("arrow_back", QIcon.ThemeIcon.GoPrevious, is_dark)
        self.forward_btn.update_icon("arrow_forward", QIcon.ThemeIcon.GoNext, is_dark)
        self.refresh_btn.update_icon("refresh", QIcon.ThemeIcon.ViewRefresh, is_dark)
        self.home_btn.update_icon("home", QIcon.ThemeIcon.GoHome, is_dark)

    def navigate(self, input: str | None):
        text = input or self.address_bar.text()

        # Try parsing as URL
        url = QUrl(text)

        if not url.scheme():
            if "." in text and " " not in text:
                url = QUrl("https://" + text)
            else:
                # Search query
                search_url = str(self.config["search_engine"]).replace("%s", text)
                url = QUrl(search_url)

        self.web_view.setUrl(url)

    def update_url(self, url: QUrl):
        self.address_bar.setText(url.toString())
