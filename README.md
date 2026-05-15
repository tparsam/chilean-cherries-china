# Chilean Cherries → China: A Trade Analysis

Supplementary data, code, and visualisations for a macroeconomics term paper on the bilateral trade in fresh cherries between Chile and China, 2005–2024.

The paper itself is a separate document. This repository contains the underlying data work and analytical methods referenced in it.

## Headline findings

- Bilateral cherry trade grew from **~$80,000 in 2005 to ~$3.2–3.6 billion in 2024** — roughly a **40,000× increase**.
- By 2024, **~91% of Chile's cherry exports** went to China, and **~88–97% of China's cherry imports** came from Chile.
- Estimated **income elasticity of demand = 4.20** (OLS, R² = 0.98, p < 10⁻¹²): cherries behave as a strongly luxury good in China.
- A singular value decomposition of Chile's cherry-export matrix (46 countries × 15 years) shows that **a single component explains 99.85% of all variance**, and that component is essentially aligned with China.
- An average of **~92% of annual cherry trade lands in the December–February window**, with **January alone capturing more than half** of an entire year's flow.
- A counterfactual comparison with Chile's cherry exports to the United States shows a **+18 percentage-point excess in January** and **−20 pp deficit in December** for the China market — a clean isolation of the Lunar New Year cultural effect.

## Repository layout

```
chilean-cherries-china/
├── README.md             (this file)
├── requirements.txt
├── scripts/              reproducible Python scripts
├── data/                 raw and processed CSVs
├── charts/               PNG figures
└── notes/                analytical notes + reference list
```

### `scripts/` — reproducible Python

| File | What it does |
|---|---|
| [`pull_data.py`](scripts/pull_data.py) | Pulls Chile-as-reporter cherry exports (HS 080920 / 080921 / 080929) to China and to the world, 2005–2024, plus World Bank macro indicators for Chile and China |
| [`pull_mirror.py`](scripts/pull_mirror.py) | Pulls China-as-reporter cherry imports from Chile and from the world (mirror statistics for cross-check) |
| [`pull_monthly.py`](scripts/pull_monthly.py) | Pulls monthly China-from-Chile cherry imports, 2018–2025, and builds the seasonality charts |
| [`build_charts.py`](scripts/build_charts.py) | Combines the Chile-side and China-side data, fills gaps, computes share ratios, builds the first three charts |
| [`ols_elasticity.py`](scripts/ols_elasticity.py) | OLS regression of (log) cherry imports on (log) China per capita GDP → income elasticity |
| [`svd_analysis.py`](scripts/svd_analysis.py) | Pulls Chile→all countries cherry exports, builds the country×year matrix, runs SVD, produces the variance / loading visualisations |
| [`lny_event_study.py`](scripts/lny_event_study.py) | Event study aligning every year to its Lunar New Year date; Herfindahl concentration measures; counterfactual comparison to Chile→USA cherry exports |

### `data/` — CSVs

| File | Description |
|---|---|
| [`cherries_raw.csv`](data/cherries_raw.csv) | Chile-reported exports, all HS codes, China + World |
| [`cherries_mirror_raw.csv`](data/cherries_mirror_raw.csv) | China-reported imports, all HS codes, Chile + World |
| [`cherries_FINAL.csv`](data/cherries_FINAL.csv) | Combined annual series — best estimate per year |
| [`cherries_combined.csv`](data/cherries_combined.csv) | Intermediate combined table with both sides shown |
| [`cherries_summary.csv`](data/cherries_summary.csv) | First-pass summary (superseded by FINAL) |
| [`cherries_mirror_summary.csv`](data/cherries_mirror_summary.csv) | First-pass mirror summary |
| [`cherries_all_destinations.csv`](data/cherries_all_destinations.csv) | Chile's cherry exports to every reported destination, 2010–2024 |
| [`cherries_matrix.csv`](data/cherries_matrix.csv) | The 46×15 country × year matrix decomposed via SVD |
| [`cherries_monthly.csv`](data/cherries_monthly.csv) | Monthly China-from-Chile cherry imports, 2018–2025 |
| [`cherries_chile_to_usa_monthly.csv`](data/cherries_chile_to_usa_monthly.csv) | Monthly Chile→USA cherry exports, 2020–2024 (counterfactual) |
| [`macro_raw.csv`](data/macro_raw.csv) | World Bank WDI series, long format |
| [`macro_summary.csv`](data/macro_summary.csv) | Same data, wide format |

### `charts/` — PNG figures (180 DPI)

| File | What it shows |
|---|---|
| [`chart1_bilateral_value.png`](charts/chart1_bilateral_value.png) | Bar chart: value of Chile's cherry exports to China, 2005–2024 |
| [`chart2_shares.png`](charts/chart2_shares.png) | Twin lines: China's share of Chile's cherry exports; Chile's share of China's cherry imports |
| [`chart3_vs_gdp.png`](charts/chart3_vs_gdp.png) | Dual-axis: Chinese GDP per capita vs cherry imports from Chile |
| [`chart4_ols_elasticity.png`](charts/chart4_ols_elasticity.png) | Log-log scatter + OLS fit (β = 4.20, R² = 0.98) |
| [`chart5_svd.png`](charts/chart5_svd.png) | 4-panel SVD figure: scree, country loadings, year pattern, orthogonal axis |
| [`chart6_monthly_seasonality.png`](charts/chart6_monthly_seasonality.png) | Monthly bars 2018–2025 with Lunar New Year dates marked |
| [`chart7_monthly_overlay.png`](charts/chart7_monthly_overlay.png) | All years overlaid by month — the universal LNY shape |
| [`chart8_lny_evidence.png`](charts/chart8_lny_evidence.png) | 4-panel LNY evidence: event study, concentration, counterfactual, China-USA gap |

### `notes/` — Markdown analytical notes

| File | Description |
|---|---|
| [`DATA_NOTES.md`](notes/DATA_NOTES.md) | Data sources, headline numbers, limitations, suggested narrative |
| [`REFERENCES.md`](notes/REFERENCES.md) | Curated reference list for Level 2 analysis, organised by theme |
| [`CULTURAL_CAVEAT.md`](notes/CULTURAL_CAVEAT.md) | The cultural-engineering / Lunar New Year argument, including a draft paragraph for the paper |
| [`SVD_RESULTS.md`](notes/SVD_RESULTS.md) | Full numerical output of the SVD analysis |

## Methods used

- **Descriptive statistics**: time series of bilateral and multilateral trade values
- **Mirror statistics**: cross-validation of reported trade flows using the reciprocal reporter
- **HS-code reconciliation**: combining `080920` (pre-2012), `080921` (sour), and `080929` (sweet) across the 2012 classification revision
- **Ordinary Least Squares regression**: log-log specification estimating income elasticity of demand
- **Singular Value Decomposition** (`numpy.linalg.svd`): decomposing the 46×15 country × year trade matrix
- **Event study** aligning monthly trade to each year's Lunar New Year date
- **Herfindahl–Hirschman concentration index** across monthly shares, with effective-number-of-months interpretation
- **Counterfactual comparison**: same product (Chilean cherries), different destination (USA vs China), to isolate destination-specific cultural-calendar effects

## Data sources

1. **UN Comtrade** — bilateral trade in goods by HS code, annual and monthly. Browse the user-facing platform at [comtradeplus.un.org](https://comtradeplus.un.org/); the scripts hit the public preview API at `https://comtradeapi.un.org/public/v1/preview/` (no API key required for the preview endpoint).
2. **World Bank World Development Indicators (WDI)** — macroeconomic indicators for Chile and China. Browse at [data.worldbank.org/products/wdi](https://data.worldbank.org/products/wdi); the scripts hit the indicators API at `https://api.worldbank.org/v2/` ([API docs](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)).

## How to reproduce

Tested with Python 3.11. Required packages: `pandas`, `numpy`, `requests`, `matplotlib`, `statsmodels`, `scipy`, `openpyxl`.

From the repo root, run scripts in this order:

```bash
pip install -r requirements.txt

python3 scripts/pull_data.py          # base trade + macro data
python3 scripts/pull_mirror.py        # mirror trade data
python3 scripts/build_charts.py       # combined table + charts 1–3
python3 scripts/ols_elasticity.py     # OLS regression + chart 4
python3 scripts/svd_analysis.py       # SVD analysis + chart 5
python3 scripts/pull_monthly.py       # monthly data + charts 6–7
python3 scripts/lny_event_study.py    # LNY event study + chart 8
```

Each script writes CSVs to `data/`, charts to `charts/`, and any generated notes to `notes/`. Total runtime: ~5 minutes, dominated by API calls.

## Limitations

- **HS code transition (2012)** produces gaps in 2012–13 where Chile and partner countries used different codes.
- **2024 Chile→World reporting** is incomplete in UN Comtrade at time of pull; China-side data is more reliable for that year.
- **FOB vs CIF**: Chile reports exports FOB, China reports imports CIF (which includes freight and insurance, typically ~10–15% higher); this causes some mirror-statistic gaps that can occasionally exceed 100%.
- **Re-exports via Hong Kong** are not separately broken out here; figures show direct mainland China flows.
- **OLS is descriptive, not causal**: the high R² and large β reflect strong association between Chinese income growth and cherry imports, but multiple FTAs, supply-side investment, and marketing campaigns happened over the same period. A causal estimate would require an identification strategy beyond the scope of this work.
- **USA as a counterfactual** is imperfect — December is partly Christmas-anchored, so the +18/−20 pp gap is best characterised as a "Lunar New Year vs Christmas calendar gap" rather than a pure LNY effect.

## Licence

Data is from UN Comtrade and the World Bank, both public-domain / open. Scripts and analysis in this repository are released under the MIT licence.
