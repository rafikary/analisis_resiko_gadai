import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "output" / "gadai_master_dataset.xlsx"

df = pd.read_excel(DATA_PATH)

print("TOTAL BARIS :", len(df))
print("TOTAL KOLOM :", len(df.columns))
print()

# cek distribusi status
print("DISTRIBUSI STATUS")
print(df["status_sheet"].value_counts())
print()

# cek missing value
print("MISSING VALUE PER KOLOM")
missing = df.isna().sum()
print(missing[missing > 0])
print()

# cek kolom identifier
for col in ["no", "imei", "outlet"]:
    if col in df.columns:
        print(f"VALIDASI KOLOM: {col}")
        print("  kosong :", df[col].isna().sum())
        print("  unik   :", df[col].nunique())
        print()

# cek tanggal
print("VALIDASI TANGGAL")
print("  kosong :", df["tanggal"].isna().sum())
print("  min    :", df["tanggal"].min())
print("  max    :", df["tanggal"].max())
print()

# cek duplikasi imei
if "imei" in df.columns:
    dup_imei = df["imei"].value_counts()
    print("IMEI DUPLIKASI (TOP 10)")
    print(dup_imei[dup_imei > 1].head(10))
