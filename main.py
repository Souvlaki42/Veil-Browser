import sys
import platform
from typing import cast
import psutil
from PyQt6.QtWebEngineCore import qWebEngineChromiumVersion
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from browser.window import VeilBrowser
from browser.utils import Config, setup_logging

# Set up logging
logger = setup_logging()


def main():
    """Main application entry point"""
    try:
        config = Config.load()

        logger.info("=" * 50)
        logger.info(f"Veil Browser v{config.local_version} (fork/remix by UmaEra)")
        logger.info("Starting...")
        logger.info("=" * 50)

        app = QApplication(sys.argv)
        app.setApplicationName("Veil Browser")
        app.setWindowIcon(QIcon("browser/logo.svg"))
        app.setApplicationVersion(config.local_version)

        # Font configuration
        try:
            font = QFont("Segoe UI", 9)
            app.setFont(font)
        except Exception as e:
            logger.warning(f"Font setup failed: {e}")

        # Create and show browser
        browser = VeilBrowser()
        browser.show()

        # System info logging
        logger.info(f"System: {platform.platform()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Chromium: {qWebEngineChromiumVersion()}")
        logger.info(f"Configuration: {config}")

        try:
            mem = psutil.virtual_memory()
            mem_available: float = cast(int, mem.available) / (1024**3)
            logger.info(f"Memory Available: {mem_available:.1f} GB")
        except Exception as e:
            logger.error(f"[ERR] Memory check failed: {e}")

        exit_code = app.exec()
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"[FATAL] Error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
