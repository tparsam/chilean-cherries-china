"""
Combines Chile-exporter and China-importer data, fills gaps with whichever side reported,
then produces tidy tables + initial charts for the term paper.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

OUT = "/Users/tanviparsam/Downloads/University/Semester4/Macroeconomics-Term_Paper"

# --- combine all cherry HS codes from each side, take total per (year, partner) ---
chile_raw = pd.read_csv(f"{OUT}/cherries_raw.csv")
china_raw = pd.read_csv(f"{OUT}/cherries_mirror_raw.csv")

chile_agg = (chile_raw.groupby(["year", "partner_name"], as_index=False)
                       .agg(chile_side_usd=("value_usd", "sum"),
                            chile_side_kg=("net_wgt_kg", "sum")))
china_agg = (china_raw.groupby(["year", "partner_name"], as_index=False)
                       .agg(china_side_usd=("value_usd", "sum"),
                            china_side_kg=("net_wgt_kg", "sum")))

# remap so both have a "China" (bilateral) and "World" (Chile->world or China<-world)
chile_agg = chile_agg[chile_agg["partner_name"].isin(["China", "World"])]
china_agg["partner_name"] = china_agg["partner_name"].map({"Chile": "China", "World": "World_imports_china"})

merged = chile_agg.merge(china_agg, on=["year", "partner_name"], how="outer")

# bilateral Chile <-> China: prefer chile_side, fallback to china_side
bi = merged[merged["partner_name"] == "China"].copy()
bi["bilateral_usd"] = bi["chile_side_usd"].where(bi["chile_side_usd"] > 0, bi["china_side_usd"])
bi["bilateral_kg"] = bi["chile_side_kg"].where(bi["chile_side_kg"] > 0, bi["china_side_kg"])
bi = bi[["year", "bilateral_usd", "bilateral_kg", "chile_side_usd", "china_side_usd"]]

# Chile -> world total
cw = chile_agg[chile_agg["partner_name"] == "World"][["year", "chile_side_usd", "chile_side_kg"]].rename(
    columns={"chile_side_usd": "chile_to_world_usd", "chile_side_kg": "chile_to_world_kg"})

# China <- world total
chw = china_agg[china_agg["partner_name"] == "World_imports_china"][["year", "china_side_usd"]].rename(
    columns={"china_side_usd": "china_from_world_usd"})

summary = bi.merge(cw, on="year", how="outer").merge(chw, on="year", how="outer").sort_values("year")
summary["china_share_of_chile_exports_pct"] = 100 * summary["bilateral_usd"] / summary["chile_to_world_usd"]
summary["chile_share_of_china_imports_pct"] = 100 * summary["bilateral_usd"] / summary["china_from_world_usd"]
summary.to_csv(f"{OUT}/cherries_combined.csv", index=False)
print("Saved cherries_combined.csv")
print(summary.to_string(index=False))

# --- macro ---
macro = pd.read_csv(f"{OUT}/macro_summary.csv")
china_macro = macro[macro["country"] == "China"][["year", "GDP_per_capita_USD", "GDP_growth_pct", "Imports_pct_GDP"]]
chile_macro = macro[macro["country"] == "Chile"][["year", "GDP_per_capita_USD", "Exports_pct_GDP", "GDP_USD"]]

# --- CHART 1: Chile-China bilateral cherry trade, value over time ---
fig, ax = plt.subplots(figsize=(10, 5.5))
data1 = summary.dropna(subset=["bilateral_usd"]).copy()
data1["bilateral_usd_m"] = data1["bilateral_usd"] / 1e6
ax.bar(data1["year"], data1["bilateral_usd_m"], color="#a4243b", edgecolor="white")
ax.set_title("Chile's cherry exports to China, 2005–2024", fontsize=13, fontweight="bold")
ax.set_ylabel("Value (USD, millions)")
ax.set_xlabel("Year")
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
for _, r in data1.iterrows():
    if r["bilateral_usd_m"] > 200:
        ax.text(r["year"], r["bilateral_usd_m"] + 50, f"${r['bilateral_usd_m']:.0f}M",
                ha="center", fontsize=8, color="#444")
ax.text(2006.2, ax.get_ylim()[1]*0.92, "China-Chile FTA\n(in force 2006)", fontsize=8, color="#555",
        bbox=dict(boxstyle="round", fc="#f4ecd8", ec="#aaa"))
plt.tight_layout()
plt.savefig(f"{OUT}/chart1_bilateral_value.png", dpi=180)
plt.close()
print("Saved chart1_bilateral_value.png")

# --- CHART 2: China's share of Chile's cherry exports AND Chile's share of China's imports ---
fig, ax = plt.subplots(figsize=(10, 5.5))
d = summary.dropna(subset=["china_share_of_chile_exports_pct"], how="all")
d2a = d.dropna(subset=["china_share_of_chile_exports_pct"])
d2a = d2a[d2a["china_share_of_chile_exports_pct"].between(0, 100)]
d2b = d.dropna(subset=["chile_share_of_china_imports_pct"])
d2b = d2b[d2b["chile_share_of_china_imports_pct"].between(0, 100)]
ax.plot(d2a["year"], d2a["china_share_of_chile_exports_pct"], "o-", color="#a4243b",
        linewidth=2, label="China's share of Chile's cherry exports")
ax.plot(d2b["year"], d2b["chile_share_of_china_imports_pct"], "s--", color="#1e6091",
        linewidth=2, label="Chile's share of China's cherry imports")
ax.set_title("A two-way bilateral lock-in", fontsize=13, fontweight="bold")
ax.set_ylabel("%")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
ax.legend(loc="lower right", frameon=False)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/chart2_shares.png", dpi=180)
plt.close()
print("Saved chart2_shares.png")

# --- CHART 3: Cherry trade vs China's GDP per capita ---
fig, ax = plt.subplots(figsize=(10, 5.5))
m = summary.merge(china_macro, on="year", how="inner").dropna(
    subset=["bilateral_usd", "GDP_per_capita_USD"])
ax2 = ax.twinx()
ax.bar(m["year"], m["bilateral_usd"]/1e6, color="#a4243b", alpha=0.85, label="Cherry imports from Chile ($M)")
ax2.plot(m["year"], m["GDP_per_capita_USD"], "o-", color="#264653", linewidth=2,
         label="China GDP per capita (USD)")
ax.set_ylabel("Cherry imports from Chile (USD millions)", color="#a4243b")
ax2.set_ylabel("China GDP per capita (USD)", color="#264653")
ax.set_title("Chinese incomes rise, Chilean cherries follow", fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/chart3_vs_gdp.png", dpi=180)
plt.close()
print("Saved chart3_vs_gdp.png")

# --- Final compact table ---
final = summary[["year", "bilateral_usd", "chile_to_world_usd", "china_from_world_usd",
                 "china_share_of_chile_exports_pct", "chile_share_of_china_imports_pct"]].copy()
final.columns = ["year", "Chile->China (USD)", "Chile->World (USD)", "China<-World (USD)",
                 "China % of Chile exports", "Chile % of China imports"]
final.to_csv(f"{OUT}/cherries_FINAL.csv", index=False)
print("\n=== FINAL TABLE ===")
print(final.to_string(index=False))
