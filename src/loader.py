"""
Data Loader Module
Fungsi: Load dan normalisasi data dari file Excel
"""
import pandas as pd
from config import INPUT_FILE, OUTPUT_DIR
from src.utils import normalize_columns, print_section, print_stats


def load_and_normalize():
    """
    Load data dari Excel dan normalisasi nama kolom
    
    Returns:
        pd.DataFrame: Data yang sudah dinormalisasi
    """
    print_section("STEP 1: LOADING DATA")
    
    # Load data
    df = pd.read_excel(INPUT_FILE)
    print(f"✓ Data loaded dari: {INPUT_FILE.name}")
    print_stats(df, "Data Awal")
    
    # Normalisasi kolom
    df.columns = normalize_columns(df.columns)
    
    print("\n✓ Kolom berhasil dinormalisasi")
    print(f"  Jumlah kolom: {len(df.columns)}")
    
    return df
