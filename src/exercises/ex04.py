from pathlib import Path
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, logger
from src.utils.web_utils import get_soup
from bs4 import BeautifulSoup

URL = "https://www.w3schools.com/html/html_tables.asp"

FALLBACK_HTML = """
<html><body>
<table id="customers">
  <tr><th>Company</th><th>Contact</th><th>Country</th></tr>
  <tr><td>Alfreds Futterkiste</td><td>Maria Anders</td><td>Germany</td></tr>
  <tr><td>Centro comercial Moctezuma</td><td>Francisco Chang</td><td>Mexico</td></tr>
  <tr><td>Ernst Handel</td><td>Roland Mendel</td><td>Austria</td></tr>
  <tr><td>Island Trading</td><td>Helen Bennett</td><td>UK</td></tr>
  <tr><td>Laughing Bacchus Winecellars</td><td>Yoshi Tannamuri</td><td>Canada</td></tr>
  <tr><td>Magazzini Alimentari Riuniti</td><td>Giovanni Rovelli</td><td>Italy</td></tr>
</table>
</body></html>
"""


def parse_table_to_df(table_tag) -> pd.DataFrame:
    rows = table_tag.find_all("tr")
    if not rows:
        return pd.DataFrame()

    header_cells = rows[0].find_all(["th", "td"])
    headers = [c.get_text(strip=True) for c in header_cells]
    if not headers:
        headers = [f"col_{i}" for i in range(len(header_cells))]

    data = []
    for tr in rows[1:]:
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        values = [c.get_text(strip=True) for c in cells]
        if len(values) < len(headers):
            values += [None] * (len(headers) - len(values))
        elif len(values) > len(headers):
            values = values[:len(headers)]
        data.append(values)

    return pd.DataFrame(data, columns=headers)


def scrap_customers_table() -> pd.DataFrame:
    try:
        soup = get_soup(URL)
        table = soup.find("table", id="customers") or soup.find("table")
        if table in None:
            raise ValueError("No table found")
        df = parse_table_to_df(table)
        if df.empty:
            raise ValueError("No valid rows in table")
        logger.info(f"Table with {len(df)} rows")
        return df
    except Exception as e:
        logger.warning(f"Fail scrapping {e}")
        fallback_path = RAW_DIR / "customers_fallback.html"
        fallback_path.write_text(FALLBACK_HTML, encoding="utf-8")
        soup_fb = BeautifulSoup(FALLBACK_HTML, "html.parser")
        table_fb = soup_fb.find("table")
        df_fb = parse_table_to_df(table_fb)
        return df_fb


def main():
    df = scrap_customers_table()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    out_path = PROCESSED_DIR / "customers_from_html.xlsx"
    df.to_excel(out_path, index=False)
    logger.info(f"Exporting in: {out_path}")


if __name__ == "__main__":
    main()