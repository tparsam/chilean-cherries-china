# Data Notes — Chilean Cherries to China

## Files produced

| File | Contents |
|---|---|
| `cherries_raw.csv` | Chile-as-reporter, all cherry HS codes (080920 pre-2012, 080929 sweet, 080921 sour), partners China and World |
| `cherries_mirror_raw.csv` | China-as-reporter, importing cherries from Chile and from World (mirror data for cross-check) |
| `cherries_FINAL.csv` | Combined annual series — best estimate per year for: bilateral Chile→China, Chile→World, China←World, plus both bilateral share metrics |
| `macro_summary.csv` | Chile + China macro data (GDP, GDP/capita, exports % of GDP, imports % of GDP, GDP growth), 2005–2024, from World Bank WDI |
| `chart1_bilateral_value.png` | Bar chart: value of Chile's cherry exports to China, 2005–2024 |
| `chart2_shares.png` | Twin-line chart: China's share of Chile's cherry exports vs Chile's share of China's cherry imports |
| `chart3_vs_gdp.png` | Dual-axis: Chinese GDP per capita (line) vs cherry imports from Chile (bars) |

## Headline numbers

- 2005: Chile exported **~$80,000** of cherries to China.
- 2014: ~**$443 million** (first big year).
- 2018: ~**$1.0 billion**.
- 2022: ~**$2.0 billion**.
- **2024: ~$3.2–3.6 billion** (depending on which side of the trade you count).
- By 2024, **~91% of Chile's cherry exports go to China**, and **~88–97% of China's cherry imports come from Chile**.
- China's GDP per capita rose from ~$1,780 (2005) → ~$13,300 (2024). Cherry imports tracked this rise almost perfectly.

## Data sources

1. **UN Comtrade Public API** (`comtradeapi.un.org/public/v1/preview`)
   - Publisher: UN Statistics Division
   - Frequency: annual (monthly also available with paid subscription)
   - Coverage: most trading economies, but reporting lag and gaps are common
2. **World Bank World Development Indicators (WDI)**
   - Publisher: World Bank
   - Frequency: annual, updated quarterly
   - Indicators used: `NY.GDP.MKTP.CD`, `NY.GDP.PCAP.CD`, `NE.EXP.GNFS.ZS`, `NE.IMP.GNFS.ZS`, `NY.GDP.MKTP.KD.ZG`

## Data limitations (important — assignment asks you to note these)

1. **HS code transition (2012):** Pre-2012, all fresh cherries were under code `080920`. From 2012 onwards, the code split into `080921` (sour cherries) and `080929` (other / sweet — the relevant one). The transition produces ugly gaps in 2012–2013 where reporters used different codes. The combined series sums all three to mitigate this.
2. **2013 gap:** Chile-as-reporter has almost no Chile→China data for 2013, and China-as-reporter is also missing that year. This is a genuine data hole, not a real collapse in trade. **Recommendation: note this in the paper, do not interpret 2013 as a drop.**
3. **2024 Chile→World reporting:** Chile had not yet fully reported its global cherry exports to Comtrade at time of pull. China's import side ($3.69B from world) is the more reliable 2024 figure.
4. **FOB vs CIF valuation:** Chile reports exports FOB (free on board), China reports imports CIF (cost, insurance, freight). CIF is typically ~10–15% higher because it includes shipping. This is why mirror values sometimes diverge (and why one share calculation occasionally exceeds 100% in 2019).
5. **Re-exports via Hong Kong:** Some cherries enter China via Hong Kong; these may be attributed to "Hong Kong, China" rather than "China" in some years. The numbers here are mainland-China direct.

## Suggested narrative for the paper

> The bilateral trade in fresh cherries between Chile and China grew from less than $0.1 million in 2005 to over $3 billion by 2024 — a roughly 40,000-fold increase in two decades. The relationship is unusually one-sided: today around 90% of Chile's cherry exports flow to a single market, and conversely the vast majority of cherries China imports come from a single supplier. This unique bilateral lock-in raises classic macroeconomic questions about export concentration risk, the role of free trade agreements (the China–Chile FTA took effect in 2006), and how rising consumer incomes in one country can reshape an entire agricultural sector on the other side of the world.
