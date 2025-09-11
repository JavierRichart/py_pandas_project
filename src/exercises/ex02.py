from pathlib import Path
import pandas as pd
import numpy as np
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe


def ensure_data(csv_path: Path) -> pd.DataFrame:
    if csv_path.exists():
        logger.info(f"Using data {csv_path}")
        return pd.read_csv(csv_path)

    logger.warning(f"{csv_path} not found. Creating example")
    df = pd.DataFrame({
    "producto": ["A", "B", "C", "A", "B"],
    "precio": [10, 12, 9, 11, 13],
    "ud_vendidas": [100, 80, 120, 90, 60]
    })
    df.to_csv(csv_path, index=False)
    return df


def main():
    csv_path = RAW_DIR / "ventas.csv"
    df = ensure_data(csv_path)

    precios = df["precio"].to_numpy(dtype=float)

    media = np.mean(precios)
    sigma = np.std(precios, ddof=0)

    z = (precios - media) / sigma if sigma != 0 else np.zeros_like(precios)

    out = df.copy()
    out["zscore_precio"] = z

    out["precio_categoria"] = np.where(out["zscore_precio"] >= 0, ">= media", "< media")

    out_path = PROCESSED_DIR / "valores_zscore.xlsx"
    to_excel_safe(out, out_path)
    logger.info(f"media={media:.2f} | sigma={sigma:.2f} -> {out_path}")


if __name__ == "__main__":
    main()