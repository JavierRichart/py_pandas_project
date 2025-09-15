from pathlib import Path
from datetime import datetime, date
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR, logger

DEDUP_KEYS = ["date", "product"]
MASTER_PATH = PROCESSED_DIR / "master.xlsx"
BACKUP_DIR = PROCESSED_DIR / "backups"


def find_daily_excel(raw_dir: Path) -> Path | None:
    xlsx_files = sorted(raw_dir.glob('*.xlsx'))
    return  xlsx_files[0] if xlsx_files else None


def create_sample_daily_excel(dest: Path) -> Path:
    today = date.today().isoformat()
    df = pd.DataFrame({
        "date": [today, today, today],
        "product": ["A", "B", "C"],
        "price": [11, 12, 9]
        "sold_units": [90, 80, 120]
    })
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(dest, index=False)
    logger.warning(f"Not found {dest}")
    return dest


