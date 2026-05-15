"""
Pulls trade and macro data for the term paper:
- Chilean cherry exports to China (UN Comtrade, HS 080929 + 080921)
- Chilean cherry exports to the world
- Chile macro data (World Bank WDI)
- China macro data (World Bank WDI)
Saves everything as CSVs alongside this script.
"""

import time
import pandas as pd
import requests

OUT_DIR = "/Users/tanviparsam/Downloads/University/Semester4/Macroeconomics-Term_Paper"

COMTRADE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
WB = "https://api.worldbank.org/v2"

CHILE = 152
CHINA = 156
WORLD = 0
SWEET = "080929"
SOUR = "080921"
OLD = "080920"  # pre-HS2012, fresh cherries combined


def fetch_comtrade(reporter, partner, cmd, years):
    rows = []
    for y in years:
        params = {
            "reporterCode": reporter,
            "period": y,
            "partnerCode": partner,
            "cmdCode": cmd,
            "flowCode": "X",
        }
        try:
            r = requests.get(COMTRADE, params=params, timeout=30)
            j = r.json()
            for d in j.get("data") or []:
                rows.append({
                    "year": d["refYear"],
                    "reporter": d["reporterCode"],
                    "partner": d["partnerCode"],
                    "cmd": d["cmdCode"],
                    "value_usd": d.get("primaryValue") or d.get("fobvalue"),
                    "net_wgt_kg": d.get("netWgt"),
                })
        except Exception as e:
            print(f"  ! {y} {cmd}: {e}")
        time.sleep(0.3)
    return pd.DataFrame(rows)


def fetch_wb(country, indicator):
    url = f"{WB}/country/{country}/indicator/{indicator}"
    params = {"format": "json", "per_page": 200}
    r = requests.get(url, params=params, timeout=30)
    j = r.json()
    if not isinstance(j, list) or len(j) < 2 or j[1] is None:
        return pd.DataFrame()
    return pd.DataFrame([
        {"year": int(d["date"]), "value": d["value"], "country": country, "indicator": indicator}
        for d in j[1] if d.get("value") is not None
    ]).sort_values("year").reset_index(drop=True)


def main():
    years = list(range(2005, 2025))

    print("Chile -> China cherries (HS 080929, sweet)")
    sweet_cn = fetch_comtrade(CHILE, CHINA, SWEET, years)
    print(f"  {len(sweet_cn)} rows")

    print("Chile -> China cherries (HS 080921, sour)")
    sour_cn = fetch_comtrade(CHILE, CHINA, SOUR, years)
    print(f"  {len(sour_cn)} rows")

    print("Chile -> China cherries (pre-2012 code 080920)")
    old_cn = fetch_comtrade(CHILE, CHINA, OLD, years[:8])
    print(f"  {len(old_cn)} rows")

    print("Chile -> World cherries (HS 080929)")
    sweet_world = fetch_comtrade(CHILE, WORLD, SWEET, years)
    print(f"  {len(sweet_world)} rows")

    print("Chile -> World cherries (HS 080921)")
    sour_world = fetch_comtrade(CHILE, WORLD, SOUR, years)
    print(f"  {len(sour_world)} rows")

    print("Chile -> World cherries (pre-2012 code 080920)")
    old_world = fetch_comtrade(CHILE, WORLD, OLD, years[:8])
    print(f"  {len(old_world)} rows")

    cherries = pd.concat([sweet_cn, sour_cn, old_cn, sweet_world, sour_world, old_world], ignore_index=True)
    cherries["partner_name"] = cherries["partner"].map({CHINA: "China", WORLD: "World"})
    cherries.to_csv(f"{OUT_DIR}/cherries_raw.csv", index=False)
    print(f"Saved cherries_raw.csv ({len(cherries)} rows)")

    pivot = (cherries.groupby(["year", "partner_name"], as_index=False)
                     .agg(value_usd=("value_usd", "sum"), kg=("net_wgt_kg", "sum")))
    pivot_v = pivot.pivot(index="year", columns="partner_name", values="value_usd").reset_index()
    pivot_v.columns.name = None
    pivot_v = pivot_v.rename(columns={"China": "value_to_china_usd", "World": "value_to_world_usd"})
    pivot_v["china_share_pct"] = 100 * pivot_v["value_to_china_usd"] / pivot_v["value_to_world_usd"]
    pivot_v.to_csv(f"{OUT_DIR}/cherries_summary.csv", index=False)
    print(f"Saved cherries_summary.csv")
    print(pivot_v.to_string(index=False))

    print("\nWorld Bank macro data")
    indicators = {
        "NY.GDP.MKTP.CD": "GDP_USD",
        "NY.GDP.PCAP.CD": "GDP_per_capita_USD",
        "NE.EXP.GNFS.ZS": "Exports_pct_GDP",
        "NE.IMP.GNFS.ZS": "Imports_pct_GDP",
        "NY.GDP.MKTP.KD.ZG": "GDP_growth_pct",
    }
    macro_rows = []
    for code, label in indicators.items():
        for c, name in [("CHL", "Chile"), ("CHN", "China")]:
            df = fetch_wb(c, code)
            if df.empty:
                print(f"  ! empty {c} {code}")
                continue
            for _, row in df.iterrows():
                macro_rows.append({"country": name, "indicator": label, "year": row["year"], "value": row["value"]})

    macro = pd.DataFrame(macro_rows)
    macro.to_csv(f"{OUT_DIR}/macro_raw.csv", index=False)
    print(f"Saved macro_raw.csv ({len(macro)} rows)")

    wide = macro.pivot_table(index=["country", "year"], columns="indicator", values="value").reset_index()
    wide.to_csv(f"{OUT_DIR}/macro_summary.csv", index=False)
    print(f"Saved macro_summary.csv")
    print(wide.tail(20).to_string(index=False))


if __name__ == "__main__":
    main()
