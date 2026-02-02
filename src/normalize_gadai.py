import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "gadai_raw.xlsx"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# sheet yang dianggap data operasional
DATA_SHEETS = [
    "Outstanding",
    "Active",
    "On-Due",
    "Late",
    "Auction"
]

# schema standar (kolom final yang kita mau)
STANDARD_COLUMNS = {
    "no": ["no"],
    "company": ["company"],
    "area": ["area"],
    "outlet": ["outlet", "cabang"],
    "sbg": ["sbg"],
    "imei": ["imei", "no seri"],
    "produk": ["produk"],
    "tanggal": ["tanggal"],
}

def normalize_columns(cols):
    return (
        pd.Series(cols)
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace("\n", " ")
        .str.replace("  ", " ")
        .str.replace("/", " ")
    )

def find_header_row(df):
    for i in range(10):
        row = df.iloc[i].astype(str).str.lower().tolist()
        hit = sum(any(k in cell for k in ["no", "outlet", "tanggal", "imei"]) for cell in row)
        if hit >= 3:
            return i
    return 0

def map_columns(df):
    col_map = {}
    for std_col, keywords in STANDARD_COLUMNS.items():
        for col in df.columns:
            for kw in keywords:
                if kw in col:
                    col_map[std_col] = col
                    break
    return col_map

all_data = []

for sheet in DATA_SHEETS:
    print(f"\nProcessing sheet: {sheet}")

    raw = pd.read_excel(DATA_PATH, sheet_name=sheet, header=None)
    header_row = find_header_row(raw)

    df = pd.read_excel(DATA_PATH, sheet_name=sheet, header=header_row)
    df.columns = normalize_columns(df.columns)

    col_map = map_columns(df)

    missing = [k for k in STANDARD_COLUMNS if k not in col_map]
    if missing:
        print(f"  Skip sheet {sheet}, missing columns: {missing}")
        continue

    df_std = df[list(col_map.values())].rename(columns={v: k for k, v in col_map.items()})

    df_std["status_sheet"] = sheet
    all_data.append(df_std)

# gabung semua sheet
if not all_data:
    raise ValueError("Tidak ada sheet valid yang berhasil diproses")

final_df = pd.concat(all_data, ignore_index=True)

# rapikan tipe data
final_df["tanggal"] = pd.to_datetime(final_df["tanggal"], errors="coerce")

# pastikan identifier sebagai string
for col in ["no", "imei", "sbg"]:
    if col in final_df.columns:
        final_df[col] = final_df[col].astype(str)

# simpan hasil ke folder output
final_df.to_csv(
    OUTPUT_DIR / "gadai_master_dataset.csv",
    index=False
)

final_df.to_excel(
    OUTPUT_DIR / "gadai_master_dataset.xlsx",
    index=False
)

print("\nSELESAI")
print("Total baris:", final_df.shape[0])
print("Kolom akhir:", list(final_df.columns))
