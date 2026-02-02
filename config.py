"""
Konfigurasi Global untuk Sistem Analisis Gadai
"""
from pathlib import Path

# Path Project
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# File Input/Output
INPUT_FILE = DATA_DIR / "gadai_raw.xlsx"
MASTER_DATASET = OUTPUT_DIR / "gadai_master_dataset.csv"
MASTER_TRANSACTION = OUTPUT_DIR / "gadai_master_transaction.csv"
PROCESSED_FILE = OUTPUT_DIR / "gadai_processed.csv"
OUTLET_SUMMARY = OUTPUT_DIR / "outlet_summary.csv"
OUTLET_RISK = OUTPUT_DIR / "outlet_risk_summary.csv"
SUMMARY_TEXT = OUTPUT_DIR / "summary.txt"

# Sheet Data Operasional
DATA_SHEETS = ["Outstanding", "Active", "On-Due", "Late", "Auction"]

# Prioritas Status (untuk deduplication)
STATUS_PRIORITY = {
    "Auction": 5,
    "Late": 4,
    "On-Due": 3,
    "Active": 2,
    "Outstanding": 1
}

# Mapping Kolom Standar
COLUMN_MAPPING = {
    "no": ["no"],
    "company": ["company"],
    "area": ["area"],
    "outlet": ["outlet", "cabang"],
    "sbg": ["sbg"],
    "imei": ["imei", "no seri"],
    "produk": ["produk"],
    "tanggal": ["tanggal"],
}

# Threshold Risiko
RISK_THRESHOLD = {
    "rasio_pinjaman": 0.9,  # > 90% dianggap berisiko
    "late_ratio": 0.3,       # > 30% late dianggap outlet berisiko
    "auction_ratio": 0.2     # > 20% auction dianggap outlet sangat berisiko
}

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)
