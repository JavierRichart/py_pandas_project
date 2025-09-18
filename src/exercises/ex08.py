from pathlib import Path
import pandas as pd
from datetime import date
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe


def ensure_samples_if_empty(raw_dir: Path) -> None:
    files = list(raw_dir.glob("*.xlsx"))
    if files:
        return
    logger.warning("Not files found. Creating examples")
    df1 = pd.DataFrame({
        "date": [date.today().isoformat(), date.today().isoformat()],
        "product": ["A", "B"], "price": [10, 12], "sold_units": [100, 80]
    })
    df2 = pd.DataFrame({
        "date": [date.today().isoformat()],
        "product": ["C"], "price": [9], "sold_units": [120]
    })
    (raw_dir / "sales_1.xlsx").parent.mkdir(parents=True, exist_ok=True)
    df1.to_excel(raw_dir / "sales_1.xlsx", index=False)
    df2.to_excel(raw_dir / "sales_2.xlsx", index=False)


def main():
    ensure_samples_if_empty(RAW_DIR)
    files = sorted(RAW_DIR.glob("*.xlsx"))
    if not files:
        logger.error("No files to combine")
        return
    logger.info(f"{len(files)} files found")
    frames = []
    for f in files:
        try:
            df = pd.read_excel(f)
            df["origin"] = f.stem
            frames.append(df)
        except Exception as e:
            logger.exception(f"Error reading {f}: {e}")

    if not frames:
        logger.error("Impossible to read files")
        return

    combo = pd.concat(frames, ignore_index=True)
    out_path = PROCESSED_DIR / "master.xlsx"
    to_excel_safe(combo, out_path, index=False)
    logger.info(f"File generated: {out_path} ({len(combo)})")


if __name__ == "__main__":
    main()
