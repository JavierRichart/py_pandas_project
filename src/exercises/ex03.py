from pathlib import Path
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.web_utils import download_file
from src.utils.io_utils import to_excel_safe

CSV_URL = "https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv"


def main():
    dest = RAW_DIR / "airtravel.csv"
    try:
        download_file(CSV_URL, dest)
        df = pd.read_csv(dest)
    except Exception as e:
        logger.exception(f"File not found {e}. Creating example")
        df = pd.DataFrame({
            "Mont": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT"],
            "1958": [340, 318, 362, 348, 363, 435, 491, 505, 404, 359]
        })

    out = df.head(10).copy()

    out_path = PROCESSED_DIR / "airtravel_top.xlsx"
    to_excel_safe(out, out_path)
    logger.info(f"Processed and exported to: {out_path}")


if __name__ == "__main__":
    main()