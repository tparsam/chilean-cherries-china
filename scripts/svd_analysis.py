"""
SVD of Chile's cherry-export matrix (destinations x years).
M = U Σ V^T
The first singular component should capture the dominant "China shock" pattern;
subsequent components capture orthogonal patterns (Europe, US, recent diversification).
"""
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHARTS = ROOT / "charts"
NOTES = ROOT / "notes"
for p in (DATA, CHARTS, NOTES):
    p.mkdir(exist_ok=True)
URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"

# UN M49 -> readable name mapping for countries that show up in Chile's cherry exports
NAME = {
    156: "China", 344: "Hong Kong", 840: "USA", 842: "USA", 490: "Taiwan",
    660: "Anguilla", 116: "Cambodia", 484: "Mexico", 76: "Brazil",
    32: "Argentina", 604: "Peru", 218: "Ecuador", 170: "Colombia", 188: "Costa Rica",
    591: "Panama", 858: "Uruguay", 600: "Paraguay", 724: "Spain", 250: "France",
    276: "Germany", 528: "Netherlands", 380: "Italy", 826: "UK", 36: "Australia",
    410: "South Korea", 392: "Japan", 158: "Taiwan", 702: "Singapore", 458: "Malaysia",
    764: "Thailand", 360: "Indonesia", 608: "Philippines", 704: "Vietnam", 410: "South Korea",
    784: "UAE", 682: "Saudi Arabia", 376: "Israel", 152: "Chile", 56: "Belgium",
    24: "Angola", 124: "Canada", 554: "New Zealand", 752: "Sweden", 578: "Norway",
    616: "Poland", 643: "Russia", 804: "Ukraine", 792: "Turkey", 818: "Egypt",
    710: "South Africa", 414: "Kuwait", 634: "Qatar", 480: "Mauritius", 408: "North Korea",
    807: "North Macedonia", 16: "American Samoa",
}


def fetch_all_partners(year, cmd):
    params = {"reporterCode": 152, "period": year, "cmdCode": cmd, "flowCode": "X"}
    try:
        r = requests.get(URL, params=params, timeout=40)
        j = r.json()
        return [
            {"year": d["refYear"], "partner": d["partnerCode"],
             "value_usd": d.get("primaryValue") or d.get("fobvalue") or 0,
             "cmd": d["cmdCode"]}
            for d in (j.get("data") or [])
        ]
    except Exception as e:
        print(f"  ! {year}: {e}")
        return []


# Pull 2010-2024 (post-FTA era). For 2010-2011 use old HS code 080920; from 2012 use 080929.
rows = []
for y in range(2010, 2012):
    print(f"Chile -> all partners cherries (080920) {y}")
    rows += fetch_all_partners(y, "080920")
    time.sleep(0.3)
for y in range(2012, 2025):
    print(f"Chile -> all partners cherries (080929) {y}")
    rows += fetch_all_partners(y, "080929")
    time.sleep(0.3)

df = pd.DataFrame(rows)
df = df[df["partner"] != 0]  # drop "World" aggregate
df["partner_name"] = df["partner"].map(NAME).fillna(df["partner"].astype(str))
df.to_csv(DATA / "cherries_all_destinations.csv", index=False)
print(f"\nSaved cherries_all_destinations.csv ({len(df)} rows, {df['partner'].nunique()} unique partners)")

# Pivot to (country x year) matrix
M = df.pivot_table(index="partner_name", columns="year", values="value_usd", aggfunc="sum", fill_value=0)
print(f"\nMatrix shape: {M.shape}")
# Keep countries that ever received >$100k of cherries from Chile (drop tiny noise)
M = M[M.max(axis=1) > 1e5]
print(f"After dropping tiny destinations: {M.shape}")
print("\nTop 12 destinations by total 2010-2024 value (USD millions):")
print((M.sum(axis=1).sort_values(ascending=False) / 1e6).head(12).to_string())
M.to_csv(DATA / "cherries_matrix.csv")

# --- SVD ---
X = M.values  # countries x years
U, S, Vt = np.linalg.svd(X, full_matrices=False)
V = Vt.T

# Variance explained
total_var = (S ** 2).sum()
var_explained = (S ** 2) / total_var
cumvar = var_explained.cumsum()

print("\n=== SVD RESULTS ===")
print(f"Matrix size: {X.shape[0]} countries x {X.shape[1]} years")
print(f"Number of singular values: {len(S)}")
print("\nSingular values and variance explained:")
for i in range(min(6, len(S))):
    print(f"  σ_{i+1} = {S[i]:>14,.0f}   var explained = {100*var_explained[i]:5.2f}%   cumulative = {100*cumvar[i]:5.2f}%")

# Interpret first component: countries by their loading
years = list(M.columns)
countries = list(M.index)

c1_country = pd.Series(U[:, 0], index=countries).sort_values(ascending=False)
c1_year = pd.Series(V[:, 0], index=years)
c2_country = pd.Series(U[:, 1], index=countries).sort_values(ascending=False)
c2_year = pd.Series(V[:, 1], index=years)

# Sign convention: flip so that the dominant country has positive loading (interpretable)
if c1_country.iloc[0] < 0:
    U[:, 0] *= -1; V[:, 0] *= -1
    c1_country = pd.Series(U[:, 0], index=countries).sort_values(ascending=False)
    c1_year = pd.Series(V[:, 0], index=years)

print("\nFirst component — top country loadings (dominant pattern):")
print(c1_country.head(10).to_string())
print("\nFirst component — year loadings (how this pattern evolves):")
print(c1_year.to_string())

print("\nSecond component — top + bottom country loadings (orthogonal pattern):")
print("  Top: " + ", ".join(f"{k}({v:+.2f})" for k, v in c2_country.head(5).items()))
print("  Bot: " + ", ".join(f"{k}({v:+.2f})" for k, v in c2_country.tail(5).items()))

# --- visualisations ---
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# (a) Variance explained / scree plot
ax = axes[0, 0]
k = min(8, len(S))
ax.bar(range(1, k+1), 100*var_explained[:k], color="#a4243b", alpha=0.85, edgecolor="white")
ax.plot(range(1, k+1), 100*cumvar[:k], "o-", color="#264653", label="Cumulative %")
for i in range(k):
    ax.text(i+1, 100*var_explained[i] + 1, f"{100*var_explained[i]:.1f}%", ha="center", fontsize=9)
ax.set_xlabel("Singular component")
ax.set_ylabel("% of variance explained")
ax.set_title("(a) Scree plot — one component dominates", fontweight="bold")
ax.legend(loc="upper right", frameon=False)
ax.set_ylim(0, 105)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# (b) First-component country loadings (top 12)
ax = axes[0, 1]
top12 = c1_country.head(12)[::-1]  # reverse for nicer horizontal bar
ax.barh(top12.index, top12.values, color="#a4243b", edgecolor="white")
ax.set_xlabel("Loading on 1st singular vector")
ax.set_title("(b) Who is the 1st component? (country loadings)", fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# (c) First-component year pattern
ax = axes[1, 0]
ax.plot(c1_year.index, c1_year.values, "o-", color="#a4243b", linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("Loading on 1st right singular vector")
ax.set_title("(c) When is the 1st component? (year pattern)", fontweight="bold")
ax.grid(alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# (d) Second component country loadings — shows the orthogonal pattern
ax = axes[1, 1]
all2 = pd.concat([c2_country.head(6), c2_country.tail(6)]).sort_values()
colors = ["#1e6091" if v < 0 else "#a4243b" for v in all2.values]
ax.barh(all2.index, all2.values, color=colors, edgecolor="white")
ax.axvline(0, color="black", linewidth=0.6)
ax.set_xlabel("Loading on 2nd singular vector")
ax.set_title("(d) 2nd component — the orthogonal axis", fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

plt.suptitle("SVD of Chile's cherry-export matrix (countries × years), 2010–2024",
             fontsize=13, fontweight="bold", y=1.00)
plt.tight_layout()
plt.savefig(CHARTS / "chart5_svd.png", dpi=180)
plt.close()
print("\nSaved chart5_svd.png")

# --- write a summary text file ---
with open(NOTES / "SVD_RESULTS.md", "w") as f:
    f.write("# SVD Results — Chile's Cherry Export Matrix\n\n")
    f.write(f"- Matrix: {X.shape[0]} destination countries × {X.shape[1]} years (2010-2024)\n")
    f.write(f"- 1st singular value: σ₁ = {S[0]:,.0f}\n")
    f.write(f"- **Variance explained by 1st component: {100*var_explained[0]:.2f}%**\n")
    f.write(f"- Cumulative variance from first 3 components: {100*cumvar[2]:.2f}%\n\n")
    f.write("## First component (the 'China shock')\n")
    f.write("### Top country loadings:\n")
    for k, v in c1_country.head(8).items():
        f.write(f"- {k}: {v:+.3f}\n")
    f.write("\n### Year loadings (temporal pattern):\n")
    for k, v in c1_year.items():
        f.write(f"- {k}: {v:+.3f}\n")
    f.write("\n## Second component (orthogonal pattern)\n")
    f.write("### Top loadings:\n")
    for k, v in c2_country.head(5).items():
        f.write(f"- {k}: {v:+.3f}\n")
    f.write("### Bottom loadings:\n")
    for k, v in c2_country.tail(5).items():
        f.write(f"- {k}: {v:+.3f}\n")
print("Saved SVD_RESULTS.md")
