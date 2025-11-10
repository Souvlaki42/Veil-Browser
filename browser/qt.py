from collections.abc import Callable
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QToolButton, QWidget, QTabWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal

from browser.data import get_icon_font, read_config, setup_logging


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


class TabWidget(QTabWidget):
    """Custom tab widget for handling multiple browser tabs"""

    # Signal emitted when the current URL changes
    current_url_changed = pyqtSignal(QUrl)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = read_config()
        self.logger = setup_logging()

        # Configure tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)

        # Create initial tab
        self.create_new_tab()

    def create_new_tab(self, url: str | None = None) -> QWebEngineView:
        """Create a new tab with a web view"""
        web_view = QWebEngineView()

        # Set URL or homepage
        if url:
            web_view.setUrl(QUrl(url))
        else:
            web_view.setUrl(QUrl(self.config["homepage"]))

        # Connect signals
        web_view.titleChanged.connect(
            lambda title: self._update_tab_title(web_view, title)
        )
        web_view.urlChanged.connect(self._on_url_changed)
        web_view.loadStarted.connect(
            lambda: self._update_tab_title(web_view, "Loading...")
        )

        # Add tab
        tab_index = self.addTab(web_view, "New Tab")
        self.setCurrentIndex(tab_index)

        # Add "+" button for new tab if this is the only tab
        if self.count() == 1:
            self._add_new_tab_button()

        return web_view

    def close_tab(self, index: int) -> None:
        """Close a tab at the given index"""
        if self.count() <= 1:
            # Don't close the last tab, just navigate to homepage
            web_view = self.widget(index)
            if isinstance(web_view, QWebEngineView):
                web_view.setUrl(QUrl(self.config["homepage"]))
            return

        # Remove the tab
        widget = self.widget(index)
        if widget:
            self.removeTab(index)
            widget.deleteLater()

    def get_current_web_view(self) -> QWebEngineView | None:
        """Get the current active web view"""
        current_widget = self.currentWidget()
        if isinstance(current_widget, QWebEngineView):
            return current_widget
        return None

    def navigate_current_tab(self, url: str) -> None:
        """Navigate the current tab to a URL"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(url))

    def _update_tab_title(self, web_view: QWebEngineView, title: str) -> None:
        """Update the title of a tab"""
        for i in range(self.count()):
            if self.widget(i) == web_view:
                # Limit title length
                display_title = title[:30] + "..." if len(title) > 30 else title
                self.setTabText(i, display_title or "Untitled")
                break

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change"""
        web_view = self.widget(index)
        if isinstance(web_view, QWebEngineView):
            # Emit URL change signal
            self.current_url_changed.emit(web_view.url())

    def _on_url_changed(self, url: QUrl) -> None:
        """Handle URL change in current tab"""
        sender_view = self.sender()
        current_view = self.get_current_web_view()

        # Only emit if this is the current tab
        if sender_view == current_view:
            self.current_url_changed.emit(url)

    def _add_new_tab_button(self) -> None:
        """Add a '+' button to create new tabs"""
        # Create a simple button in the corner
        new_tab_btn = ToolButton(self.create_new_tab)
        new_tab_btn.setText("+")
        new_tab_btn.setToolTip("New Tab")
        self.setCornerWidget(new_tab_btn)
