import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "output" / "outlet_risk_summary.xlsx"

df = pd.read_excel(DATA_PATH)

top_outlet = df.sort_values(
    by=["auction_ratio", "late_ratio"],
    ascending=False
).head(10)

plt.figure()
plt.bar(top_outlet["outlet"], top_outlet["auction_ratio"])
plt.xticks(rotation=45, ha="right")
plt.title("Top 10 Outlet dengan Rasio Auction Tertinggi")
plt.ylabel("Auction Ratio")
plt.xlabel("Nama Outlet")
plt.tight_layout()
plt.show()
