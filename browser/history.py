from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse
import hashlib

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineCore import QWebEnginePage

from url_normalize import url_normalize


def qicon_to_base64(icon: QIcon, size: tuple = (24, 24)) -> str:
    pixmap = icon.pixmap(size[0], size[1])

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG")
    buffer.close()

    base64_data = byte_array.toBase64().data().decode("utf-8")
    data_uri = f"data:image/png;base64,{base64_data}"

    return data_uri


def get_favicon_id(domain: str) -> str:
    """Generate predictable favicon ID from domain"""
    # Use domain as the ID base (shortened hash)
    domain_hash = hashlib.sha256(domain.encode()).hexdigest()[:12]
    return f"fav_{domain_hash}"


def append_to_history(page: QWebEnginePage):
    """Append to the history file"""

    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    history_file = data_dir / "history.json"
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = {}

    url = page.url().url()
    canonical_url = url_normalize(url) or url

    parsed = urlparse(canonical_url)
    domain = parsed.netloc.replace("www.", "")

    now = datetime.now()
    str_date = str(now.date())

    if str_date not in history:
        history[str_date] = []

    existing_entry = None
    for item in history[str_date]:
        if item["canonical_url"] == canonical_url:
            existing_entry = item
            break

    if existing_entry:
        existing_entry["visits"].append(now.timestamp())
        existing_entry["title"] = page.title()
    else:
        history[str_date].append(
            {
                "title": page.title(),
                "url": url,
                "canonical_url": canonical_url,
                "favicon_id": get_favicon_id(domain),
                "visits": [now.timestamp()],
            }
        )

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    return history


def append_to_favicons(page: QWebEnginePage, icon: QIcon | None = None):
    """Append to the favicon file"""

    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    favicon = icon or page.icon()
    favicon_file = data_dir / "favicons.json"

    if favicon_file.exists():
        with open(favicon_file, "r") as f:
            favicons = json.load(f)
    else:
        favicons = {}

    url = page.url().url()
    canonical_url = url_normalize(url) or url

    parsed = urlparse(canonical_url)
    domain = parsed.netloc.replace("www.", "")

    favicon_id = get_favicon_id(domain)

    is_icon_empty = favicon.isNull() or len(favicon.availableSizes()) <= 0

    if favicon_id not in favicons or favicons[favicon_id]["status"] == "pending":
        favicons[favicon_id] = {
            "domain": domain,
            "icon_data": None if is_icon_empty else qicon_to_base64(favicon),
            "last_updated": None if is_icon_empty else datetime.now().isoformat(),
            "status": "pending" if is_icon_empty else "loaded",
        }

    clean_favicons = {}
    for favicon_id, favicon in favicons.items():
        if favicon["domain"] == "":
            continue
        else:
            clean_favicons[favicon_id] = favicon

    with open(favicon_file, "w") as f:
        json.dump(clean_favicons, f, indent=2)

    return clean_favicons
