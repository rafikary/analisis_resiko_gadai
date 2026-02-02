import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "output" / "gadai_master_transaction.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

df = pd.read_excel(DATA_PATH)

print("DATA TRANSAKSI")
print("Total baris :", len(df))
print()

# buat flag risiko
df["is_late"] = df["status_sheet"].isin(["Late", "Auction"])
df["is_auction"] = df["status_sheet"] == "Auction"

# simpan dataset dengan fitur risiko
df.to_excel(
    OUTPUT_DIR / "gadai_transaction_with_risk.xlsx",
    index=False
)

# agregasi per outlet
outlet_risk = (
    df.groupby("outlet")
    .agg(
        total_transaksi=("imei", "count"),
        total_late=("is_late", "sum"),
        total_auction=("is_auction", "sum")
    )
    .reset_index()
)

outlet_risk["late_ratio"] = outlet_risk["total_late"] / outlet_risk["total_transaksi"]
outlet_risk["auction_ratio"] = outlet_risk["total_auction"] / outlet_risk["total_transaksi"]

# urutkan outlet paling berisiko
outlet_risk = outlet_risk.sort_values(
    by=["auction_ratio", "late_ratio"],
    ascending=False
)

# simpan hasil
outlet_risk.to_excel(
    OUTPUT_DIR / "outlet_risk_summary.xlsx",
    index=False
)

print("SELESAI")
print("Output:")
print("- gadai_transaction_with_risk.xlsx")
print("- outlet_risk_summary.xlsx")
