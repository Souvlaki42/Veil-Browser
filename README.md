<div align="center">

# Veil Browser

_Privacy-first web browsing, reimagined_

![Veil-Browser](https://raw.githubusercontent.com/Souvlaki42/Veil-Browser/refs/heads/main/.github/SCREENSHOTS/browser.png)

**A modern, open-source browser designed to eliminate tracking and protect your privacy**

---

### **Contributors**

**Developer**: [Souvlaki42](https://github.com/Souvlaki42) \
**Developer**: [umaera](https://github.com/NotYarazi) \
**Original Creator**: [ThatSINEWAVE](https://github.com/ThatSINEWAVE)

## Features

<table>
<tr>
<td width="50%">

### **Privacy First**

- Zero tracking & telemetry
- Privacy by design
- No data collection

</td>
<td width="50%">

### **Clean Experience**

- Minimalist UI
- No bloatware & unnecessary stuff
- Lightweight & fast

</td>
</tr>
</table>

**Fully Open Source** – Transparent, community-driven development

---

## Current Status

> **⚠️ Development Stage**: Veil Browser is in early development. Expect instability and limited functionality.

> **🚨 Not ready for daily use yet!** This browser is under active development. Expect bugs, crashes, and missing features.

## Quick Start

</div>

### Prerequisites

- **Python 3.12+** → [Download here](https://www.python.org/downloads/)
- **UV Package Manager** (virtual environment - optional) → [Install UV](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

### Installation (virtual environment)

```bash
# 1. Clone the repository
git clone git@github.com:Souvlaki42/Veil-Browser.git
cd Veil-Browser

# 2. Setup environment
uv venv
uv sync --extra pyqt

# 3. Launch Veil Browser
uv run main.py
```

<details>
<summary><b>Arch Linux Installation</b></summary>

```bash
# Install system packages for codec support
sudo pacman -Sy --needed python-pyqt6 python-pyqt6-webengine

# Create environment with system packages
uv venv --system-site-packages
uv sync
```

</details>

<details>
<summary><b>Alternative: Install without virtual enviroment</b></summary>

```bash
pip install -r requirements.txt
python main.py
```

</details>

### Auto-created files:

- `data/config.json` - Browser settings
- `data/history.json` - Browser history
- `data/keybinds.json` - Browser keybindings
- `data/favicons.json` - Cached favicons
- `data/logs/` - Application logs
<div align="center">

## Roadmap

<table>
<tr>
<td width="50%">

### **Coming Soon**

- [x] Keyboard shortcuts
- [x] Tab support
- [ ] Ad & tracker blocker
- [ ] Incognito mode

</td>
<td width="50%">

### **Future Plans**

- [ ] UI customization
- [ ] Site-specific settings
- [x] Developer tools
- [ ] Enhanced storage

</td>
</tr>
</table>

<div align="center">

## Get Involved

### **Community**

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da?style=for-the-badge&logo=discord)](https://moulas.dev/discord)

### **Contribute**

Found a bug? Have an idea? **Contributions welcome!**

Report issues
Submit feature requests
Create pull requests

> Core browser logic is in the `browser/` package

---

## License & Credits

**License**: GPL-3.0 License - See [LICENSE](LICENSE)

**Icons**: [Material Design Icons](https://github.com/google/material-design-icons/blob/master/variablefont/MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf)

---

</div>
