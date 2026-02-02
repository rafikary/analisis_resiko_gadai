"""
Data Analyzer Module
Fungsi: Analisis dan agregasi data per outlet
"""
import pandas as pd
from src.utils import print_section


def analyze_data(df, col_mapping):
    """
    Analisis data dan buat summary per outlet
    
    Args:
        df (pd.DataFrame): Data yang sudah diproses
        col_mapping (dict): Mapping kolom
        
    Returns:
        tuple: (summary_status, outlet_summary)
    """
    print_section("STEP 3: ANALYZING DATA")
    
    # Summary status transaksi
    summary_status = df["status_transaksi"].value_counts()
    
    # Summary per outlet (OPTIMIZED - one aggregation)
    outlet_col = col_mapping["outlet"]
    pinjaman_col = col_mapping["pinjaman"]
    
    outlet_summary = (
        df.groupby(outlet_col, observed=True)
        .agg(
            total_transaksi=(pinjaman_col, "count"),
            total_pinjaman=(pinjaman_col, "sum"),
            rata_rasio=("rasio_pinjaman", "mean"),
            transaksi_berisiko=("is_high_risk", "sum")
        )
    )
    
    outlet_summary["persen_berisiko"] = (
        outlet_summary["transaksi_berisiko"] / outlet_summary["total_transaksi"] * 100
    )
    
    outlet_summary = outlet_summary.sort_values("total_pinjaman", ascending=False)
    
    print(f"\n✓ Analisis {len(outlet_summary)} outlet selesai")
    
    return summary_status, outlet_summary
