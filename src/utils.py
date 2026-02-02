"""
Utility Functions untuk Sistem Analisis Gadai
"""
import pandas as pd


def normalize_columns(cols):
    """Normalisasi nama kolom ke format standar"""
    return (
        pd.Series(cols)
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace("\n", " ")
        .str.replace("  ", " ")
        .str.replace("/", "_")
    )


def find_column(df, keywords):
    """Cari kolom berdasarkan keyword"""
    for col in df.columns:
        for kw in keywords:
            if kw in col.lower():
                return col
    return None


def find_header_row(df, max_search=10):
    """Deteksi baris header dalam dataset"""
    for i in range(max_search):
        row = df.iloc[i].astype(str).str.lower().tolist()
        hit = sum(
            any(k in cell for k in ["no", "outlet", "tanggal", "imei"]) 
            for cell in row
        )
        if hit >= 3:
            return i
    return 0


def clean_numeric(series):
    """Konversi kolom ke numeric dengan error handling"""
    return pd.to_numeric(series, errors="coerce")


def clean_datetime(series):
    """Konversi kolom ke datetime dengan error handling"""
    return pd.to_datetime(series, errors="coerce")


def print_section(title):
    """Print section header untuk output yang lebih rapi"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_stats(df, name="Dataset"):
    """Print statistik dasar dataset"""
    print(f"\n{name}")
    print(f"  Baris: {len(df):,}")
    print(f"  Kolom: {len(df.columns)}")
    if "imei" in df.columns:
        print(f"  IMEI Unik: {df['imei'].nunique():,}")
