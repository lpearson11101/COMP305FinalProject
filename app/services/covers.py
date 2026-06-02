import os
import requests
from pathlib import Path
from flask import url_for

BASE_DIR = Path(__file__).resolve().parent.parent.parent
COVER_DIR = BASE_DIR / "app" / "static" / "covers"
COVER_DIR.mkdir(parents=True, exist_ok=True)

OPEN_LIBRARY_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"


def get_cover_path(cover_id: int) -> Path:
    """Return local file path for a cover image."""
    return COVER_DIR / f"{cover_id}.jpg"


def cover_exists(cover_id: int) -> bool:
    """Check if cover already exists locally."""
    return get_cover_path(cover_id).exists()


def download_cover(cover_id: int) -> bool:
    """
    Download cover from Open Library and save locally.
    Returns True if successful.
    """
    url = OPEN_LIBRARY_URL.format(cover_id=cover_id)
    path = get_cover_path(cover_id)

    try:
        response = requests.get(url, timeout=10, stream=True)
        if response.status_code != 200:
            return False

        # Avoid saving empty/invalid images
        if "image" not in response.headers.get("Content-Type", ""):
            return False
        
        tmp_path = path.with_suffix(".tmp")

        tmp_path.write_bytes(response.content)
        if not path.exists():
            tmp_path.replace(path)
        else:
            tmp_path.unlink(missing_ok=True)

        return True

    except requests.RequestException:
        return False

    #just in case of filesystem permission issues, we don't want to crash the app
    except PermissionError:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        return False

def ensure_cover_cached(cover_id: int) -> str | None:
    if not cover_id:
        return None

    if not cover_exists(cover_id):
        download_cover(cover_id)

    if cover_exists(cover_id):
        return f"covers/{cover_id}.jpg"

    return None