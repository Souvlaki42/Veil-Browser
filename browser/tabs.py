from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QWidget
from browser.history import append_to_favicons, append_to_history
from browser.qt import ToolButton, WebPage, WebView
from browser.utils import Config, setup_logging


class Tabs(QTabWidget):
    """Custom tab widget for handling multiple browser tabs"""

    # Signal emitted when the current URL changes
    current_url_changed = pyqtSignal(QUrl)

    # Signal emitted when window's last tab is closed
    last_tab_closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = Config.load()
        self.logger = setup_logging()

        # Configure tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)
        self.tabBarDoubleClicked.connect(self._tab_open_doubleclick)

        # Create initial tab
        self.create_new_tab()

    def create_new_tab(self, url: str | None = None) -> WebView:
        """Create a new tab with a web view"""
        web_view = WebView()

        # Set URL or homepage
        if url:
            web_view.setUrl(QUrl(url))
        else:
            web_view.setUrl(QUrl(self.config.homepage))

        # Connect signals
        web_view.titleChanged.connect(
            lambda title: self._update_tab_title(web_view, title)
        )
        web_view.urlChanged.connect(self._on_url_changed)
        web_view.loadStarted.connect(
            lambda: self._update_tab_title(web_view, "Loading...")
        )
        web_view.loadFinished.connect(self._on_load_finished)
        web_view.iconChanged.connect(lambda icon: self._update_tab_icon(web_view, icon))

        # Add tab
        tab_index = self.addTab(web_view, "New Tab")
        self.setCurrentIndex(tab_index)

        # Add "+" button for new tab if this is the only tab
        if self.count() == 1:
            self._add_new_tab_button()

        return web_view

    def _tab_open_doubleclick(self, i):
        if i == -1:
            self.create_new_tab()

    def close_tab(self, index: int) -> None:
        """Close a tab at the given index"""
        if self.count() <= 1:
            if not self.config.close_after_last_tab:
                web_view = self.widget(index)
                if isinstance(web_view, WebView):
                    web_view.setUrl(QUrl(self.config.homepage))
                return
            else:
                # Clean up and emit signal
                widget = self.widget(index)
                if widget:
                    if isinstance(widget, WebView):
                        page = widget.page()
                        if not page:
                            return
                        page.deleteLater()

                    self.removeTab(index)
                    widget.deleteLater()

                # Emit signal for parent to handle
                self.last_tab_closed.emit()
                return

        # Normal tab closing
        widget = self.widget(index)
        if widget:
            if isinstance(widget, WebView):
                page = widget.page()
                if not page:
                    return
                page.deleteLater()

            self.removeTab(index)
            widget.deleteLater()

    def get_current_web_view(self) -> WebView | None:
        """Get the current active web view"""
        current_widget = self.currentWidget()
        if isinstance(current_widget, WebView):
            return current_widget
        return None

    def navigate_current_tab(self, url: str) -> None:
        """Navigate the current tab to a URL"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(url))

    def _update_tab_title(self, web_view: WebView, title: str) -> None:
        """Update the title of a tab"""
        for i in range(self.count()):
            if self.widget(i) == web_view:
                # Limit title length
                display_title = title[:30] + "..." if len(title) > 30 else title
                self.setTabText(i, display_title or "Untitled")
                break

    def _update_tab_icon(self, web_view: WebView, icon: QIcon) -> None:
        """Update the favicon of a tab"""
        for i in range(self.count()):
            if self.widget(i) == web_view:
                self.setTabIcon(i, icon)
                break
        page = web_view.page()
        if page:
            append_to_favicons(page, icon)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change"""
        web_view = self.widget(index)
        if isinstance(web_view, WebView):
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

    def _on_load_finished(self) -> None:
        view = self.get_current_web_view()
        if not view:
            return
        page = view.page()
        if not page:
            return
        self._update_tab_title(view, page.title())
        append_to_history(page)

    def request_dev_tools(self):
        tab = self.get_current_web_view()  # Get your current web view
        if not tab:
            return
        page = tab.page()
        if not page:
            return

        devtools_page = WebPage()
        page.setDevToolsPage(devtools_page)
        page.triggerAction(WebPage.WebAction.InspectElement)

    def set_zoom_level(self, level: int):
        view = self.get_current_web_view()
        if view:
            view.setZoomFactor(level / 100)
