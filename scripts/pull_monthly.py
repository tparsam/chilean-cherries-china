"""
Monthly cherry trade: China imports from Chile, 2018-2025.
Used to visualise the Lunar New Year seasonality.
"""
import time
from pathlib import Path
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHARTS = ROOT / "charts"
DATA.mkdir(exist_ok=True); CHARTS.mkdir(exist_ok=True)
URL = "https://comtradeapi.un.org/public/v1/preview/C/M/HS"

# Lunar New Year dates by year (approx — used to anchor the chart)
LNY = {
    2018: "2018-02-16", 2019: "2019-02-05", 2020: "2020-01-25", 2021: "2021-02-12",
    2022: "2022-02-01", 2023: "2023-01-22", 2024: "2024-02-10", 2025: "2025-01-29",
    2026: "2026-02-17",
}

rows = []
for year in range(2018, 2026):
    for month in range(1, 13):
        period = f"{year}{month:02d}"
        params = {"reporterCode": 156, "period": period, "partnerCode": 152,
                  "cmdCode": "080929", "flowCode": "M"}
        try:
            j = requests.get(URL, params=params, timeout=30).json()
            for d in j.get("data") or []:
                rows.append({
                    "year": year, "month": month, "period": period,
                    "value_usd": d.get("primaryValue") or d.get("cifvalue") or 0,
                    "net_wgt_kg": d.get("netWgt") or 0,
                })
            if not (j.get("data")):
                pass  # likely not yet reported
        except Exception as e:
            print(f"  ! {period}: {e}")
        time.sleep(0.2)
    print(f"  done {year}")

df = pd.DataFrame(rows)
df["date"] = pd.to_datetime(df["period"], format="%Y%m")
df = df.sort_values("date").reset_index(drop=True)
df.to_csv(DATA / "cherries_monthly.csv", index=False)
print(f"\nSaved cherries_monthly.csv ({len(df)} rows)")
print(df.groupby("year")["value_usd"].sum().apply(lambda x: f"${x/1e6:,.0f}M").to_string())

# --- Chart 6: monthly time series with LNY markers ---
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.bar(df["date"], df["value_usd"]/1e6, width=22, color="#a4243b", edgecolor="white")
for y, lny in LNY.items():
    if y in df["year"].values:
        ax.axvline(pd.to_datetime(lny), color="#1e6091", linestyle="--", alpha=0.5, linewidth=1)
ax.set_ylabel("Cherry imports from Chile (USD, millions)")
ax.set_xlabel("Month")
ax.set_title("Monthly Chilean cherry imports by China — every spike is Lunar New Year",
             fontsize=13, fontweight="bold")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
# legend
lny_handle = mpatches.Patch(color="#1e6091", alpha=0.5, label="Lunar New Year date (dashed line)")
val_handle = mpatches.Patch(color="#a4243b", label="Monthly imports (USD M)")
ax.legend(handles=[val_handle, lny_handle], loc="upper left", frameon=False)
plt.tight_layout()
plt.savefig(CHARTS / "chart6_monthly_seasonality.png", dpi=180)
plt.close()
print("Saved chart6_monthly_seasonality.png")

# --- Chart 7: stacked seasonality view — monthly share by year ---
fig, ax = plt.subplots(figsize=(11, 6))
import calendar
month_names = [calendar.month_abbr[m] for m in range(1, 13)]
colors = plt.cm.YlOrRd([0.3 + 0.08*i for i in range(8)])
for i, y in enumerate(sorted(df["year"].unique())):
    d = df[df["year"] == y].set_index("month").reindex(range(1, 13), fill_value=0)
    ax.plot(range(1, 13), d["value_usd"]/1e6, "o-", color=colors[i], linewidth=2, label=str(y))
ax.set_xticks(range(1, 13))
ax.set_xticklabels(month_names)
ax.set_ylabel("Cherry imports from Chile (USD, millions)")
ax.set_xlabel("Month of year")
ax.set_title("Seasonality: every year tells the same Lunar New Year story",
             fontsize=13, fontweight="bold")
ax.legend(title="Year", loc="upper center", ncol=4, frameon=False)
ax.grid(alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
# annotate
ax.annotate("Lunar New Year\nshipping window\n(harvest Dec–Feb)",
            xy=(1.5, df.groupby("month")["value_usd"].max().iloc[0]/1e6),
            xytext=(4.5, df["value_usd"].max()/1e6*0.65),
            arrowprops=dict(arrowstyle="->", color="#555"),
            fontsize=10, color="#555",
            bbox=dict(boxstyle="round", fc="#f4ecd8", ec="#aaa"))
plt.tight_layout()
plt.savefig(CHARTS / "chart7_monthly_overlay.png", dpi=180)
plt.close()
print("Saved chart7_monthly_overlay.png")

# --- Quick stat: what % of annual trade falls in Dec-Feb? ---
df["season"] = df["month"].map(lambda m: "Dec-Feb (LNY window)" if m in [12, 1, 2] else "Rest of year")
pct = df.groupby(["year", "season"])["value_usd"].sum().unstack(fill_value=0)
pct["LNY % of year"] = 100 * pct["Dec-Feb (LNY window)"] / pct.sum(axis=1)
pct["Total ($M)"] = pct.sum(axis=1) / 1e6
print("\nShare of annual trade in Dec-Feb (the LNY window):")
print(pct[["Total ($M)", "LNY % of year"]].round(1).to_string())
