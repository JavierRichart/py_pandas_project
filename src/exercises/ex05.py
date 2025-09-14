from pathlib import Path
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.plot_utils import save_lineplot


def ensure_airtravel(csv_path: Path) -> pd.DataFrame:
    if csv_path.exists():
        logger.info(f"Usando datos existentes: {csv_path}")
        return pd.read_csv(csv_path)
    logger.warning(f"No se encontró {csv_path}. Creando datos de ejemplo.")
    df = pd.DataFrame({
        "Month": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
        "1958": [340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310, 337]
    })
    df.to_csv(csv_path, index=False)
    return df


def month_to_number(month_str: str) -> int:
    mapping = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }
    return mapping.get(month_str.strip().upper(), None)


def main():
    csv_path = RAW_DIR / "airtravel.csv"
    df = ensure_airtravel(csv_path)

    if "Month" not in df.columns:
        raise ValueError("No se encontró la columna 'Month' en el CSV.")
    if "1958" not in df.columns:
        year_cols = [c for c in df.columns if c.isdigit()]
        if not year_cols:
            raise ValueError("No hay ninguna columna de año numérico en el CSV.")
        year = year_cols[0]
        logger.warning(f"No se encontró '1958'. Usando '{year}' en su lugar.")
    else:
        year = "1958"

    df["month_num"] = df["Month"].apply(month_to_number)
    df = df.dropna(subset=["month_num"]).sort_values("month_num")

    x = df["Month"]
    y = pd.to_numeric(df[year], errors="coerce").fillna(0)

    out_img = PROCESSED_DIR / f"airtravel_{year}_line.png"
    save_lineplot(
        x=x,
        y=y,
        out_path=out_img,
        title=f"Travelers / Month ({year})",
        xlabel="Month",
        ylabel="Travellers"
    )
    logger.info(f"Saved: {out_img}")


if __name__ == "__main__":
    main()
