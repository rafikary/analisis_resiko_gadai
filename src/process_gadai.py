import pandas as pd
from pathlib import Path
import sys

# path project
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "gadai_raw.xlsx"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# load data
df = pd.read_excel(DATA_PATH)
print("Data loaded:", df.shape)

# rapikan nama kolom
df.columns = (
    df.columns
    .astype(str)
    .str.lower()
    .str.strip()
    .str.replace("\n", " ")
    .str.replace("  ", " ")
    .str.replace("/", "_")
)

print("\nKolom yang terbaca:")
for c in df.columns:
    print("-", c)

# helper cari kolom berdasarkan keyword
def find_column(keywords):
    for col in df.columns:
        for kw in keywords:
            if kw in col:
                return col
    return None

# auto-detect kolom penting
col_pinjaman = find_column(["pokok pinjaman", "pinjaman"])
col_jaminan = find_column(["nilai jaminan", "jaminan"])
col_terbayar = find_column(["pokok terbayar", "terbayar"])
col_tanggal = find_column(["tanggal gadai", "tanggal"])
col_tanggal_jt = find_column(["jt", "jatuh tempo"])
col_outlet = find_column(["outlet", "cabang"])

required = {
    "pinjaman": col_pinjaman,
    "jaminan": col_jaminan,
    "terbayar": col_terbayar,
    "tanggal": col_tanggal,
    "tanggal_jt": col_tanggal_jt,
    "outlet": col_outlet,
}

print("\nHasil auto-detect kolom:")
for k, v in required.items():
    print(f"{k} -> {v}")

# validasi kolom wajib
missing = [k for k, v in required.items() if v is None]
if missing:
    print("\nERROR: kolom tidak ditemukan:", missing)
    sys.exit(1)

# type casting
df[col_tanggal] = pd.to_datetime(df[col_tanggal], errors="coerce")
df[col_tanggal_jt] = pd.to_datetime(df[col_tanggal_jt], errors="coerce")

for col in [col_pinjaman, col_jaminan, col_terbayar]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# feature engineering
df["lama_gadai_hari"] = (df[col_tanggal_jt] - df[col_tanggal]).dt.days
df["outstanding_pokok"] = df[col_jaminan] - df[col_terbayar]
df["ltv"] = (df[col_pinjaman] / df[col_jaminan]) * 100  # Loan to Value dalam persen

# Status transaksi
def status_transaksi(row):
    if row["outstanding_pokok"] <= 0:
        return "lunas"
    elif pd.notnull(row[col_tanggal_jt]) and row[col_tanggal_jt] < pd.Timestamp.today():
        return "lewat_jt"
    else:
        return "aktif"

df["status_transaksi"] = df.apply(status_transaksi, axis=1)

# LOGIKA RISIKO YANG LEBIH AKURAT
def kategori_risiko(row):
    """
    Menentukan risiko berdasarkan multiple factors:
    - Lewat jatuh tempo = TINGGI
    - LTV > 100% (pinjaman > nilai barang) = TINGGI  
    - Outstanding tinggi + durasi lama = SEDANG
    - Lainnya = RENDAH
    """
    # Risiko TINGGI: Sudah lewat jatuh tempo
    if row["status_transaksi"] == "lewat_jt":
        return "tinggi"
    
    # Risiko TINGGI: LTV lebih dari 100% (overlending - pinjaman melebihi nilai barang)
    if row["ltv"] > 100:
        return "tinggi"
    
    # Risiko SEDANG: Outstanding masih tinggi (>70%) DAN durasi gadai > 6 bulan
    if row["status_transaksi"] == "aktif":
        persen_outstanding = (row["outstanding_pokok"] / row[col_jaminan]) * 100 if row[col_jaminan] > 0 else 0
        durasi_lama = row["lama_gadai_hari"] > 180  # 6 bulan
        
        if persen_outstanding > 70 and durasi_lama:
            return "sedang"
    
    # Default: Risiko RENDAH
    return "rendah"

df["kategori_risiko"] = df.apply(kategori_risiko, axis=1)

# ringkasan analisis
summary_status = df["status_transaksi"].value_counts()
summary_risiko = df["kategori_risiko"].value_counts()

outlet_summary = (
    df.groupby(col_outlet)
      .agg(
          total_transaksi=(col_pinjaman, "count"),
          total_pinjaman=(col_pinjaman, "sum"),
          rata_ltv=("ltv", "mean"),
          transaksi_berisiko=("kategori_risiko", lambda x: (x == "tinggi").sum()),
          transaksi_sedang=("kategori_risiko", lambda x: (x == "sedang").sum()),
          persen_berisiko=("kategori_risiko", lambda x: (x == "tinggi").sum() / len(x) * 100 if len(x) > 0 else 0)
      )
      .sort_values("persen_berisiko", ascending=False)
)

# simpan output
df.to_csv(OUTPUT_DIR / "gadai_processed.csv", index=False)
outlet_summary.to_csv(OUTPUT_DIR / "outlet_summary.csv")

with open(OUTPUT_DIR / "summary.txt", "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("RINGKASAN ANALISIS RISIKO GADAI\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("STATUS TRANSAKSI\n")
    f.write("-" * 40 + "\n")
    f.write(summary_status.to_string())
    f.write("\n\n")
    
    f.write("KATEGORI RISIKO\n")
    f.write("-" * 40 + "\n")
    f.write(summary_risiko.to_string())
    f.write("\n\n")
    
    f.write("PENJELASAN LOGIKA RISIKO:\n")
    f.write("-" * 40 + "\n")
    f.write("TINGGI  : Lewat jatuh tempo ATAU LTV > 100%\n")
    f.write("SEDANG  : Outstanding >70% DAN durasi >6 bulan\n")
    f.write("RENDAH  : Kondisi normal lainnya\n")
    f.write("\nLTV (Loan to Value) = (Pinjaman / Nilai Barang) x 100%\n")

print("\nProcessing selesai. Output ada di folder output/")
