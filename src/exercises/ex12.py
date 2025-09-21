from pathlib import Path
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe

OUT_PATH = PROCESSED_DIR / "last_sheet.xlsx"


def find_latest_xlsx(raw_dir: Path) -> Path | None:
    files = [p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() == ".xlsx"]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def main():
    src = find_latest_xlsx(RAW_DIR)
    if src is None:
        logger.error(f"No files in {RAW_DIR}")
        return

    logger.info(f"Processing book: {src.name}")
    book = pd.read_excel(src, sheet_name=None)
    if not book:
        logger.error(f"No sheets in {src.name}")
        return

    frames = []
    for sheet_name, df in book.items():
        if df is None or df.empty:
            logger.info(f"{sheet_name} is empty")
            continue
        df = df.copy()
        df["sheet"] = sheet_name
        frames.append(df)

    if not frames:
        logger.error("All sheets are empty")
        return

    union = pd.concat(frames, ignore_index=True)
    to_excel_safe(union, OUT_PATH, index=True)
    logger.info(f"File saved in {OUT_PATH}. (Rows= {len(union)})")


if __name__ == "__main__":
    main()
