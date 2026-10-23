import requests
import re

headers = {'User-Agent': 'Mozilla/5.0'}
for prod in ['hydrorivers', 'hydrobasins', 'hydrolakes']:
    r = requests.get(f'https://www.hydrosheds.org/products/{prod}', headers=headers)
    print(f"\n=== {prod} (Status {r.status_code}) ===")
    matches = set(re.findall(r'https?://[a-zA-Z0-9_\-\./]+\.zip', r.text))
    for m in sorted(matches):
        if any(k in m.lower() for k in ['na', 'ca', 'global', 'glo']):
            print(" ", m)
