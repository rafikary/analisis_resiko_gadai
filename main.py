"""
========================================
SISTEM ANALISIS GADAI
========================================
Sistem terintegrasi untuk analisis data gadai

Modul:
1. Loader      - Load dan normalisasi data
2. Processor   - Processing dan feature engineering  
3. Analyzer    - Analisis dan agregasi
4. Reporter    - Generate laporan

Author: Big Data Team
Date: 2026
========================================
"""
import sys
from datetime import datetime
from src.loader import load_and_normalize
from src.processor import process_data
from src.analyzer import analyze_data
from src.reporter import save_reports


def main():
    """Main entry point untuk sistem analisis gadai"""
    
    print("\n" + "=" * 60)
    print("  SISTEM ANALISIS GADAI")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    try:
        # Step 1: Load data
        df = load_and_normalize()
        
        # Step 2: Process data
        df, col_mapping = process_data(df)
        
        # Step 3: Analyze data
        summary_status, outlet_summary = analyze_data(df, col_mapping)
        
        # Step 4: Save reports
        save_reports(df, summary_status, outlet_summary)
        
        # Summary akhir
        print("\n" + "=" * 60)
        print("  ✓ PROSES SELESAI")
        print("=" * 60)
        print(f"\nTotal data diproses  : {len(df):,} transaksi")
        print(f"Total outlet         : {df[col_mapping['outlet']].nunique()} outlet")
        print(f"Transaksi berisiko   : {df['is_high_risk'].sum():,} ({df['is_high_risk'].sum()/len(df)*100:.1f}%)")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
