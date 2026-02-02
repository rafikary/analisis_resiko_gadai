"""
Report Generator Module
Fungsi: Simpan hasil analisis ke file
"""
from config import PROCESSED_FILE, OUTLET_SUMMARY, SUMMARY_TEXT
from src.utils import print_section


def save_reports(df, summary_status, outlet_summary):
    """
    Simpan semua hasil ke file
    
    Args:
        df (pd.DataFrame): Data processed
        summary_status (pd.Series): Summary status transaksi
        outlet_summary (pd.DataFrame): Summary per outlet
    """
    print_section("STEP 4: SAVING REPORTS")
    
    # Simpan data processed
    df.to_csv(PROCESSED_FILE, index=False)
    print(f"✓ Data processed    : {PROCESSED_FILE.name}")
    
    # Simpan outlet summary
    outlet_summary_with_name = outlet_summary.reset_index()
    outlet_summary_with_name.to_csv(OUTLET_SUMMARY, index=False)
    print(f"✓ Outlet summary    : {OUTLET_SUMMARY.name}")
    
    # Simpan summary text
    with open(SUMMARY_TEXT, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  RINGKASAN ANALISIS GADAI\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("STATUS TRANSAKSI\n")
        f.write("-" * 40 + "\n")
        for status, count in summary_status.items():
            pct = count / summary_status.sum() * 100
            f.write(f"{status:12} : {count:6,} ({pct:5.1f}%)\n")
        
        f.write("\n\nTOP 10 OUTLET (Total Pinjaman)\n")
        f.write("-" * 40 + "\n")
        for idx, row in outlet_summary.head(10).iterrows():
            f.write(f"{idx:30} : Rp {row['total_pinjaman']:15,.0f}\n")
        
        f.write("\n\nTOP 10 OUTLET BERISIKO (% Transaksi High Risk)\n")
        f.write("-" * 40 + "\n")
        top_risk = outlet_summary.sort_values("persen_berisiko", ascending=False).head(10)
        for idx, row in top_risk.iterrows():
            f.write(f"{idx:30} : {row['persen_berisiko']:5.1f}%\n")
    
    print(f"✓ Summary text      : {SUMMARY_TEXT.name}")
    print(f"\n✓ Semua laporan tersimpan di folder: {PROCESSED_FILE.parent.name}/")
