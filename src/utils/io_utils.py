from pathlib import Path
import pandas as pd
from config import logger, DEFAULT_CSV_ENCODING

def read_csv_safe(path: Path, **kwargs) -> pd.DataFrame:
    try:
        logger.info(f"Reading CSV: {path}")
        return pd.read_csv(path, encoding=DEFAULT_CSV_ENCODING, **kwargs)
    except Exception as e:
        logger.exception(f"Error reading CSV {path}: {e}")
        raise


def to_excel_safe(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    try:
        logger.info(f"Writing Excel: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(path, index=index)
    except Exception as e:
        logger.exception(f"Error writting Excel {path}: {e}")
        raise