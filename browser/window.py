from pathlib import Path
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)
from PyQt6.QtCore import QPoint, QUrl, Qt
from PyQt6.QtGui import QIcon

from browser.adblock import AdBlockInterceptor
from browser.utils import (
    Config,
    Keybindings,
    StepCycler,
    open_in_default_editor,
    setup_logging,
)
from browser.qt import ToolButton, WebAction, WebView
from browser.tabs import Tabs

import pyperclip

logger = setup_logging()


class VeilBrowser(QMainWindow):
    """Main browser window class"""

    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.init_window()
        self.init_ui()

    def init_window(self):
        self.setMouseTracking(True)
        self._drag_position: QPoint = QPoint()
        self.resize(800, 600)

        instance = QApplication.instance()
        if not instance or not isinstance(instance, QApplication):
            logger.fatal("[FATAL] Application window not found!")
            return

        self.instance = instance

        self.devtools_view: WebView | None = None

        self.profile = QWebEngineProfile.defaultProfile()
        if not self.profile:
            logger.warning("[WARNING] Profile not found!")
            return

        ad_blocker = AdBlockInterceptor()
        self.profile.setUrlRequestInterceptor(ad_blocker)

        zoom_levels = [
            25,
            33,
            50,
            67,
            75,
            80,
            90,
            100,
            110,
            125,
            150,
            175,
            200,
            250,
            300,
            400,
            500,
        ]
        self.zoom_cycler = StepCycler(zoom_levels, initial_value=self.config.zoom_level)

    def init_ui(self):
        main_widget = QWidget()

        # Tab widget with web views
        self.tabs = Tabs()
        self.tabs.current_url_changed.connect(self.update_url)
        self.tabs.last_tab_closed.connect(self.close)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Navigation bar
        nav_bar = QHBoxLayout()
        web_view = self.tabs.get_current_web_view()
        if web_view:
            page = web_view.page()
            if page:
                self.back_btn = ToolButton(page.action(WebAction.Back))
                self.forward_btn = ToolButton(page.action(WebAction.Forward))
                self.refresh_btn = ToolButton(page.action(WebAction.Reload))

        self.home_btn = ToolButton(
            lambda: self.navigate(self.config.homepage),
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
            logger.warning("[WARN] Style hints are not available!")

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.refresh_btn)
        nav_bar.addWidget(self.home_btn)
        nav_bar.addWidget(self.address_bar)

        layout.addLayout(nav_bar)
        layout.addWidget(self.tabs)

        self.setCentralWidget(main_widget)

        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def _update_icon_colors(self, color_scheme: Qt.ColorScheme | None):
        is_dark: bool = color_scheme == Qt.ColorScheme.Dark
        self.back_btn.update_icon("arrow_back", QIcon.ThemeIcon.GoPrevious, is_dark)
        self.forward_btn.update_icon("arrow_forward", QIcon.ThemeIcon.GoNext, is_dark)
        self.refresh_btn.update_icon("refresh", QIcon.ThemeIcon.ViewRefresh, is_dark)
        self.home_btn.update_icon("home", QIcon.ThemeIcon.GoHome, is_dark)

    def toggle_devtools(self):
        if self.devtools_view is None or not self.devtools_view.isVisible():
            self.devtools_view = WebView()
            self.devtools_view.setWindowTitle("Developer Tools")
            self.devtools_view.resize(1024, 600)

            devtools_page = self.devtools_view.page()

            web_view = self.tabs.get_current_web_view()
            if not web_view:
                logger.info("Web view is not found!")
                return

            page = web_view.page()
            if not page:
                logger.info("Page is not found!")
                return

            page.setDevToolsPage(devtools_page)
            self.devtools_view.show()
        else:
            self.devtools_view.hide()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for tab management"""
        web_view = self.tabs.get_current_web_view()
        if not web_view:
            return
        page = web_view.page()
        if not page:
            return

        keybinds = Keybindings.load()

        # New tab
        keybinds.bind_shortcuts("new_tab", self.create_new_tab, self)

        # Close tab
        keybinds.bind_shortcuts("close_tab", self.close_current_tab, self)

        # Next tab
        keybinds.bind_shortcuts("next_tab", self.next_tab, self)

        # Previous tab
        keybinds.bind_shortcuts("prev_tab", self.previous_tab, self)

        # Previous page
        keybinds.bind_shortcuts("prev_page", page.action(WebAction.Back), self)

        # Next page
        keybinds.bind_shortcuts("next_page", page.action(WebAction.Forward), self)

        # Refresh
        keybinds.bind_shortcuts("refresh", page.action(WebAction.Reload), self)

        # Address bar focus
        keybinds.bind_shortcuts("address_focus", self.focus_address_bar, self)

        # Opening dev tools
        keybinds.bind_shortcuts("devtools", self.toggle_devtools, self)

        # TODO FIX: Page source
        keybinds.bind_shortcuts("page_source", page.action(WebAction.ViewSource), self)

        # TODO: print page shortcut

        # TODO: save as shortcut

        # Copy address bar to clipboard
        keybinds.bind_shortcuts(
            "copy_address", self.copy_address_bar_to_clipboard, self
        )

        # Duplicate tab
        keybinds.bind_shortcuts(
            "duplicate_tab",
            lambda: self.tabs.create_new_tab(self.address_bar.text()),
            self,
        )

        # Reset zoom level
        keybinds.bind_shortcuts(
            "reset_zoom",
            lambda: self.tabs.set_zoom_level(self.zoom_cycler.reset()),
            self,
        )

        # Increase zoom level
        keybinds.bind_shortcuts(
            "increase_zoom",
            lambda: self.tabs.set_zoom_level(self.zoom_cycler.up()),
            self,
        )

        # Decrease zoom level
        keybinds.bind_shortcuts(
            "decrease_zoom",
            lambda: self.tabs.set_zoom_level(self.zoom_cycler.down()),
            self,
        )

        # Open config shortcut
        config_file_path = Path(__file__).parent.parent / "data/config.json"
        if config_file_path.exists():
            keybinds.bind_shortcuts(
                "open_config", lambda: open_in_default_editor(config_file_path), self
            )
        else:
            logger.warning("Didn't find configuration file!")

        # TODO: Reload config
        # keybinds.bind_shortcuts("reload_config", self.reload_config, self)

    def reload_config(self):
        Config.reload()
        Keybindings.reload()
        logger.info("Config and keybindings successfully reloaded!")

    def create_new_tab(self):
        """Create a new tab"""
        self.tabs.create_new_tab()

    def close_current_tab(self):
        """Close the current tab"""
        current_index = self.tabs.currentIndex()
        self.tabs.close_tab(current_index)

    def next_tab(self):
        """Switch to next tab"""
        current = self.tabs.currentIndex()
        count = self.tabs.count()
        next_index = (current + 1) % count
        self.tabs.setCurrentIndex(next_index)

    def previous_tab(self):
        """Switch to previous tab"""
        current = self.tabs.currentIndex()
        count = self.tabs.count()
        prev_index = (current - 1) % count
        self.tabs.setCurrentIndex(prev_index)

    def focus_address_bar(self):
        """Focus the address bar and select all text"""
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def copy_address_bar_to_clipboard(self):
        """Copy the contents of the address bar to system clipboard"""
        content = self.address_bar.text().strip()
        if not content == "":
            pyperclip.copy(content)

    def navigate(self, input: str | None):
        text = input or self.address_bar.text()

        # Try parsing as URL
        url = QUrl(text)

        if not url.scheme():
            if "." in text and " " not in text:
                url = QUrl("https://" + text)
            else:
                # Search query
                search_url = str(self.config.search_engine).replace("%s", text)
                url = QUrl(search_url)

        # Navigate current tab
        web_view = self.tabs.get_current_web_view()
        if web_view:
            web_view.setUrl(url)

    def update_url(self, url: QUrl):
        """Update address bar with current tab's URL"""
        self.address_bar.setText(url.toString())
