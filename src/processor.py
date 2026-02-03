"""
Data Processor Module
Fungsi: Processing data, feature engineering, dan analisis
"""
import pandas as pd
import sys
from config import RISK_THRESHOLD
from src.utils import find_column, clean_numeric, clean_datetime, print_section


def process_data(df):
    """
    Process data: validasi, type casting, feature engineering
    
    Args:
        df (pd.DataFrame): Data yang akan diproses
        
    Returns:
        pd.DataFrame: Data yang sudah diproses
    """
    print_section("STEP 2: PROCESSING DATA")
    
    # Auto-detect kolom penting (sudah dalam format normalized: lowercase + underscore)
    col_pinjaman = find_column(df, ["pokok_pinjaman", "pinjaman", "nilai_pinjam", "loan", "outstanding_pokok"])
    col_jaminan = find_column(df, ["nilai_jaminan", "jaminan_pokok", "pokok", "jaminan"])
    col_terbayar = find_column(df, ["pokok_terbayar", "terbayar"])
    col_tanggal = find_column(df, ["tanggal_gadai", "tanggal"])
    col_tanggal_jt = find_column(df, ["tanggal_jt", "jt", "jatuh_tempo"])
    col_outlet = find_column(df, ["outlet", "cabang"])
    
    col_mapping = {
        "pinjaman": col_pinjaman,
        "jaminan": col_jaminan,
        "terbayar": col_terbayar,
        "tanggal": col_tanggal,
        "tanggal_jt": col_tanggal_jt,
        "outlet": col_outlet,
    }
    
    print("\n✓ Kolom terdeteksi:")
    for key, col in col_mapping.items():
        status = "✓" if col else "✗"
        print(f"  {status} {key:15} -> {col}")
    
    # Validasi kolom wajib
    missing = [k for k, v in col_mapping.items() if v is None]
    if missing:
        print(f"\n✗ ERROR: Kolom tidak ditemukan: {missing}")
        sys.exit(1)
    
    # Type casting
    print("\n✓ Type casting...")
    df[col_mapping["tanggal"]] = pd.to_datetime(df[col_mapping["tanggal"]], errors='coerce')
    df[col_mapping["tanggal_jt"]] = pd.to_datetime(df[col_mapping["tanggal_jt"]], errors='coerce')
    df[col_mapping["pinjaman"]] = pd.to_numeric(df[col_mapping["pinjaman"]], errors='coerce')
    df[col_mapping["jaminan"]] = pd.to_numeric(df[col_mapping["jaminan"]], errors='coerce')
    df[col_mapping["terbayar"]] = pd.to_numeric(df[col_mapping["terbayar"]], errors='coerce')
    
    # Feature engineering
    print("✓ Feature engineering...")
    df["lama_gadai_hari"] = (df[col_mapping["tanggal_jt"]] - df[col_mapping["tanggal"]]).dt.days
    df["outstanding_pokok"] = df[col_mapping["jaminan"]] - df[col_mapping["terbayar"]]
    df["rasio_pinjaman"] = df[col_mapping["pinjaman"]] / df[col_mapping["jaminan"]]
    
    # Status transaksi - OPTIMIZED (vectorized, no apply)
    today = pd.Timestamp.today()
    df["status_transaksi"] = "aktif"
    df.loc[df["outstanding_pokok"] <= 0, "status_transaksi"] = "lunas"
    df.loc[(df["outstanding_pokok"] > 0) & (df[col_mapping["tanggal_jt"]] < today), "status_transaksi"] = "lewat_jt"
    
    # Flag risiko
    df["is_high_risk"] = df["rasio_pinjaman"] > RISK_THRESHOLD["rasio_pinjaman"]
    
    print("  ✓ Semua feature berhasil dibuat")
    
    return df, col_mapping
