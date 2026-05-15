"""
Mirror data: China as reporter, importing cherries from Chile and from the World.
Used to cross-check the Chile-side numbers.
"""
import time
import pandas as pd
import requests

OUT = "/Users/tanviparsam/Downloads/University/Semester4/Macroeconomics-Term_Paper"
URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"

CHINA = 156
CHILE = 152
WORLD = 0

def fetch(reporter, partner, cmd, years, flow="M"):
    rows = []
    for y in years:
        params = {"reporterCode": reporter, "period": y, "partnerCode": partner,
                  "cmdCode": cmd, "flowCode": flow}
        try:
            j = requests.get(URL, params=params, timeout=30).json()
            for d in j.get("data") or []:
                rows.append({
                    "year": d["refYear"], "reporter": d["reporterCode"],
                    "partner": d["partnerCode"], "cmd": d["cmdCode"],
                    "value_usd": d.get("primaryValue") or d.get("cifvalue"),
                    "net_wgt_kg": d.get("netWgt"),
                })
        except Exception as e:
            print(f"  ! {y} {cmd}: {e}")
        time.sleep(0.25)
    return pd.DataFrame(rows)


years_new = list(range(2012, 2025))
years_old = list(range(2005, 2012))

dfs = []
print("China imports of cherries from Chile (HS 080929)")
dfs.append(fetch(CHINA, CHILE, "080929", years_new))
print("China imports of cherries from Chile (HS 080921 sour)")
dfs.append(fetch(CHINA, CHILE, "080921", years_new))
print("China imports of cherries from Chile (pre-2012 080920)")
dfs.append(fetch(CHINA, CHILE, "080920", years_old))
print("China imports of cherries from World (080929)")
dfs.append(fetch(CHINA, WORLD, "080929", years_new))
print("China imports of cherries from World (080921)")
dfs.append(fetch(CHINA, WORLD, "080921", years_new))
print("China imports of cherries from World (pre-2012 080920)")
dfs.append(fetch(CHINA, WORLD, "080920", years_old))

df = pd.concat(dfs, ignore_index=True)
df["partner_name"] = df["partner"].map({CHILE: "Chile", WORLD: "World"})
df.to_csv(f"{OUT}/cherries_mirror_raw.csv", index=False)
print(f"\nSaved cherries_mirror_raw.csv ({len(df)} rows)")

agg = (df.groupby(["year", "partner_name"], as_index=False)
         .agg(value_usd=("value_usd", "sum"), kg=("net_wgt_kg", "sum")))
piv = agg.pivot(index="year", columns="partner_name", values="value_usd").reset_index()
piv.columns.name = None
piv = piv.rename(columns={"Chile": "imports_from_chile_usd", "World": "imports_from_world_usd"})
piv["chile_share_pct"] = 100 * piv["imports_from_chile_usd"] / piv["imports_from_world_usd"]
piv.to_csv(f"{OUT}/cherries_mirror_summary.csv", index=False)
print(piv.to_string(index=False))
