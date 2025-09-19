from pathlib import Path
from datetime import date
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe

OUT_PATH = PROCESSED_DIR / "main.xlsx"

SYNONYMS = {
    "date": {"date", "fecha", "trade_date"},
    "product": {"product", "producto", "article"},
    "price": {"price", "precio", "cost"},
    "sold_units": {"sold_un", "unidades", "quantity", "cantidad", "uds"}
}


def find_latest_xlsx(raw_dir: Path) -> Path | None:
    files = list(raw_dir.glob("*.xlsx"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    lower_map = {c.lower().strip(): c for c in df.columns}
    for target, aliases in SYNONYMS.items():
        for alias in aliases:
            if alias in lower_map:
                rename_map[lower_map[alias]] = target
                break
    df = df.rename(columns=rename_map)
    missing = [k for k in SYNONYMS.keys() if k not in df.columns]
    if missing:
        raise ValueError(f"Some columns are missing {missing}")
    return df


def clean_and_cast(df: pd.DataFrame) -> pd.DataFrame:
    df["product"] = df["product"].astype(str).str.strip().str.upper()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["sold_units"] = pd.to_numeric(df["sold_units"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["date", "product"])
    df = df.fillna({"price": 0, "sold_units": 0})
    after = len(df)
    logger.info(f"Valid rows: {after} / {before}")

    return df[["date", "product", "price", "sold_units"]].copy()


def main():
    src = find_latest_xlsx(RAW_DIR)
    if src is None:
        logger.error(f"No files in {RAW_DIR}")
        return

    logger.info(f"Proccesing {src.name}")
    try:
        df = pd.read_excel(src)
        df = normalize_headers(df)
        df = clean_and_cast(df)
        to_excel_safe(df, OUT_PATH, index=False)
        logger.info(f"File saved in {OUT_PATH}")
    except Exception as e:
        logger.exception(f"Error {src}: {e}")


if __name__ == "__main__":
    main()