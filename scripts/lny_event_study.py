"""
Three additional analyses around the Lunar New Year hypothesis:
  1. Event study: align every year to LNY month, see the universal pulse
  2. Concentration measures: Herfindahl index, effective number of months
  3. Counterfactual: same product (Chilean cherries) but a non-LNY market (USA),
     to test whether the seasonality is intrinsic to cherries or specific to China.
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

OUT = "/Users/tanviparsam/Downloads/University/Semester4/Macroeconomics-Term_Paper"
URL = "https://comtradeapi.un.org/public/v1/preview/C/M/HS"

LNY_MONTH = {2018: 2, 2019: 2, 2020: 1, 2021: 2, 2022: 2, 2023: 1, 2024: 2, 2025: 1}
LNY_DAY = {2018: 47, 2019: 36, 2020: 25, 2021: 43, 2022: 32, 2023: 22, 2024: 41, 2025: 29}  # day-of-year

# --- 1+2: use existing monthly China-from-Chile data ---
ch = pd.read_csv(f"{OUT}/cherries_monthly.csv")
ch["lny_month"] = ch["year"].map(LNY_MONTH)
ch["months_from_lny"] = ch["month"] - ch["lny_month"]
# wrap: trade in Nov/Dec for an LNY in Feb is at -3/-2; trade in Oct after LNY in Jan is at +9 (drop these)
ch["months_from_lny"] = ch["months_from_lny"].where(ch["months_from_lny"].between(-6, 6),
                                                     ch["months_from_lny"] - 12)

# Event-study aggregation
event = (ch.groupby("months_from_lny", as_index=False)
           .agg(mean_val_m=("value_usd", "mean"),
                total_val=("value_usd", "sum"),
                n_obs=("value_usd", "size")))
event["mean_val_m"] = event["mean_val_m"] / 1e6
event["share_of_total"] = 100 * event["total_val"] / event["total_val"].sum()
print("Event study (months relative to LNY):")
print(event.to_string(index=False))

# Concentration metrics: HHI per year + effective number of months
def hhi(s):
    p = s / s.sum()
    return (p**2).sum()

conc = []
for y, g in ch.groupby("year"):
    monthly = g.groupby("month")["value_usd"].sum().reindex(range(1, 13), fill_value=0)
    if monthly.sum() == 0:
        continue
    h = hhi(monthly)
    eff = 1 / h if h > 0 else np.nan
    top_month_val = monthly.max() / monthly.sum() * 100
    conc.append({"year": y, "total_usd": monthly.sum(), "HHI": h,
                 "effective_n_months": eff, "peak_month": int(monthly.idxmax()),
                 "peak_month_share_pct": top_month_val})
conc = pd.DataFrame(conc)
print("\nConcentration (Herfindahl index across 12 months, lower = more even):")
print(conc.round(3).to_string(index=False))
print("\nReference: a perfectly uniform 12-month distribution has HHI = 0.083, effective months = 12.")
print(f"Average effective months for Chile->China cherries: {conc['effective_n_months'].mean():.2f}")

# --- 3: counterfactual — Chile's cherry exports to USA, monthly ---
print("\nPulling Chile -> USA monthly cherry exports (counterfactual: no LNY)...")
us_rows = []
for year in range(2020, 2025):
    for month in range(1, 13):
        period = f"{year}{month:02d}"
        params = {"reporterCode": 152, "period": period, "partnerCode": 842,
                  "cmdCode": "080929", "flowCode": "X"}
        try:
            j = requests.get(URL, params=params, timeout=30).json()
            for d in j.get("data") or []:
                us_rows.append({"year": year, "month": month, "period": period,
                                "value_usd": d.get("primaryValue") or d.get("fobvalue") or 0})
        except Exception as e:
            print(f"  ! {period}: {e}")
        time.sleep(0.18)
    print(f"  done USA {year}")

us = pd.DataFrame(us_rows)
us.to_csv(f"{OUT}/cherries_chile_to_usa_monthly.csv", index=False)
print(f"\nUSA: {len(us)} rows, total = ${us['value_usd'].sum()/1e6:,.1f}M")
print(us.groupby("year")["value_usd"].sum().apply(lambda x: f"${x/1e6:.1f}M").to_string())

# Compare monthly distributions
def monthly_dist(df_):
    s = df_.groupby("month")["value_usd"].sum().reindex(range(1, 13), fill_value=0)
    return s / s.sum() * 100

cn_dist = monthly_dist(ch[ch["year"].between(2020, 2024)])
us_dist = monthly_dist(us)
print("\nMonthly distribution (% of annual, 2020-2024 avg):")
print(pd.DataFrame({"China_market_%": cn_dist, "USA_market_%": us_dist}).round(1).to_string())

# Concentration comparison
def hhi_dist(d):
    p = d / 100
    return (p**2).sum()
print(f"\nHHI (China market): {hhi_dist(cn_dist):.3f}  ->  effective months = {1/hhi_dist(cn_dist):.2f}")
print(f"HHI (USA market):   {hhi_dist(us_dist):.3f}  ->  effective months = {1/hhi_dist(us_dist):.2f}")

# --- VISUALISATION: 4-panel ---
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# (a) Event study
ax = axes[0, 0]
e_sorted = event.sort_values("months_from_lny")
ax.bar(e_sorted["months_from_lny"], e_sorted["share_of_total"], color="#a4243b", edgecolor="white")
ax.axvline(0, color="#1e6091", linestyle="--", linewidth=1.5, label="Lunar New Year month")
ax.set_xlabel("Months relative to Lunar New Year")
ax.set_ylabel("% of total trade across all years")
ax.set_title("(a) Event study — every year's trade collapses to the LNY pulse",
             fontweight="bold", fontsize=11)
for _, r in e_sorted.iterrows():
    if r["share_of_total"] > 5:
        ax.text(r["months_from_lny"], r["share_of_total"] + 0.7, f"{r['share_of_total']:.1f}%",
                ha="center", fontsize=9)
ax.legend(loc="upper right", frameon=False)
ax.set_xticks(range(int(e_sorted["months_from_lny"].min()), int(e_sorted["months_from_lny"].max())+1))
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# (b) HHI / effective months over time
ax = axes[0, 1]
ax2 = ax.twinx()
ax.bar(conc["year"], conc["effective_n_months"], color="#a4243b", alpha=0.85, label="Effective months (1/HHI)")
ax.axhline(12, color="#264653", linestyle="--", linewidth=1, label="Uniform = 12")
ax2.plot(conc["year"], conc["peak_month_share_pct"], "o-", color="#1e6091", linewidth=2, label="Peak month % of year")
ax.set_ylabel("Effective months", color="#a4243b")
ax2.set_ylabel("Peak month % of annual", color="#1e6091")
ax.set_xlabel("Year")
ax.set_title("(b) Concentration: trade compressed to ~3 effective months",
             fontweight="bold", fontsize=11)
ax.set_ylim(0, 13)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=9)

# (c) China vs USA monthly distribution
ax = axes[1, 0]
months = np.arange(1, 13)
import calendar
mnames = [calendar.month_abbr[m] for m in months]
width = 0.4
ax.bar(months - width/2, cn_dist.values, width, color="#a4243b", label=f"To China (HHI={hhi_dist(cn_dist):.2f})")
ax.bar(months + width/2, us_dist.values, width, color="#1e6091", label=f"To USA (HHI={hhi_dist(us_dist):.2f})")
ax.set_xticks(months)
ax.set_xticklabels(mnames)
ax.set_ylabel("% of annual trade")
ax.set_title("(c) Same cherries, different destinations — only China shows the LNY pulse",
             fontweight="bold", fontsize=11)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# (d) China - USA monthly share gap: isolates the LNY effect
ax = axes[1, 1]
gap = (cn_dist - us_dist).reindex(range(1, 13)).fillna(0)
colors_gap = ["#a4243b" if v > 0 else "#1e6091" for v in gap.values]
ax.bar(range(1, 13), gap.values, color=colors_gap, edgecolor="white")
ax.axhline(0, color="black", linewidth=0.6)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(mnames)
ax.set_ylabel("% share of annual (China minus USA, pp)")
ax.set_title("(d) Where the LNY effect lives: China loads Jan, USA loads Dec",
             fontweight="bold", fontsize=11)
for i, v in enumerate(gap.values, start=1):
    if abs(v) > 3:
        ax.text(i, v + (1.2 if v > 0 else -2.5), f"{v:+.0f}pp", ha="center", fontsize=9,
                color="#a4243b" if v > 0 else "#1e6091", fontweight="bold")
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

plt.suptitle("Empirical evidence: Chilean cherry exports are a Lunar New Year industry",
             fontsize=13, fontweight="bold", y=1.00)
plt.tight_layout()
plt.savefig(f"{OUT}/chart8_lny_evidence.png", dpi=180)
plt.close()
print("\nSaved chart8_lny_evidence.png")
