import pandas as pd
from pathlib import Path

# path file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "gadai_raw.xlsx"

# ambil daftar sheet
xls = pd.ExcelFile(DATA_PATH)

print("JUMLAH SHEET:", len(xls.sheet_names))
print("\nDAFTAR SHEET:\n")

for sheet in xls.sheet_names:
    df = pd.read_excel(DATA_PATH, sheet_name=sheet)
    print(f"Sheet: {sheet}")
    print(f"  Shape : {df.shape}")
    print(f"  Kolom : {list(df.columns)[:8]} ...")
    print("-" * 50)
