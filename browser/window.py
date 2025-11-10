from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)
from PyQt6.QtCore import QPoint, QUrl, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

from browser.data import read_config, setup_logging
from browser.qt import ToolButton, TabWidget

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
        self.resize(800, 600)

        instance = QApplication.instance()
        if not instance or not isinstance(instance, QApplication):
            logger.fatal("[FATAL] Application window not found!")
            return

        self.instance = instance
        self.devtools_view: QWebEngineView | None = None

    def init_ui(self):
        main_widget = QWidget()

        # Tab widget with web views
        self.tab_widget = TabWidget()
        self.tab_widget.current_url_changed.connect(self.update_url)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Navigation bar
        nav_bar = QHBoxLayout()
        self.back_btn = ToolButton(self.go_back)
        self.forward_btn = ToolButton(self.go_forward)
        self.refresh_btn = ToolButton(self.refresh_page)
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
            logger.warning("[WARN] Style hints are not available!")

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.refresh_btn)
        nav_bar.addWidget(self.home_btn)
        nav_bar.addWidget(self.address_bar)

        layout.addLayout(nav_bar)
        layout.addWidget(self.tab_widget)

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
            self.devtools_view = QWebEngineView()
            self.devtools_view.setWindowTitle("Developer Tools")
            self.devtools_view.resize(1024, 600)

            devtools_page = self.devtools_view.page()

            web_view = self.tab_widget.get_current_web_view()
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
        # New tab: Ctrl+T
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.create_new_tab)

        # Close tab: Ctrl+W
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(self.close_current_tab)

        # Next tab: Ctrl+Tab
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self.next_tab)

        # Previous tab: Ctrl+Shift+Tab
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self.previous_tab)

        # Refresh: F5 or Ctrl+R
        refresh_f5 = QShortcut(QKeySequence("F5"), self)
        refresh_f5.activated.connect(self.refresh_page)

        refresh_ctrl_r = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_ctrl_r.activated.connect(self.refresh_page)

        # Address bar focus: Ctrl+L
        address_focus = QShortcut(QKeySequence("Ctrl+L"), self)
        address_focus.activated.connect(self.focus_address_bar)

        # Opening dev tools: F12 and Ctrl+Shift+I
        devtools_f12_shortcut = QShortcut(QKeySequence("F12"), self)
        devtools_f12_shortcut.activated.connect(self.toggle_devtools)
        devtools_ctrl_shift_i_shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        devtools_ctrl_shift_i_shortcut.activated.connect(self.toggle_devtools)

    def create_new_tab(self):
        """Create a new tab"""
        self.tab_widget.create_new_tab()

    def close_current_tab(self):
        """Close the current tab"""
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.close_tab(current_index)

    def next_tab(self):
        """Switch to next tab"""
        current = self.tab_widget.currentIndex()
        count = self.tab_widget.count()
        next_index = (current + 1) % count
        self.tab_widget.setCurrentIndex(next_index)

    def previous_tab(self):
        """Switch to previous tab"""
        current = self.tab_widget.currentIndex()
        count = self.tab_widget.count()
        prev_index = (current - 1) % count
        self.tab_widget.setCurrentIndex(prev_index)

    def focus_address_bar(self):
        """Focus the address bar and select all text"""
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def go_back(self):
        """Go back in current tab"""
        web_view = self.tab_widget.get_current_web_view()
        if web_view:
            web_view.back()

    def go_forward(self):
        """Go forward in current tab"""
        web_view = self.tab_widget.get_current_web_view()
        if web_view:
            web_view.forward()

    def refresh_page(self):
        """Refresh current tab"""
        web_view = self.tab_widget.get_current_web_view()
        if web_view:
            web_view.reload()

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

        # Navigate current tab
        web_view = self.tab_widget.get_current_web_view()
        if web_view:
            web_view.setUrl(url)

    def update_url(self, url: QUrl):
        """Update address bar with current tab's URL"""
        self.address_bar.setText(url.toString())
