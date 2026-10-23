import sys
import os
import requests
import re
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

gov_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"
os.makedirs(gov_dir, exist_ok=True)

targets = [
    ("INSIVUMEH_Portal", "https://insivumeh.gob.gt/"),
    ("INSIVUMEH_Hidrologia", "https://insivumeh.gob.gt/hidrologia/"),
    ("MARN_Portal", "https://marn.gob.gt/"),
    ("AMSA_Portal", "https://amsa.gob.gt/"),
    ("AMSCLAE_Portal", "https://amsclae.gob.gt/"),
    ("FUNCAGUA_Portal", "https://funcagua.org.gt/"),
    ("SEGEPLAN_IDEG", "http://ideg.segeplan.gob.gt/geoserver/wfs?request=GetCapabilities"),
    ("DATOS_GOB_GT", "https://datos.gob.gt/api/3/action/package_search?q=agua")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

results = {}
for name, url in targets:
    print(f"\nProbing {name}: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"  Status: {r.status_code}, Length: {len(r.content)}")
        results[name] = {
            'url': url,
            'status_code': r.status_code,
            'content_length': len(r.content),
            'content_type': r.headers.get('Content-Type')
        }
        # If html, extract pdf and excel links
        if 'html' in r.headers.get('Content-Type', '').lower():
            text = r.text
            hrefs = re.findall(r'href=[\'"]([^\'"]+)[\'"]', text, re.IGNORECASE)
            doc_links = []
            for href in hrefs:
                if any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.xls', '.csv', '.zip', '.geojson', '.kml', '.shp']):
                    doc_links.append(href)
            # deduplicate
            doc_links = list(dict.fromkeys(doc_links))
            results[name]['doc_links'] = doc_links
            print(f"  Found {len(doc_links)} downloadable document links.")
            for dl in doc_links[:5]:
                print(f"    - {dl}")
        elif 'json' in r.headers.get('Content-Type', '').lower():
            try:
                js = r.json()
                results[name]['json_keys'] = list(js.keys()) if isinstance(js, dict) else len(js)
                if 'result' in js and 'results' in js['result']:
                    print(f"  CKAN Package count: {js['result'].get('count')}")
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")
        results[name] = {'url': url, 'error': str(e)}

with open('D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government/probe_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nProbe results saved.")
