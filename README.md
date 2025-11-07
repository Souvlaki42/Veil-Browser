<div align="center">

# Veil Browser

This project was originally made by [ThatSINEWAVE](https://github.com/ThatSINEWAVE).

![Veil-Browser](https://raw.githubusercontent.com/Souvlaki42/Veil-Browser/refs/heads/main/.github/SCREENSHOTS/browser.png)

Veil Browser is a privacy-first web browser designed to eliminate tracking, data collection, and intrusive analytics. It is fully open-source and built with the goal of providing a truly private browsing experience. The project is currently in its early development stage and remains highly unstable.

</div>

## Planned Features

- 🚫 **No Trackers** – No hidden tracking, telemetry, or data collection.
- 🔓 **Open Source** – Fully transparent code for community-driven development.
- 🎭 **Custom UI** – A unique, modern, and minimalist interface.
- 🛠 **No Bloat** – Stripped-down browsing experience without unnecessary features.
- 🏴 **Privacy by Design** – Enforced privacy-focused settings by default.

## Current Status

Veil Browser is in **early development** and is currently **unstable and mostly unusable**. Key functionalities, such as smooth navigation and stability, are still under development.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [UV](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

## Installation

1. Clone the repository:

```bash
git clone git@github.com:Souvlaki42/Veil-Browser.git
cd Veil-Browser
```

### For Arch Linux users (recommended for proprietary codec support)

1. Install system PyQt6 packages:

```bash
sudo pacman -Sy --needed python-pyqt6 python-pyqt6-webengine
```

2. Create environment with system package access:

```bash
uv venv --system-site-packages
uv sync
```

**Note:** The system PyQt6 includes proprietary codecs (H.264, AAC) by default.

### For other platforms

Install with PyQt6 from PyPI:

```bash
uv venv
uv sync --extra pyqt
```

**Note:** PyPI PyQt6 does not include proprietary codecs.

### Verify Installation

```bash
python -c "import PyQt6; print(PyQt6)"
```

If the path includes `/usr/lib/python3.x/`, you're using system packages with codec support.

### After installation

Run the application:

```bash
uv run main.py
```

The application will automatically create:

- `data/history.json`: Browsing history storage.
- `data/config.json`: Browser configuration file.
- `data/logs/`: Application log directory.

## Known Issues

- Navigation issues and broken rendering.
- Limited functionality beyond basic browsing.

## Roadmap

- [ ] Add an integrated ad and tracker blocker.
- [ ] Enhance the UI with more customization options.
- [ ] Add site options and auto play.
- [ ] Add persistent storage.
- [ ] Add incognito mode.
- [ ] Add keyboard shortcuts.
- [ ] Add chrome devtools.

## Other credits

- Icons use [this font](https://github.com/google/material-design-icons/blob/master/variablefont/MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf)

<div align="center">

## [Join my discord server](https://moulas.dev/discord)

</div>

## Contributions

Contributions are welcome! Feel free to fork the repository, submit issues, and open pull requests.
Please note:

- Core browser logic is in `browser/` package

## License

This project is licensed under the GPL-3.0 License. See [LICENSE](LICENSE) for more details.

## Disclaimer

This browser is **not yet suitable for daily use**. Expect bugs, crashes, and missing features as development progresses.

Stay tuned for updates and improvements as we work toward making Veil Browser a truly private and reliable browsing solution!
