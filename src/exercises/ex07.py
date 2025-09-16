from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from config import RAW_DIR, PROCESSED_DIR, logger


def ensure_ventas(csv_path: Path) -> pd.DataFrame:
    if csv_path.exists():
        logger.info(f"Usando datos existentes: {csv_path}")
        return pd.read_csv(csv_path)

    logger.warning(f"No se encontró {csv_path}. Creando datos de ejemplo.")
    df = pd.DataFrame({
        "producto": ["A", "B", "C", "A", "B", "A", "C", "B", "A", "C"],
        "precio": [10, 12, 9, 11, 13, 10, 12, 12, 11, 9],
        "ud_vendidas": [100, 80, 120, 90, 60, 75, 110, 85, 95, 130],
    })
    df.to_csv(csv_path, index=False)
    return df


def main():
    csv_path = RAW_DIR / "ventas.csv"
    df = ensure_ventas(csv_path)

    ax1 = sns.histplot(data=df, x="precio", bins=10)
    ax1.set_title("Distribución de precios")
    ax1.set_xlabel("Precio")
    ax1.set_ylabel("Frecuencia")
    out_hist = PROCESSED_DIR / "precio_histograma.png"
    ax1.figure.tight_layout()
    out_hist.parent.mkdir(parents=True, exist_ok=True)
    ax1.figure.savefig(out_hist, dpi=150)
    plt.close(ax1.figure)
    logger.info(f"Histograma guardado en: {out_hist}")

    ax2 = sns.countplot(data=df, x="producto")
    ax2.set_title("Número de registros por producto")
    ax2.set_xlabel("Producto")
    ax2.set_ylabel("Conteo")
    out_count = PROCESSED_DIR / "productos_conteo.png"
    ax2.figure.tight_layout()
    ax2.figure.savefig(out_count, dpi=150)
    plt.close(ax2.figure)
    logger.info(f"Conteo guardado en: {out_count}")


if __name__ == "__main__":
    main()
