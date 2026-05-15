"""
OLS regression: income elasticity of demand for Chilean cherries in China.
Model:  log(cherry_imports_t) = alpha + beta * log(China_GDP_per_capita_t) + eps_t
Slope (beta) is the income elasticity of demand. beta > 1 => luxury good.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

OUT = "/Users/tanviparsam/Downloads/University/Semester4/Macroeconomics-Term_Paper"

# --- assemble the dataset ---
cherries = pd.read_csv(f"{OUT}/cherries_FINAL.csv")
cherries = cherries.rename(columns={
    "Chile->China (USD)": "imports_usd",
    "Chile->World (USD)": "chile_world",
    "China<-World (USD)": "china_world",
})
macro = pd.read_csv(f"{OUT}/macro_summary.csv")
china = macro[macro["country"] == "China"][["year", "GDP_per_capita_USD"]].rename(
    columns={"GDP_per_capita_USD": "china_gdp_pc"})

df = cherries.merge(china, on="year")
# Keep only years where bilateral trade is non-trivial (>$1M) and not in the 2013 reporting gap
df = df[df["imports_usd"] > 1e6].dropna(subset=["imports_usd", "china_gdp_pc"]).copy()
df["log_imports"] = np.log(df["imports_usd"])
df["log_gdp_pc"] = np.log(df["china_gdp_pc"])

print("Sample used (year, imports USD, China GDP/capita USD):")
print(df[["year", "imports_usd", "china_gdp_pc"]].to_string(index=False))
print(f"\nN = {len(df)} observations\n")

# --- fit OLS ---
X = sm.add_constant(df["log_gdp_pc"])
y = df["log_imports"]
model = sm.OLS(y, X).fit()
print(model.summary())

beta = model.params["log_gdp_pc"]
se = model.bse["log_gdp_pc"]
pval = model.pvalues["log_gdp_pc"]
r2 = model.rsquared
ci = model.conf_int().loc["log_gdp_pc"].tolist()

print("\n=== HEADLINE RESULT ===")
print(f"Income elasticity (beta) = {beta:.3f}")
print(f"Standard error          = {se:.3f}")
print(f"95% CI                  = [{ci[0]:.3f}, {ci[1]:.3f}]")
print(f"p-value                 = {pval:.2e}")
print(f"R-squared               = {r2:.3f}")
print(f"Interpretation: a 1% rise in China's GDP per capita is associated with a")
print(f"                {beta:.2f}% rise in Chinese imports of Chilean cherries.")
print(f"Since beta >> 1, cherries behave as a strongly income-elastic luxury good.")

# --- plot the regression ---
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["log_gdp_pc"], df["log_imports"], s=70, color="#a4243b", edgecolor="white", zorder=3)
xs = np.linspace(df["log_gdp_pc"].min(), df["log_gdp_pc"].max(), 100)
Xs = sm.add_constant(xs)
ys = model.predict(Xs)
ax.plot(xs, ys, color="#264653", linewidth=2, label=f"OLS fit: y = {model.params['const']:.2f} + {beta:.2f}·x")
# label the points with years
for _, r in df.iterrows():
    ax.annotate(int(r["year"]), (r["log_gdp_pc"], r["log_imports"]),
                xytext=(6, -2), textcoords="offset points", fontsize=8, color="#444")
ax.set_xlabel("log(China GDP per capita, USD)")
ax.set_ylabel("log(Cherry imports from Chile, USD)")
ax.set_title(f"Income elasticity of Chinese cherry demand:  β = {beta:.2f}  (R² = {r2:.2f})",
             fontsize=12, fontweight="bold")
ax.legend(loc="upper left", frameon=False)
ax.grid(alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/chart4_ols_elasticity.png", dpi=180)
plt.close()
print("\nSaved chart4_ols_elasticity.png")
