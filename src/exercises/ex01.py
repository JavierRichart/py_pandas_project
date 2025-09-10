from pathlib import Path
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.io_utils import to_excel_safe

def main():
    sample = pd.DataFrame({
        "producto": ["A", "B", "C", "A", "B"],
        "precio": [10, 12, 9, 11, 13],
        "ud_vendidas": [100, 80, 120, 90, 60]
    })
    csv_path = RAW_DIR/ "ventas.csv"
    sample.to_csv(csv_path, index=False)
    logger.info(f"CSV created in: {csv_path}")

    df = pd.read_csv(csv_path)

    df_filtrado = df[df["precio"] >= 11].copy()

    df_filtrado["importe"] = df_filtrado["precio"] * df_filtrado["ud_vendidas"]

    out_path = PROCESSED_DIR / "ventas_filtrado.xlsx"
    to_excel_safe(df_filtrado, out_path)
    logger.info(f"File saved in {out_path}")


if __name__ == "__main__":
    main()