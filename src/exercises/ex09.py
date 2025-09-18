from pathlib import Path
import pandas as pd
from config import PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe

MASTER = PROCESSED_DIR / "master.xlsx"
OUT_DIR = PROCESSED_DIR / "by_product"


def ensure_master_if_missing() -> None:
    if MASTER.exists():
        return
    logger.warning(f"{MASTER} does not exist. Creating example")
    df = pd.DataFrame({
        "fecha": ["2025-09-01", "2025-09-01", "2025-09-02", "2025-09-02"],
        "producto": ["A", "B", "A", None],
        "precio": [10, 12, 11, 9],
        "ud_vendidas": [100, 80, 90, 120],
        "origen": ["ventas_1", "ventas_1", "ventas_2", "ventas_2"]
    })
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(MASTER, index=False)


def sanitize_filename(text: str) -> str:
    s = str(text).strip()
    if not s:
        s = "UNKNOWN"
    for ch in r'\/:*?"<>|':
        s = s.replace(ch, "_")
    return s[:80]


def main():
    ensure_master_if_missing()
    df = pd.read_excel(MASTER)

    if "product" not in df.columns:
        raise ValueError("Not found")

    df["product"] = df["product"].astype(str).str.strip().str.upper()
    df["product"] = df["product"].replace({"NAN": "", "NONE": ""})
    df["product"] = df["product"].where(df["product"] != "", "UNKNOWN")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    products = df["product"].unique().tolist()
    logger.info(f"Products found: {products}")

    for prod, subdf in df.groupby("product"):
        fname = f"product_{sanitize_filename(prod)}.xlsx"
        out_path = OUT_DIR / fname
        to_excel_safe(subdf, out_path, index=False)
        logger.info(f"Saved in {out_path}")


if __name__ == "__main__":
    main()
