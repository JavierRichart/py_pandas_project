from pathlib import Path
from urllib.parse import urlparse
from config import RAW_DIR, logger
from src.utils.web_utils import download_file

URLS_TXT = RAW_DIR / "urls.txt"
DEST_DIR = RAW_DIR / "downloads"


def sanitize_filename(text: str) -> str:
    s = str(text).strip()
    for ch in r'\/:*?"<>|':
        s = s.replace(ch, "_")
    return (s or "file").strip()[:120]


def unique_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem, suffix = base.stem, base.suffix
    i = 1
    while True:
        candidate = base.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def derive_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        name = "file.csv"
    if "." not in name:
        name += ".csv"
    if not name.lower().endswith(".csv"):
        name += ".csv"
    return sanitize_filename(name)


def main():
    if not URLS_TXT.exists():
        logger.error(f"{URLS_TXT} does not exist")
        return

    lines = [ln.strip() for ln in URLS_TXT.read_text(encoding="utf-8").splitlines()]
    urls = [ln for ln in lines if ln and not ln.startswith("#")]

    if not urls:
        logger.error(f"No valid URLs in {URLS_TXT}")
        return

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading {len(urls)} files in {DEST_DIR}")

    for url in urls:
        try:
            filename = derive_filename_from_url(url)
            dest = unique_path(DEST_DIR / filename)
            download_file(url, dest)
            logger.info(f"{url} -> {dest.name}")
        except Exception as e:
            logger.exception(f"{url} download failed: {e}")


if __name__ == "__main__":
    main()
