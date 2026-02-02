import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "output" / "gadai_master_dataset.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

df = pd.read_excel(DATA_PATH)

print("DATA AWAL")
print("Baris :", len(df))
print("IMEI unik :", df["imei"].nunique())
print()

# prioritas status (semakin besar = semakin buruk)
status_priority = {
    "Auction": 5,
    "Late": 4,
    "On-Due": 3,
    "Active": 2,
    "Outstanding": 1
}

df["status_rank"] = df["status_sheet"].map(status_priority)

# pastikan tanggal valid
df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

# urutkan: IMEI sama → status terburuk → tanggal terbaru
df_sorted = df.sort_values(
    by=["imei", "status_rank", "tanggal"],
    ascending=[True, False, False]
)

# ambil 1 baris per IMEI
master_df = df_sorted.drop_duplicates(
    subset=["imei"],
    keep="first"
)

# buang kolom bantu
master_df = master_df.drop(columns=["status_rank"])

print("DATA SETELAH DEDUPE")
print("Baris :", len(master_df))
print()

# simpan hasil
master_df.to_excel(
    OUTPUT_DIR / "gadai_master_transaction.xlsx",
    index=False
)

master_df.to_csv(
    OUTPUT_DIR / "gadai_master_transaction.csv",
    index=False
)

print("SELESAI")
print("File output:")
print(" - gadai_master_transaction.xlsx")
print(" - gadai_master_transaction.csv")
