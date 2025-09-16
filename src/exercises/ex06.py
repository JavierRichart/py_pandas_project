from pathlib import Path
from datetime import datetime, date
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR, logger

DEDUP_KEYS = ["fecha", "producto"]
MASTER_PATH = PROCESSED_DIR / "maestro_ventas.xlsx"
BACKUP_DIR = PROCESSED_DIR / "backups"


def _find_daily_excel(raw_dir: Path) -> Path | None:
    xlsx_files = sorted(raw_dir.glob("*.xlsx"))
    return xlsx_files[0] if xlsx_files else None


def _create_sample_daily_excel(dest: Path) -> Path:
    today = date.today().isoformat()
    df = pd.DataFrame({
        "fecha": [today, today, today],
        "producto": ["A", "B", "C"],
        "precio": [11, 12, 9],
        "ud_vendidas": [90, 80, 120],
    })
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(dest, index=False)
    logger.warning(f"No se encontró Excel diario. Creado ejemplo: {dest}")
    return dest


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        lc = col.strip().lower()
        if lc in {"fecha", "date"}:
            rename_map[col] = "fecha"
        elif lc in {"producto", "product"}:
            rename_map[col] = "producto"
        elif lc in {"precio", "price"}:
            rename_map[col] = "precio"
        elif lc in {"ud_vendidas", "unidades", "qty", "cantidad"}:
            rename_map[col] = "ud_vendidas"

    df = df.rename(columns=rename_map)

    for required in ["producto", "precio", "ud_vendidas"]:
        if required not in df.columns:
            raise ValueError(f"Falta columna obligatoria en el diario: '{required}'")

    if "fecha" not in df.columns:
        df["fecha"] = date.today().isoformat()

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["ud_vendidas"] = pd.to_numeric(df["ud_vendidas"], errors="coerce")

    if "producto" in df.columns:
        df["producto"] = df["producto"].astype(str).str.strip().str.upper()

    df = df.dropna(subset=["fecha", "producto"])
    return df[["fecha", "producto", "precio", "ud_vendidas"]].copy()


def _backup_master(master_path: Path) -> None:
    if not master_path.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bkp = BACKUP_DIR / f"{master_path.stem}_{ts}{master_path.suffix}"
    master_path.replace(bkp)
    logger.info(f"Backup del maestro creado en: {bkp}")


def main():
    daily = _find_daily_excel(RAW_DIR)
    if daily is None:
        daily = RAW_DIR / f"ventas_diarias_{date.today().strftime('%Y%m%d')}.xlsx"
        daily = _create_sample_daily_excel(daily)
    logger.info(f"Usando Excel diario: {daily}")

    df_day = pd.read_excel(daily)
    df_day = _normalize_columns(df_day)
    df_day["ingestion_ts"] = datetime.now().isoformat(timespec="seconds")

    if MASTER_PATH.exists():
        df_master = pd.read_excel(MASTER_PATH)
        logger.info(f"Maestro existente cargado: {MASTER_PATH} ({len(df_master)} filas)")
    else:
        df_master = pd.DataFrame(columns=["fecha", "producto", "precio", "ud_vendidas", "ingestion_ts"])
        logger.info("No existe maestro. Se creará uno nuevo.")

    combined = pd.concat([df_master, df_day], ignore_index=True)

    combined["fecha"] = pd.to_datetime(combined["fecha"], errors="coerce").dt.date
    combined["ingestion_ts"] = pd.to_datetime(combined["ingestion_ts"], errors="coerce")

    combined = (
        combined.sort_values(["ingestion_ts"])
        .drop_duplicates(subset=DEDUP_KEYS, keep="last")
        .sort_values(["fecha", "producto"])
        .reset_index(drop=True)
    )

    _backup_master(MASTER_PATH)
    MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_excel(MASTER_PATH, index=False)
    logger.info(f"Maestro actualizado: {MASTER_PATH} ({len(combined)} filas)")


if __name__ == "__main__":
    main()
