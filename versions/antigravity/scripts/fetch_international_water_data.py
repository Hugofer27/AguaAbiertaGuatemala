import sys
import os
import requests
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

out_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/international"
os.makedirs(out_dir, exist_ok=True)

# 1. WHO/UNICEF JMP data for Guatemala
# JMP provides country data downloads at: https://washdata.org/data/downloads
# Let's test downloading Guatemala JMP country file or API
print("1. Testing WHO/UNICEF JMP...")
jmp_urls = [
    ("JMP_Guatemala_WASH.xlsx", "https://washdata.org/sites/default/files/2023-07/jmp-2023-wat-san-hyg-guatemala.xlsx"),
    ("JMP_Country_Estimates_2023.xlsx", "https://washdata.org/sites/default/files/2023-07/jmp-2023-country-estimates.xlsx"),
    ("JMP_Inequalities_2023.xlsx", "https://washdata.org/sites/default/files/2023-07/jmp-2023-inequalities.xlsx")
]

for filename, url in jmp_urls:
    dest = os.path.join(out_dir, filename)
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        print(f"JMP {filename} -> Status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"  Saved {dest} ({len(r.content)} bytes)")
    except Exception as e:
        print(f"  Error {url}: {e}")

# 2. GRDC (Global Runoff Data Centre) Station Catalogue
print("\n2. Fetching GRDC Station Catalogue...")
grdc_urls = [
    ("GRDC_Stations.csv", "https://portal.grdc.bafg.de/stations/export?format=csv"),
    ("GRDC_Catalogue.xlsx", "https://www.bafg.de/GRDC/EN/02_srvcs/21_tmsrs/211_cntrbs/Catalogue.xlsx?__blob=publicationFile")
]
for filename, url in grdc_urls:
    dest = os.path.join(out_dir, filename)
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=25)
        print(f"GRDC {filename} -> Status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"  Saved {dest} ({len(r.content)} bytes)")
    except Exception as e:
        print(f"  Error {url}: {e}")

# 3. World Bank Indicators for Guatemala (Water, Renewable freshwater, wastewater treatment)
print("\n3. Fetching World Bank Water Data for Guatemala...")
wb_indicators = {
    "ER.H2O.FWTL.K3": "Annual freshwater withdrawals, total (billion cubic meters)",
    "ER.H2O.FWTL.ZS": "Annual freshwater withdrawals, total (% of internal resources)",
    "ER.H2O.INTR.K3": "Renewable internal freshwater resources, total (billion cubic meters)",
    "ER.H2O.INTR.PC": "Renewable internal freshwater resources per capita (cubic meters)",
    "SH.H2O.BASW.ZS": "People using at least basic drinking water services (% of population)",
    "SH.H2O.SMDW.ZS": "People using safely managed drinking water services (% of population)",
    "SH.STA.BASS.ZS": "People using at least basic sanitation services (% of population)",
    "SH.STA.SMSS.ZS": "People using safely managed sanitation services (% of population)",
    "AG.LND.IRIG.AG.ZS": "Agricultural irrigated land (% of total agricultural land)"
}

wb_results = []
for ind, name in wb_indicators.items():
    url = f"https://api.worldbank.org/v2/country/GTM/indicator/{ind}?format=json&per_page=100"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1 and data[1]:
                records = data[1]
                for rec in records:
                    if rec.get('value') is not None:
                        wb_results.append({
                            'country': 'Guatemala',
                            'indicator_id': ind,
                            'indicator_name': name,
                            'year': rec.get('date'),
                            'value': rec.get('value')
                        })
                print(f"  WB {ind} -> OK ({len([r for r in records if r.get('value') is not None])} years)")
    except Exception as e:
        print(f"  Error WB {ind}: {e}")

if wb_results:
    dest = os.path.join(out_dir, "WorldBank_Guatemala_Water_Indicators.json")
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(wb_results, f, indent=2)
    print(f"Saved {len(wb_results)} records to {dest}")

print("\nInternational fetch complete.")
