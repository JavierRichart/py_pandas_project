from pathlib import Path
import requests
from config import logger
from bs4 import BeautifulSoup


def download_file(url: str, dest: Path, timeout: int = 30, chunk_size: int = 8192) -> Path:
    logger.info(f"Downloading: {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "python-lab/1.0"}) as r:
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        if "text" not in ctype and "csv" not in ctype:
            logger.warning(f"Unexpected Content-Type: {ctype}")
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    logger.info(f"File saved in {dest}")
    return dest


def get_soup(url: str, timeout: int = 30) -> BeautifulSoup:
    logger.info(f"HTML: {url}")
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "python-lab/1.0"})
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")